from typing import Callable
from ..lib.validator import Validator
class ReTurnType:
    validate: Callable
    errors: dict
def yupResolver(schema): ...