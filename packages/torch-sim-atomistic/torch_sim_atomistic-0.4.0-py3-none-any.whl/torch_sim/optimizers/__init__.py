"""Optimizers for geometry relaxations.

This module provides optimization algorithms for atomic structures in a batched format,
enabling efficient relaxation of multiple atomic structures simultaneously. It uses a
filter-based design where cell optimization constraints and parameterizations are
handled by separate filter functions.
"""

from collections.abc import Callable
from enum import StrEnum
from typing import Any, Final, Literal, get_args

from torch_sim.optimizers.cell_filters import CellFireState, CellOptimState  # noqa: F401
from torch_sim.optimizers.fire import fire_init, fire_step
from torch_sim.optimizers.gradient_descent import (
    gradient_descent_init,
    gradient_descent_step,
)
from torch_sim.optimizers.state import FireState, OptimState  # noqa: F401


FireFlavor = Literal["vv_fire", "ase_fire"]
vv_fire_key, ase_fire_key = get_args(FireFlavor)


class Optimizer(StrEnum):
    """Enumeration of the optimization flavors."""

    gradient_descent = "gradient_descent"
    fire = "fire"


OPTIM_REGISTRY: Final[dict[Optimizer, tuple[Callable[..., Any], Callable[..., Any]]]] = {
    Optimizer.gradient_descent: (gradient_descent_init, gradient_descent_step),
    Optimizer.fire: (fire_init, fire_step),
}
