"""Anharmonic interatomic potential for molecular dynamics.

This module implements the Morse potential for molecular dynamics simulations.
The Morse potential provides a more realistic description of anharmonic bond
behavior than simple harmonic potentials, capturing bond breaking and formation.
It includes both energy and force calculations with support for neighbor lists.

Example::

    # Create a Morse model with default parameters
    model = MorseModel(device=torch.device("cuda"))

    # Calculate properties for a simulation state
    output = model(sim_state)
    energy = output["energy"]
    forces = output["forces"]

Notes:
    The Morse potential follows the form:
    V(r) = D_e * (1 - exp(-a(r-r_e)))^2

    Where:
    - D_e (epsilon) is the well depth (dissociation energy)
    - r_e (sigma) is the equilibrium bond distance
    - a (alpha) controls the width of the potential well
"""

import torch

import torch_sim as ts
from torch_sim import transforms
from torch_sim.models.interface import ModelInterface
from torch_sim.neighbors import vesin_nl_ts
from torch_sim.typing import StateDict


DEFAULT_SIGMA = 1.0
DEFAULT_EPSILON = 5.0
DEFAULT_ALPHA = 5.0


def morse_pair(
    dr: torch.Tensor,
    sigma: float | torch.Tensor = DEFAULT_SIGMA,
    epsilon: float | torch.Tensor = DEFAULT_EPSILON,
    alpha: float | torch.Tensor = DEFAULT_ALPHA,
) -> torch.Tensor:
    """Calculate pairwise Morse potential energies between particles.

    Implements the Morse potential that combines short-range repulsion with
    longer-range attraction. The potential has a minimum at r=sigma and approaches
    -epsilon as r→∞.

    The functional form is:
    V(r) = epsilon * (1 - exp(-alpha*(r-sigma)))^2 - epsilon

    Args:
        dr: Pairwise distances between particles. Shape: [n, m].
        sigma: Distance at which potential reaches its minimum. Either a scalar float
            or tensor of shape [n, m] for particle-specific equilibrium distances.
        epsilon: Depth of the potential well (energy scale). Either a scalar float
            or tensor of shape [n, m] for pair-specific interaction strengths.
        alpha: Controls the width of the potential well. Larger values give a narrower
            well. Either a scalar float or tensor of shape [n, m].

    Returns:
        torch.Tensor: Pairwise Morse interaction energies between particles.
            Shape: [n, m]. Each element [i,j] represents the interaction energy between
            particles i and j.
    """
    # Calculate potential energy
    energy = epsilon * (1.0 - torch.exp(-alpha * (dr - sigma))).pow(2) - epsilon

    # Handle potential numerical instabilities
    return torch.where(dr > 0, energy, torch.zeros_like(energy))


def morse_pair_force(
    dr: torch.Tensor,
    sigma: float | torch.Tensor = DEFAULT_SIGMA,
    epsilon: float | torch.Tensor = DEFAULT_EPSILON,
    alpha: float | torch.Tensor = DEFAULT_ALPHA,
) -> torch.Tensor:
    """Calculate pairwise Morse forces between particles.

    Implements the force derived from the Morse potential. The force changes
    from repulsive to attractive at r=sigma.

    The functional form is:
    F(r) = 2*alpha*epsilon * exp(-alpha*(r-sigma)) * (1 - exp(-alpha*(r-sigma)))

    This is the negative gradient of the Morse potential energy.

    Args:
        dr: Pairwise distances between particles. Shape: [n, m].
        sigma: Distance at which force changes from repulsive to attractive.
            Either a scalar float or tensor of shape [n, m].
        epsilon: Energy scale of the interaction. Either a scalar float or tensor
            of shape [n, m].
        alpha: Controls the force range and stiffness. Either a scalar float or
            tensor of shape [n, m].

    Returns:
        torch.Tensor: Pairwise Morse forces between particles. Shape: [n, m].
            Positive values indicate repulsion, negative values indicate attraction.
    """
    exp_term = torch.exp(-alpha * (dr - sigma))
    force = -2.0 * alpha * epsilon * exp_term * (1.0 - exp_term)

    # Handle potential numerical instabilities
    return torch.where(dr > 0, force, torch.zeros_like(force))


