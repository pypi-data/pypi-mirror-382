from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...theme_reducer import ThemeState

from ..properties_name import *
from .....system.color_manipulator import alpha

def py_outlined_input(_theme):
    theme: ThemeState = _theme

    _color = {
        'focused': theme.palette.text.primary,
        'active': theme.palette.text.secondary,
        'placeholder': theme.palette.text.disabled,
    }

    return {
        'PyOutlinedInput': {
            'styles': {
                'root': {
                    borderColor: alpha(theme.palette.grey._500, 0.2),
                    "slots": {
                        "hover": {
                            borderColor: _color['active']
                        },
                        "focus": {
                            borderColor: _color['focused']
                        },
                        'disable': {
                            borderColor: theme.palette.action.disabledBackground
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

                "inputField": {
                    "root": {
                        paddingLeft: 8,
                        "props": {
                            "hasStartAdornment": {
                                paddingLeft: "0px"
                            }
                        }
                    }
                }
            },
        },
    }