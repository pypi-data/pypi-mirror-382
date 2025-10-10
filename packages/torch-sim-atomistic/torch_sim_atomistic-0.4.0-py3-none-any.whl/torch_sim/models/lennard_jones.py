"""Classical pairwise interatomic potential model.

This module implements the Lennard-Jones potential for molecular dynamics simulations.
It provides efficient calculation of energies, forces, and stresses based on the
classic 12-6 potential function. The implementation supports both full pairwise
calculations and neighbor list-based optimizations.

Example::

    # Create a Lennard-Jones model with default parameters
    model = LennardJonesModel(device=torch.device("cuda"))

    # Create a model with custom parameters
    model = LennardJonesModel(
        sigma=3.405,  # Angstroms
        epsilon=0.01032,  # eV
        cutoff=10.0,  # Angstroms
        compute_stress=True,
    )

    # Calculate properties for a simulation state
    output = model(sim_state)
    energy = output["energy"]
    forces = output["forces"]
"""

import torch

import torch_sim as ts
from torch_sim import transforms
from torch_sim.models.interface import ModelInterface
from torch_sim.neighbors import vesin_nl_ts
from torch_sim.typing import StateDict


DEFAULT_SIGMA = 1.0
DEFAULT_EPSILON = 1.0


def lennard_jones_pair(
    dr: torch.Tensor,
    sigma: float | torch.Tensor = DEFAULT_SIGMA,
    epsilon: float | torch.Tensor = DEFAULT_EPSILON,
) -> torch.Tensor:
    """Calculate pairwise Lennard-Jones interaction energies between particles.

    Implements the standard 12-6 Lennard-Jones potential that combines short-range
    repulsion with longer-range attraction. The potential has a minimum at r=sigma.

    The functional form is:
    V(r) = 4*epsilon*[(sigma/r)^12 - (sigma/r)^6]

    Args:
        dr: Pairwise distances between particles. Shape: [n, m].
        sigma: Distance at which potential reaches its minimum. Either a scalar float
            or tensor of shape [n, m] for particle-specific interaction distances.
        epsilon: Depth of the potential well (energy scale). Either a scalar float
            or tensor of shape [n, m] for pair-specific interaction strengths.

    Returns:
        torch.Tensor: Pairwise Lennard-Jones interaction energies between particles.
            Shape: [n, m]. Each element [i,j] represents the interaction energy between
            particles i and j.
    """
    # Calculate inverse dr and its powers
    idr = sigma / dr
    idr2 = idr * idr
    idr6 = idr2 * idr2 * idr2
    idr12 = idr6 * idr6

    # Calculate potential energy
    energy = 4.0 * epsilon * (idr12 - idr6)

    # Handle potential numerical instabilities and infinities
    return torch.where(dr > 0, energy, torch.zeros_like(energy))
    # return torch.nan_to_num(energy, nan=0.0, posinf=0.0, neginf=0.0)


def lennard_jones_pair_force(
    dr: torch.Tensor,
    sigma: float | torch.Tensor = DEFAULT_SIGMA,
    epsilon: float | torch.Tensor = DEFAULT_EPSILON,
) -> torch.Tensor:
    """Calculate pairwise Lennard-Jones forces between particles.

    Implements the force derived from the 12-6 Lennard-Jones potential. The force
    is repulsive at short range and attractive at long range, with a zero-crossing
    at r=sigma.

    The functional form is:
    F(r) = 24*epsilon/r * [(2*sigma^12/r^12) - (sigma^6/r^6)]

    This is the negative gradient of the Lennard-Jones potential energy.

    Args:
        dr: Pairwise distances between particles. Shape: [n, m].
        sigma: Distance at which force changes from repulsive to attractive.
            Either a scalar float or tensor of shape [n, m] for particle-specific
            interaction distances.
        epsilon: Energy scale of the interaction. Either a scalar float or tensor
            of shape [n, m] for pair-specific interaction strengths.

    Returns:
        torch.Tensor: Pairwise Lennard-Jones forces between particles. Shape: [n, m].
            Each element [i,j] represents the force magnitude between particles i and j.
            Positive values indicate repulsion, negative values indicate attraction.
    """
    # Calculate inverse dr and its powers
    idr = sigma / dr
    idr2 = idr * idr
    idr6 = idr2 * idr2 * idr2
    idr12 = idr6 * idr6

    # Calculate force (negative gradient of potential)
    # F = -24*epsilon/r * ((sigma/r)^6 - 2*(sigma/r)^12)
    force = 24.0 * epsilon / dr * (2.0 * idr12 - idr6)

    # Handle potential numerical instabilities and infinities
    return torch.where(dr > 0, force, torch.zeros_like(force))


