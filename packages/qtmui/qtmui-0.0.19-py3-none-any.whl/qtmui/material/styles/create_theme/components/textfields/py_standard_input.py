from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...theme_reducer import ThemeState

from ..properties_name import *
from .....system.color_manipulator import alpha

def py_standard_input(_theme):
    theme: ThemeState = _theme

    _color = {
        'focused': theme.palette.text.primary,
        'active': theme.palette.text.secondary,
        'placeholder': theme.palette.text.disabled,
    }

    return {
        'PyStandardInput': {
            'styles': {
                'root': {
                    borderColor: "transparent",
                    borderBottom: f"1px solid {alpha(theme.palette.grey._500, 0.32)}" ,
                    borderRadius: '0px',
                    "slots": {
                        "hover": {
                            borderColor: "transparent",
                            borderBottom: f"1px solid {_color['active']}" ,
                        },
                        "focus": {
                            borderColor: "transparent",
                            borderBottom: f"1px solid {_color['focused']}" ,
                        },
                        'disable': {
                            borderColor: "transparent",
                            borderBottom: f"1px solid {theme.palette.action.disabledBackground}" ,
                        },
                    },
                    "props": {
                        "error": {
                            borderColor: theme.palette.error.main
                        },
                        "validate": {
                            borderColor: theme.palette.success.main
                        },
                    },
                },
                "title": {
                    left: 0
                },
                "inputField": {
                    "root": {
                        paddingLeft: 0,
                    }
                }
            },
        },
    }