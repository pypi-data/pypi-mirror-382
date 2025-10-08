import inspect
from typing import Callable, List, Optional
from .hook_state import get_hook_state
def useCallback(callback: Callable, dependencies: Optional[List[Any]]): ...