class LennardJonesModel(ModelInterface):
    """Lennard-Jones potential energy and force calculator.

    Implements the Lennard-Jones 12-6 potential for molecular dynamics simulations.
    This model calculates pairwise interactions between atoms and supports either
    full pairwise calculation or neighbor list-based optimization for efficiency.

    Attributes:
        sigma (torch.Tensor): Length parameter controlling particle size/repulsion
            distance.
        epsilon (torch.Tensor): Energy parameter controlling interaction strength.
        cutoff (torch.Tensor): Distance cutoff for truncating potential calculation.
        device (torch.device): Device where calculations are performed.
        dtype (torch.dtype): Data type used for calculations.
        compute_forces (bool): Whether to compute atomic forces.
        compute_stress (bool): Whether to compute stress tensor.
        per_atom_energies (bool): Whether to compute per-atom energy decomposition.
        per_atom_stresses (bool): Whether to compute per-atom stress decomposition.
        use_neighbor_list (bool): Whether to use neighbor list optimization.

    Example::

        # Basic usage with default parameters
        lj_model = LennardJonesModel(device=torch.device("cuda"))
        results = lj_model(sim_state)

        # Custom parameterization for Argon
        ar_model = LennardJonesModel(
            sigma=3.405,  # Å
            epsilon=0.0104,  # eV
            cutoff=8.5,  # Å
            compute_stress=True,
        )
    """

    def __init__(
        self,
        sigma: float = 1.0,
        epsilon: float = 1.0,
        device: torch.device | None = None,
        dtype: torch.dtype = torch.float32,
        *,  # Force keyword-only arguments
        compute_forces: bool = True,
        compute_stress: bool = False,
        per_atom_energies: bool = False,
        per_atom_stresses: bool = False,
        use_neighbor_list: bool = True,
        cutoff: float | None = None,
    ) -> None:
        """Initialize the Lennard-Jones potential calculator.

        Creates a model with specified interaction parameters and computational flags.
        The model can be configured to compute different properties (forces, stresses)
        and use different optimization strategies.

        Args:
            sigma (float): Length parameter of the Lennard-Jones potential in distance
                units. Controls the size of particles. Defaults to 1.0.
            epsilon (float): Energy parameter of the Lennard-Jones potential in energy
                units. Controls the strength of the interaction. Defaults to 1.0.
            device (torch.device | None): Device to run computations on. If None, uses
                CPU. Defaults to None.
            dtype (torch.dtype): Data type for calculations. Defaults to torch.float32.
            compute_forces (bool): Whether to compute forces. Defaults to True.
            compute_stress (bool): Whether to compute stress tensor. Defaults to False.
            per_atom_energies (bool): Whether to compute per-atom energy decomposition.
                Defaults to False.
            per_atom_stresses (bool): Whether to compute per-atom stress decomposition.
                Defaults to False.
            use_neighbor_list (bool): Whether to use a neighbor list for optimization.
                Significantly faster for large systems. Defaults to True.
            cutoff (float | None): Cutoff distance for interactions in distance units.
                If None, uses 2.5*sigma. Defaults to None.

        Example::

            # Model with custom parameters
            model = LennardJonesModel(
                sigma=3.405,
                epsilon=0.01032,
                device=torch.device("cuda"),
                dtype=torch.float64,
                compute_stress=True,
                per_atom_energies=True,
                cutoff=10.0,
            )
        """
        super().__init__()
        self._device = device or torch.device("cpu")
        self._dtype = dtype
        self._compute_forces = compute_forces
        self._compute_stress = compute_stress
        self.per_atom_energies = per_atom_energies
        self.per_atom_stresses = per_atom_stresses
        self.use_neighbor_list = use_neighbor_list

        # Convert parameters to tensors
        self.sigma = torch.tensor(sigma, dtype=dtype, device=self.device)
        self.cutoff = torch.tensor(cutoff or 2.5 * sigma, dtype=dtype, device=self.device)
        self.epsilon = torch.tensor(epsilon, dtype=dtype, device=self.device)

    def unbatched_forward(
        self,
        state: ts.SimState,
    ) -> dict[str, torch.Tensor]:
        """Compute Lennard-Jones properties for a single unbatched system.

        Internal implementation that processes a single, non-batched simulation state.
        This method handles the core computations of pair interactions, neighbor lists,
        and property calculations.

        Args:
            state (SimState): Single, non-batched simulation state containing atomic
                positions, cell vectors, and other system information.

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
            This method handles two different approaches:
            1. Neighbor list approach: Efficient for larger systems
            2. Full pairwise calculation: Better for small systems

            The implementation applies cutoff distance to both approaches for consistency.
        """
        if not isinstance(state, ts.SimState):
            state = ts.SimState(**state)

        positions = state.positions
        cell = state.row_vector_cell
        cell = cell.squeeze()
        pbc = state.pbc

        if self.use_neighbor_list:
            # Get neighbor list using vesin_nl_ts
            mapping, shifts = vesin_nl_ts(
                positions=positions,
                cell=cell,
                pbc=pbc,
                cutoff=self.cutoff,
                sort_id=False,
            )
            # Get displacements using neighbor list
            dr_vec, distances = transforms.get_pair_displacements(
                positions=positions, cell=cell, pbc=pbc, pairs=mapping, shifts=shifts
            )
        else:
            # Get all pairwise displacements
            dr_vec, distances = transforms.get_pair_displacements(
                positions=positions, cell=cell, pbc=pbc
            )
            # Mask out self-interactions
            mask = torch.eye(positions.shape[0], dtype=torch.bool, device=self.device)
            distances = distances.masked_fill(mask, float("inf"))
            # Apply cutoff
            mask = distances < self.cutoff
            # Get valid pairs - match neighbor list convention for pair order
            i, j = torch.where(mask)
            mapping = torch.stack([j, i])
            # Get valid displacements and distances
            dr_vec = dr_vec[mask]
            distances = distances[mask]

        # Calculate pair energies and apply cutoff
        pair_energies = lennard_jones_pair(
            distances, sigma=self.sigma, epsilon=self.epsilon
        )
        # Zero out energies beyond cutoff
        mask = distances < self.cutoff
        pair_energies = torch.where(mask, pair_energies, torch.zeros_like(pair_energies))

        # Initialize results with total energy (sum/2 to avoid double counting)
        results = {"energy": 0.5 * pair_energies.sum()}

        if self.per_atom_energies:
            atom_energies = torch.zeros(
                positions.shape[0], dtype=self.dtype, device=self.device
            )
            # Each atom gets half of the pair energy
            atom_energies.index_add_(0, mapping[0], 0.5 * pair_energies)
            atom_energies.index_add_(0, mapping[1], 0.5 * pair_energies)
            results["energies"] = atom_energies

        if self.compute_forces or self.compute_stress:
            # Calculate forces and apply cutoff
            pair_forces = lennard_jones_pair_force(
                distances, sigma=self.sigma, epsilon=self.epsilon
            )
            pair_forces = torch.where(mask, pair_forces, torch.zeros_like(pair_forces))

            # Project forces along displacement vectors
            force_vectors = (pair_forces / distances)[:, None] * dr_vec

            if self.compute_forces:
                # Initialize forces tensor
                forces = torch.zeros_like(positions)
                # Add force contributions (f_ij on i, -f_ij on j)
                forces.index_add_(0, mapping[0], -force_vectors)
                forces.index_add_(0, mapping[1], force_vectors)
                results["forces"] = forces

            if self.compute_stress and cell is not None:
                # Compute stress tensor
                stress_per_pair = torch.einsum("...i,...j->...ij", dr_vec, force_vectors)
                volume = torch.abs(torch.linalg.det(cell))

                results["stress"] = -stress_per_pair.sum(dim=0) / volume

                if self.per_atom_stresses:
                    atom_stresses = torch.zeros(
                        (state.positions.shape[0], 3, 3),
                        dtype=self.dtype,
                        device=self.device,
                    )
                    atom_stresses.index_add_(0, mapping[0], -0.5 * stress_per_pair)
                    atom_stresses.index_add_(0, mapping[1], -0.5 * stress_per_pair)
                    results["stresses"] = atom_stresses / volume

        return results

    def forward(self, state: ts.SimState | StateDict) -> dict[str, torch.Tensor]:
        """Compute Lennard-Jones energies, forces, and stresses for a system.

        Main entry point for Lennard-Jones calculations that handles batched states by
        dispatching each system to the unbatched implementation and combining results.

        Args:
            state (SimState | StateDict): Input state containing atomic positions,
                cell vectors, and other system information. Can be a SimState object
                or a dictionary with the same keys.

        Returns:
            dict[str, torch.Tensor]: Computed properties:
                - "energy": Potential energy with shape [n_systems]
                - "forces": Atomic forces with shape [n_atoms, 3] (if
                    compute_forces=True)
                - "stress": Stress tensor with shape [n_systems, 3, 3] (if
                    compute_stress=True)
                - "energies": Per-atom energies with shape [n_atoms] (if
                    per_atom_energies=True)
                - "stresses": Per-atom stresses with shape [n_atoms, 3, 3] (if
                    per_atom_stresses=True)

        Raises:
            ValueError: If system cannot be inferred for multi-cell systems.

        Example::

            # Compute properties for a simulation state
            model = LennardJonesModel(compute_stress=True)
            results = model(sim_state)

            energy = results["energy"]  # Shape: [n_systems]
            forces = results["forces"]  # Shape: [n_atoms, 3]
            stress = results["stress"]  # Shape: [n_systems, 3, 3]
            energies = results["energies"]  # Shape: [n_atoms]
            stresses = results["stresses"]  # Shape: [n_atoms, 3, 3]
        """
        sim_state = (
            state
            if isinstance(state, ts.SimState)
            else ts.SimState(**state, masses=torch.ones_like(state["positions"]))
        )

        if sim_state.system_idx is None and sim_state.cell.shape[0] > 1:
            raise ValueError("System can only be inferred for batch size 1.")

        outputs = [
            self.unbatched_forward(sim_state[idx]) for idx in range(sim_state.n_systems)
        ]
        properties = outputs[0]

        # we always return tensors
        # per atom properties are returned as (atoms, ...) tensors
        # global properties are returned as shape (..., n) tensors
        results: dict[str, torch.Tensor] = {}
        for key in ("stress", "energy"):
            if key in properties:
                results[key] = torch.stack([out[key] for out in outputs])
        for key in ("forces", "energies", "stresses"):
            if key in properties:
                results[key] = torch.cat([out[key] for out in outputs], dim=0)

        return results
