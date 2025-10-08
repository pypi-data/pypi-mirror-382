from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...theme_reducer import ThemeState

from ..properties_name import *
from .....system.color_manipulator import alpha

def py_line_edit(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyLineEdit': {
            'styles': {
                'root': {
                    paddingLeft: theme.spacing(1),
                    "slots": {
                        "hover": {
                            borderRadius: theme.shape.borderRadius * 4,
                        },
                        "focus": {
                            borderRadius: theme.shape.borderRadius * 4,
                        },
                    },
                    "props": {
                        "error": {
                            borderRadius: theme.shape.borderRadius * 4,
                        },
                        "validate": {
                            borderRadius: theme.shape.borderRadius * 4,
                        },
                    },
                },
                "placeholder": {
                    color: theme.palette.text.secondary,
                }
            },
        },
    }