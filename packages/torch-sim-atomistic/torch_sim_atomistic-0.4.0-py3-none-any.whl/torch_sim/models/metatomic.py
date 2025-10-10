"""Wrapper for metatomic-based models in TorchSim.

This module provides a TorchSim wrapper of metatomic models for computing
energies, forces, and stresses for atomistic systems, including batched computations
for multiple systems simultaneously.

The MetatomicModel class adapts metatomic models to the ModelInterface protocol,
allowing them to be used within the broader torch-sim simulation framework.

Notes:
    This module depends on the metatomic-torch package.
"""

import traceback
import warnings
from pathlib import Path
from typing import Any

import torch
import vesin.metatomic

import torch_sim as ts
from torch_sim.models.interface import ModelInterface
from torch_sim.typing import StateDict


try:
    from metatomic.torch import (
        ModelEvaluationOptions,
        ModelOutput,
        System,
        load_atomistic_model,
    )
    from metatrain.utils.io import load_model

except ImportError as exc:
    warnings.warn(f"Metatomic import failed: {traceback.format_exc()}", stacklevel=2)

    class MetatomicModel(ModelInterface):
        """Metatomic model wrapper for torch-sim.

        This class is a placeholder for the MetatomicModel class.
        It raises an ImportError if metatomic is not installed.
        """

        def __init__(self, err: ImportError = exc, *_args: Any, **_kwargs: Any) -> None:
            """Dummy init for type checking."""
            raise err


