"""An interface for using arbitrary GraphPESModels in ts.

This module provides a TorchSim wrapper of the GraphPES models for computing
energies, forces, and stresses of atomistic systems. It serves as a wrapper around
the graph_pes library, integrating it with the torch-sim framework to enable seamless
simulation of atomistic systems with machine learning potentials.

The GraphPESWrapper class adapts GraphPESModels to the ModelInterface protocol,
allowing them to be used within the broader torch-sim simulation framework.

Notes:
    This implementation requires graph_pes to be installed and accessible.
    It supports various model configurations through model instances or model paths.
"""

import traceback
import warnings
from pathlib import Path
from typing import Any

import torch

import torch_sim as ts
from torch_sim.models.interface import ModelInterface
from torch_sim.neighbors import vesin_nl_ts
from torch_sim.typing import StateDict


try:
    from graph_pes import AtomicGraph, GraphPESModel
    from graph_pes.atomic_graph import PropertyKey, to_batch
    from graph_pes.models import load_model

except ImportError as exc:
    warnings.warn(f"GraphPES import failed: {traceback.format_exc()}", stacklevel=2)
    PropertyKey = str

    class GraphPESWrapper(ModelInterface):  # type: ignore[reportRedeclaration]
        """GraphPESModel wrapper for torch-sim.

        This class is a placeholder for the GraphPESWrapper class.
        It raises an ImportError if graph_pes is not installed.
        """

        def __init__(self, err: ImportError = exc, *_args: Any, **_kwargs: Any) -> None:
            """Dummy init for type checking."""
            raise err

    class AtomicGraph:  # type: ignore[reportRedeclaration]  # noqa: D101
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D107,ARG002
            raise ImportError("graph_pes must be installed to use this model.")

    class GraphPESModel(torch.nn.Module):  # type: ignore[reportRedeclaration]  # noqa: D101
        pass


def state_to_atomic_graph(state: ts.SimState, cutoff: torch.Tensor) -> AtomicGraph:
    """Convert a SimState object into an AtomicGraph object.

    Args:
        state: SimState object containing atomic positions, cell, and atomic numbers
        cutoff: Cutoff radius for the neighbor list

    Returns:
        AtomicGraph object representing the batched structures
    """
    graphs = []

    for sys_idx in range(state.n_systems):
        system_mask = state.system_idx == sys_idx
        R = state.positions[system_mask]
        Z = state.atomic_numbers[system_mask]
        cell = state.row_vector_cell[sys_idx]
        # graph-pes models internally trim the neighbor list to the
        # model's cutoff value. To ensure no strange edge effects whereby
        # edges that are exactly `cutoff` long are included/excluded,
        # we bump cutoff + 1e-5 up slightly
        nl, shifts = vesin_nl_ts(R, cell, state.pbc, cutoff + 1e-5)

        atomic_graph = AtomicGraph(
            Z=Z.long(),
            R=R,
            cell=cell,
            neighbour_list=nl.long(),
            neighbour_cell_offsets=shifts,
            properties={},
            cutoff=cutoff.item(),
            other={},
        )
        graphs.append(atomic_graph)

    return to_batch(graphs)


class GraphPESWrapper(ModelInterface):
    """Wrapper for GraphPESModel in TorchSim.

    This class provides a TorchSim wrapper around GraphPESModel instances,
    allowing them to be used within the broader torch-sim simulation framework.

    The graph-pes package allows for the training of existing model architectures,
    including SchNet, PaiNN, MACE, NequIP, TensorNet, EDDP and more.
    You can use any of these, as well as your own custom architectures, with this wrapper.
    See the the graph-pes repo for more details: https://github.com/jla-gardner/graph-pes

    Args:
        model: GraphPESModel instance, or a path to a model file
        device: Device to run the model on
        dtype: Data type for the model
        compute_forces: Whether to compute forces
        compute_stress: Whether to compute stress

    Example:
        >>> from torch_sim.models.graphpes import GraphPESWrapper
        >>> from graph_pes.models import load_model
        >>> model = load_model("path/to/model.pt")
        >>> wrapper = GraphPESWrapper(model)
        >>> state = ts.SimState(
        ...     positions=torch.randn(10, 3),
        ...     cell=torch.eye(3),
        ...     atomic_numbers=torch.randint(1, 104, (10,)),
        ... )
        >>> wrapper(state)
    """

    def __init__(
        self,
        model: GraphPESModel | str | Path,
        device: torch.device | None = None,
        dtype: torch.dtype = torch.float64,
        *,
        compute_forces: bool = True,
        compute_stress: bool = True,
    ) -> None:
        """Initialize the GraphPESWrapper.

        Args:
            model: GraphPESModel instance, or a path to a model file
            device: Device to run the model on
            dtype: Data type for the model
            compute_forces: Whether to compute forces
            compute_stress: Whether to compute stress
        """
        super().__init__()
        self._device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self._dtype = dtype

        _model = model if isinstance(model, GraphPESModel) else load_model(model)
        self._gp_model = _model.to(device=self.device, dtype=self.dtype)

        self._compute_forces = compute_forces
        self._compute_stress = compute_stress

        self._properties: list[PropertyKey] = ["energy"]
        if self.compute_forces:
            self._properties.append("forces")
        if self.compute_stress:
            self._properties.append("stress")

        if self._gp_model.cutoff.item() < 0.5:
            self._memory_scales_with = "n_atoms"

    def forward(self, state: ts.SimState | StateDict) -> dict[str, torch.Tensor]:
        """Forward pass for the GraphPESWrapper.

        Args:
            state: SimState object containing atomic positions, cell, and atomic numbers

        Returns:
            Dictionary containing the computed energies, forces, and stresses
            (where applicable)
        """
        if not isinstance(state, ts.SimState):
            state = ts.SimState(**state)  # type: ignore[arg-type]

        atomic_graph = state_to_atomic_graph(state, self._gp_model.cutoff)
        return self._gp_model.predict(atomic_graph, self._properties)  # type: ignore[return-value]
