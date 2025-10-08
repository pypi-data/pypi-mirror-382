import uuid
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from functools import wraps
import uuid
from dataclasses import replace
from .use_state import useState
from ..immutable import Immutable
from redux import BaseAction, BaseEvent, CompleteReducerResult, FinishAction, ReducerResult
from redux.main import Store
class InitialState:
    currentLocation: Optional[str]
    params: Optional[dict]
class UpdateCurrentLocationAction:
    currentLocation: Optional[str]
class UpdatePushParamsAction:
    params: Optional[dict]
def reducer(state: Any, action: BaseAction): ...
def useRouter(): ...
def useSearchParams(): ...
def useLocation(): ...
def update_location(currentLocation): ...
def update_params(params): ...