class MetatomicModel(ModelInterface):
    """Computes energies for a list of systems using a metatomic model.

    This class wraps a metatomic model to compute energies, forces, and stresses for
    atomic systems within the TorchSim framework. It supports batched calculations
    for multiple systems and handles the necessary transformations between
    TorchSim's data structures and metatomic's expected inputs.

    Attributes:
        ...
    """

    def __init__(
        self,
        model: str | Path | None = None,
        extensions_path: str | Path | None = None,
        device: torch.device | str | None = None,
        *,
        check_consistency: bool = False,
        compute_forces: bool = True,
        compute_stress: bool = True,
    ) -> None:
        """Initialize the metatomic model for energy, force and stress calculations.

        Sets up a metatomic model for energy, force, and stress calculations within
        the TorchSim framework. The model can be initialized with atomic numbers
        and system indices, or these can be provided during the forward pass.

        Args:
            model (str | Path | None): Path to the metatomic model file or a
                pre-defined model name. Currently only "pet-mad"
                (https://arxiv.org/abs/2503.14118) is supported as a pre-defined model.
                If None, defaults to "pet-mad".
            extensions_path (str | Path | None): Optional, path to the folder containing
                compiled extensions for the model.
            device (torch.device | None): Device on which to run the model. If None,
                defaults to "cuda" if available, otherwise "cpu".
            check_consistency (bool): Whether to perform various consistency checks
                during model evaluation. This should only be used in case of anomalous
                behavior, as it can hurt performance significantly.
            compute_forces (bool): Whether to compute forces.
            compute_stress (bool): Whether to compute stresses.

        Raises:
            TypeError: If model is neither a path nor "pet-mad".
        """
        super().__init__()

        if model is None:
            raise ValueError(
                "A model path, or the name of a pre-defined model, must be provided. "
                'Currently only "pet-mad" is available as a pre-defined model.'
            )

        if model == "pet-mad":
            path = "https://huggingface.co/lab-cosmo/pet-mad/resolve/v1.1.0/models/pet-mad-v1.1.0.ckpt"
            self._model = load_model(path).export()
        elif str(model).endswith(".ckpt"):
            path = model
            self._model = load_model(path).export()
        elif str(model).endswith(".pt"):
            path = model
            self._model = load_atomistic_model(path, extensions_path)
        else:
            raise ValueError('Model must be a path to a .ckpt/.pt file, or "pet-mad".')

        if "energy" not in self._model.capabilities().outputs:
            raise ValueError(
                "This model does not support energy predictions. "
                "The model must have an `energy` output to be used in TorchSim."
            )

        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if isinstance(self._device, str):
            self._device = torch.device(self._device)
        if self._device.type not in self._model.capabilities().supported_devices:
            raise ValueError(
                f"Model does not support device {self._device}. Supported devices: "
                f"{self._model.capabilities().supported_devices}. You might want to "
                f"set the `device` argument to a supported device."
            )

        self._dtype = getattr(torch, self._model.capabilities().dtype)
        self._model.to(self._device)
        self._compute_forces = compute_forces
        self._compute_stress = compute_stress
        self._memory_scales_with = "n_atoms_x_density"  # for the majority of models
        self._check_consistency = check_consistency
        self._requested_neighbor_lists = self._model.requested_neighbor_lists()
        self._evaluation_options = ModelEvaluationOptions(
            length_unit="angstrom",
            outputs={"energy": ModelOutput(quantity="energy", unit="eV", per_atom=False)},
        )

    def forward(self, state: ts.SimState | StateDict) -> dict[str, torch.Tensor]:  # noqa: C901, PLR0915
        """Compute energies, forces, and stresses for the given atomic systems.

        Processes the provided state information and computes energies, forces, and
        stresses using the underlying metatomic model. Handles batched calculations for
        multiple systems as well as constructing the necessary neighbor lists.

        Args:
            state (SimState | StateDict): State object containing positions, cell,
                and other system information. Can be either a SimState object or a
                dictionary with the relevant fields.

        Returns:
            dict[str, torch.Tensor]: Computed properties:
                - 'energy': System energies with shape [n_systems]
                - 'forces': Atomic forces with shape [n_atoms, 3] if compute_forces=True
                - 'stress': System stresses with shape [n_systems, 3, 3] if
                    compute_stress=True
        """
        sim_state = (
            state
            if isinstance(state, ts.SimState)
            else ts.SimState(**state, masses=torch.ones_like(state["positions"]))
        )

        # Input validation is already done inside the forward method of the
        # AtomisticModel class, so we don't need to do it again here.

        atomic_nums = sim_state.atomic_numbers
        cell = sim_state.row_vector_cell
        positions = sim_state.positions
        pbc = sim_state.pbc

        # Check dtype (metatomic models require a specific input dtype)
        if positions.dtype != self._dtype:
            raise TypeError(
                f"Positions dtype {positions.dtype} does not match model dtype "
                f"{self._dtype}"
            )

        # Compared to other models, metatomic models have two peculiarities:
        # - different structures are fed to the models separately as a list of System
        #   objects, and not as a single graph-like batch
        # - the model does not compute forces and stresses itself, but rather the
        #   caller code needs to call torch.autograd.grad or similar to compute them
        #   from the energy output

        # Process each system separately
        systems: list[System] = []
        strains = []
        for sys_idx in range(len(cell)):
            system_mask = sim_state.system_idx == sys_idx
            system_positions = positions[system_mask]
            system_cell = cell[sys_idx]
            system_pbc = torch.tensor(
                [pbc, pbc, pbc], device=self._device, dtype=torch.bool
            )
            system_atomic_numbers = atomic_nums[system_mask]

            # Create a System object for this system
            if self._compute_forces:
                system_positions.requires_grad_()
            if self._compute_stress:
                strain = torch.eye(
                    3, device=self._device, dtype=self._dtype, requires_grad=True
                )
                system_positions = system_positions @ strain
                system_cell = system_cell @ strain
                strains.append(strain)

            systems.append(
                System(
                    positions=system_positions,
                    types=system_atomic_numbers,
                    cell=system_cell,
                    pbc=system_pbc,
                )
            )

        # Calculate the required neighbor list(s) for all the systems

        # move data to CPU because vesin only supports CPU for now
        systems = [system.to(device="cpu") for system in systems]
        vesin.metatomic.compute_requested_neighbors(
            systems, system_length_unit="Angstrom", model=self._model
        )
        # move back to the proper device
        systems = [system.to(device=self.device) for system in systems]

        # Get model output
        model_outputs = self._model(
            systems=systems,
            options=self._evaluation_options,
            check_consistency=self._check_consistency,
        )

        results: dict[str, torch.Tensor] = {}
        results["energy"] = model_outputs["energy"].block().values.detach().squeeze(-1)

        # Compute forces and/or stresses if requested
        tensors_for_autograd = []
        if self._compute_forces:
            for system in systems:
                tensors_for_autograd.append(system.positions)  # noqa: PERF401
        if self._compute_stress:
            for strain in strains:
                tensors_for_autograd.append(strain)  # noqa: PERF402

        if self._compute_forces or self._compute_stress:
            derivatives = torch.autograd.grad(
                outputs=model_outputs["energy"].block().values,
                inputs=tensors_for_autograd,
                grad_outputs=torch.ones_like(model_outputs["energy"].block().values),
            )
        else:
            derivatives = []

        results_by_system: dict[str, list[torch.Tensor]] = {}
        if self._compute_forces and self._compute_stress:
            results_by_system["forces"] = [-d for d in derivatives[: len(systems)]]
            results_by_system["stress"] = [
                d / torch.abs(torch.det(system.cell.detach()))
                for d, system in zip(derivatives[len(systems) :], systems, strict=False)
            ]
        elif self._compute_forces:
            results_by_system["forces"] = [-d for d in derivatives]
        elif self._compute_stress:
            results_by_system["stress"] = [
                d / torch.abs(torch.det(system.cell.detach()))
                for d, system in zip(derivatives, systems, strict=False)
            ]
        else:
            pass

        # Concatenate/stack forces and stresses
        if self._compute_forces:
            if len(results_by_system["forces"]) > 0:
                results["forces"] = torch.cat(results_by_system["forces"])
            else:
                results["forces"] = torch.empty_like(positions)
        if self._compute_stress:
            if len(results_by_system["stress"]) > 0:
                results["stress"] = torch.stack(results_by_system["stress"])
            else:
                results["stress"] = torch.empty_like(cell)

        return results
