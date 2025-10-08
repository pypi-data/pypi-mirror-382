import inspect
from typing import Callable, List
from .use_state import State
def useEffect(callback: Callable, dependencies: List[State]): ...