class MorseModel(ModelInterface):
    """Morse potential energy and force calculator.

    Implements the Morse potential for molecular dynamics simulations. This model
    is particularly useful for modeling covalent bonds as it can accurately describe
    bond stretching, breaking, and anharmonic behavior. Unlike the Lennard-Jones
    potential, Morse is often better for cases where accurate dissociation energy
    and bond dynamics are important.

    Attributes:
        sigma (torch.Tensor): Equilibrium bond length (r_e) in distance units.
        epsilon (torch.Tensor): Dissociation energy (D_e) in energy units.
        alpha (torch.Tensor): Parameter controlling the width/steepness of the potential.
        cutoff (torch.Tensor): Distance cutoff for truncating potential calculation.
        device (torch.device): Device where calculations are performed.
        dtype (torch.dtype): Data type used for calculations.
        compute_forces (bool): Whether to compute atomic forces.
        compute_stress (bool): Whether to compute stress tensor.
        per_atom_energies (bool): Whether to compute per-atom energy decomposition.
        per_atom_stresses (bool): Whether to compute per-atom stress decomposition.
        use_neighbor_list (bool): Whether to use neighbor list optimization.

    Examples:
        ```py
        # Basic usage with default parameters
        morse_model = MorseModel(device=torch.device("cuda"))
        results = morse_model(sim_state)

        # Model parameterized for O-H bonds in water, atomic units
        oh_model = MorseModel(
            sigma=0.96,
            epsilon=4.52,
            alpha=2.0,
            compute_forces=True,
            compute_stress=True,
        )
        ```
    """

    def __init__(
        self,
        sigma: float = 1.0,
        epsilon: float = 5.0,
        alpha: float = 5.0,
        device: torch.device | None = None,
        dtype: torch.dtype = torch.float32,
        *,  # Force keyword-only arguments
        compute_forces: bool = False,
        compute_stress: bool = False,
        per_atom_energies: bool = False,
        per_atom_stresses: bool = False,
        use_neighbor_list: bool = True,
        cutoff: float | None = None,
    ) -> None:
        """Initialize the Morse potential calculator.

        Creates a model with specified interaction parameters and computational flags.
        The Morse potential is defined by three key parameters: sigma (equilibrium
        distance), epsilon (dissociation energy), and alpha (width control).

        Args:
            sigma (float): Equilibrium bond distance (r_e) in distance units.
                Defaults to 1.0.
            epsilon (float): Dissociation energy (D_e) in energy units.
                Defaults to 5.0.
            alpha (float): Controls the width/steepness of the potential well.
                Larger values create a narrower well. Defaults to 5.0.
            device (torch.device | None): Device to run computations on. If None, uses
                CPU. Defaults to None.
            dtype (torch.dtype): Data type for calculations. Defaults to torch.float32.
            compute_forces (bool): Whether to compute forces. Defaults to False.
            compute_stress (bool): Whether to compute stress tensor. Defaults to False.
            per_atom_energies (bool): Whether to compute per-atom energy decomposition.
                Defaults to False.
            per_atom_stresses (bool): Whether to compute per-atom stress decomposition.
                Defaults to False.
            use_neighbor_list (bool): Whether to use a neighbor list for optimization.
                Significantly faster for large systems. Defaults to True.
            cutoff (float | None): Cutoff distance for interactions in distance units.
                If None, uses 2.5*sigma. Defaults to None.

        Examples:
            ```py
            # Basic model with default parameters
            model = MorseModel()

            # Model for diatomic hydrogen
            model = MorseModel(
                sigma=0.74,  # Å
                epsilon=4.75,  # eV
                alpha=1.94,  # Steepness parameter
                compute_forces=True,
            )
            ```

        Notes:
            The alpha parameter can be related to the harmonic force constant k and
            dissociation energy D_e by: alpha = sqrt(k/(2*D_e))
        """
        super().__init__()
        self._device = device or torch.device("cpu")
        self._dtype = dtype
        self._compute_forces = compute_forces
        self._compute_stress = compute_stress
        self._per_atom_energies = per_atom_energies
        self._per_atom_stresses = per_atom_stresses
        self.use_neighbor_list = use_neighbor_list
        # Convert parameters to tensors
        self.sigma = torch.tensor(sigma, dtype=self.dtype, device=self.device)
        self.cutoff = torch.tensor(
            cutoff or 2.5 * sigma, dtype=self.dtype, device=self.device
        )
        self.epsilon = torch.tensor(epsilon, dtype=self.dtype, device=self.device)
        self.alpha = torch.tensor(alpha, dtype=self.dtype, device=self.device)

    def unbatched_forward(
        self, state: ts.SimState | StateDict
    ) -> dict[str, torch.Tensor]:
        """Compute Morse potential properties for a single unbatched system.

        Internal implementation that processes a single, non-batched simulation state.
        This method handles the core computations of pair interactions, including
        neighbor list construction, distance calculations, and property computation.

        Args:
            state (SimState | StateDict): Single, non-batched simulation state or
                equivalent dictionary containing atomic positions, cell vectors,
                and other system information.

        Returns:
            dict[str, torch.Tensor]: Computed properties:
                - "energy": Total potential energy (scalar)
                - "forces": Atomic forces with shape [n_atoms, 3] (if
                    compute_forces=True)
                - "stress": Stress tensor with shape [3, 3] (if compute_stress=True)
                - "energies": Per-atom energies with shape [n_atoms] (if
                    per_atom_energies=True)
                - "stresses": Per-atom stresses with shape [n_atoms, 3, 3] (if
                    per_atom_stresses=True)

        Notes:
            This method can work with both neighbor list and full pairwise calculations.
            In both cases, interactions are truncated at the cutoff distance.
        """
        sim_state = (
            state
            if isinstance(state, ts.SimState)
            else ts.SimState(**state, masses=torch.ones_like(state["positions"]))
        )

        positions = sim_state.positions
        cell = sim_state.row_vector_cell
        cell = cell.squeeze()
        pbc = sim_state.pbc

        if self.use_neighbor_list:
            mapping, shifts = vesin_nl_ts(
                positions=positions,
                cell=cell,
                pbc=pbc,
                cutoff=self.cutoff,
                sort_id=False,
            )
            dr_vec, distances = transforms.get_pair_displacements(
                positions=positions,
                cell=cell,
                pbc=pbc,
                pairs=mapping,
                shifts=shifts,
            )
        else:
            dr_vec, distances = transforms.get_pair_displacements(
                positions=positions,
                cell=cell,
                pbc=pbc,
            )
            mask = torch.eye(positions.shape[0], dtype=torch.bool, device=self.device)
            distances = distances.masked_fill(mask, float("inf"))
            mask = distances < self.cutoff
            i, j = torch.where(mask)
            mapping = torch.stack([j, i])
            dr_vec = dr_vec[mask]
            distances = distances[mask]

        # Calculate pair energies and apply cutoff
        pair_energies = morse_pair(
            distances, sigma=self.sigma, epsilon=self.epsilon, alpha=self.alpha
        )
        mask = distances < self.cutoff
        pair_energies = torch.where(mask, pair_energies, torch.zeros_like(pair_energies))

        # Initialize results with total energy (sum/2 to avoid double counting)
        results = {"energy": 0.5 * pair_energies.sum()}

        if self._per_atom_energies:
            atom_energies = torch.zeros(
                positions.shape[0], dtype=self.dtype, device=self.device
            )
            atom_energies.index_add_(0, mapping[0], 0.5 * pair_energies)
            atom_energies.index_add_(0, mapping[1], 0.5 * pair_energies)
            results["energies"] = atom_energies

        if self.compute_forces or self.compute_stress:
            pair_forces = morse_pair_force(
                distances, sigma=self.sigma, epsilon=self.epsilon, alpha=self.alpha
            )
            pair_forces = torch.where(mask, pair_forces, torch.zeros_like(pair_forces))

            force_vectors = (pair_forces / distances)[:, None] * dr_vec

            if self.compute_forces:
                forces = torch.zeros_like(sim_state.positions)
                forces.index_add_(0, mapping[0], -force_vectors)
                forces.index_add_(0, mapping[1], force_vectors)
                results["forces"] = forces

            if self.compute_stress and sim_state.cell is not None:
                stress_per_pair = torch.einsum("...i,...j->...ij", dr_vec, force_vectors)
                volume = torch.abs(torch.linalg.det(sim_state.cell))

                results["stress"] = -stress_per_pair.sum(dim=0) / volume

                if self._per_atom_stresses:
                    atom_stresses = torch.zeros(
                        (sim_state.positions.shape[0], 3, 3),
                        dtype=self.dtype,
                        device=self.device,
                    )
                    atom_stresses.index_add_(0, mapping[0], -0.5 * stress_per_pair)
                    atom_stresses.index_add_(0, mapping[1], -0.5 * stress_per_pair)
                    results["stresses"] = atom_stresses / volume

        return results

    def forward(self, state: ts.SimState | StateDict) -> dict[str, torch.Tensor]:
        """Compute Morse potential energies, forces, and stresses for a system.

        Main entry point for Morse potential calculations that handles batched states
        by dispatching each batch to the unbatched implementation and combining results.

        Args:
            state (SimState | StateDict): Input state containing atomic positions,
                cell vectors, and other system information. Can be a SimState object
                or a dictionary with the same keys.

        Returns:
            dict[str, torch.Tensor]: Computed properties:
                - "energy": Potential energy with shape [n_systems]
                - "forces": Atomic forces with shape [n_atoms, 3]
                    (if compute_forces=True)
                - "stress": Stress tensor with shape [n_systems, 3, 3]
                    (if compute_stress=True)
                - May include additional outputs based on configuration

        Raises:
            ValueError: If batch cannot be inferred for multi-cell systems.

        Examples:
            ```py
            # Compute properties for a simulation state
            model = MorseModel(compute_forces=True)
            results = model(sim_state)

            energy = results["energy"]  # Shape: [n_systems]
            forces = results["forces"]  # Shape: [n_atoms, 3]
            ```
        """
        sim_state = (
            state
            if isinstance(state, ts.SimState)
            else ts.SimState(**state, masses=torch.ones_like(state["positions"]))
        )

        if sim_state.system_idx is None and sim_state.cell.shape[0] > 1:
            raise ValueError(
                "system_idx can only be inferred if there is only one system."
            )

        outputs = [
            self.unbatched_forward(sim_state[i]) for i in range(sim_state.n_systems)
        ]
        properties = outputs[0]

        # we always return tensors
        # per atom properties are returned as (atoms, ...) tensors
        # global properties are returned as shape (..., n) tensors
        results: dict[str, torch.Tensor] = {}
        for key in ("stress", "energy"):
            if key in properties:
                results[key] = torch.stack([out[key] for out in outputs])
        for key in ("forces",):
            if key in properties:
                results[key] = torch.cat([out[key] for out in outputs], dim=0)

        return results
