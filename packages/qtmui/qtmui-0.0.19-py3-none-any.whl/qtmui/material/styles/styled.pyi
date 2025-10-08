from typing import Optional, Callable
from ...utils.data import deep_merge
class StyledOptions:
    shouldForwardProp: Optional[str]
    label: Optional[str]
    name: Optional[str]
    slot: Optional[str]
    overridesResolver: Optional[Callable]
    skipVariantsResolver: Optional[bool]
    skipSx: Optional[bool]
def styled(component, options: dict, style_fn: Callable): ...