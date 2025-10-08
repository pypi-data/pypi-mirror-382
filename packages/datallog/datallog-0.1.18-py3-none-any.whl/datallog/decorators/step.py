from functools import wraps
from typing import Optional, Callable
from datallog.utils.storage import set_next_step, set_step_to_callable, set_core_step




def step(*, next_step: Optional[str] = None, core_step: bool = False) -> Callable:
    """
    Decorator to mark a function as a step in a sequence.
    
    Args:
        next_step (Optional[str]): The name of the next step in the sequence.
        core_step (bool): Whether the step is the core step of the application. (first step)
    """

    def decorator(func):
        set_step_to_callable(func.__name__, func)
        set_next_step(func.__name__, next_step)
        if core_step:
            set_core_step(func.__name__)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
