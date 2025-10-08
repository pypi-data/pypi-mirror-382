from functools import wraps
import inspect
from typing import Callable, Optional, List
import hashlib
from functools import lru_cache, partial
from qtpy.QtCore import QObject, Signal
from .use_state import State, useState
def useCallback(callback: Callable, dependencies: Optional[List[State]]): ...