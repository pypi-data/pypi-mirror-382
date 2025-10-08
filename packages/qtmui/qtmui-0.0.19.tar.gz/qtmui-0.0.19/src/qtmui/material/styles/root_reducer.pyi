from redux.combine_reducers import combine_reducers
from .create_theme.theme_reducer import theme_reducer, ThemeState
from .location_reducer import location_reducer, LocationState
from redux import BaseAction, BaseCombineReducerState, CombineReducerAction, CombineReducerRegisterAction, CombineReducerUnregisterAction, InitAction, InitializationActionError, Store, combine_reducers
from redux.basic_types import BaseEvent, CompleteReducerResult, FinishAction, ReducerResult
class ProductAction:
class UserAction:
class StateType:
    theme: ThemeState
    location: LocationState