from typing import Optional, Dict, Callable, Set
from .errors import (
    CoreStepAlreadySetError,
    StepNameConflictError,
    StepBranchingCannotBeUsedWithoutNextStepError,
)


"""
This module stores the data from the decorators
"""

# The name of the core step of the application
_core_step: Optional[str] = None
# The name of the step to call next, E.g. "step_1" -> "step_2"
_step_sequence: Dict[str, Optional[str]] = {}
# The name of the step to callable
_step_name_to_callable: Dict[str, Callable] = {}


def reset_storage() -> None:
    """
    Reset the data from the decorators
    """
    global _core_step, _step_sequence, _step_name_to_callable
    _core_step = None
    _step_sequence = {}
    _step_name_to_callable = {}

def set_core_step(core_step: str) -> None:
    """
    Set the core step of the application
    """
    global _core_step
    if _core_step is None:
        _core_step = core_step
    else:
        raise CoreStepAlreadySetError(f'Core step "{core_step}" already set')


def get_core_step() -> Optional[str]:
    """
    Get the core step of the application
    """
    return _core_step


def get_next_step(step: str) -> Optional[str]:
    """
    Get the next step of the application
    """
    return _step_sequence.get(step)


def get_step_to_callable(step: str) -> Optional[Callable]:
    """
    Get the callable of the step
    """
    return _step_name_to_callable.get(step)


def set_step_to_callable(step: str, callable: Callable) -> None:
    """
    Set the callable of the step
    """
    if step in _step_name_to_callable:
        raise StepNameConflictError(f'Step "{step}" already exist')

    _step_name_to_callable[step] = callable


def set_next_step(step: str, next_step: Optional[str]) -> None:
    """
    Set the sequence of steps of the application
    """
    _step_sequence[step] = next_step
