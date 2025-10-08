from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...theme_reducer import ThemeState

from ..properties_name import *
from .....system.color_manipulator import alpha

def py_filled_input(_theme):
    theme: ThemeState = _theme

    _color = {
        'focused': theme.palette.text.primary,
        'active': theme.palette.text.secondary,
        'placeholder': theme.palette.text.disabled,
    }

    return {
        'PyFilledInput': {
            'styles': {
                'root': {
                    backgroundColor: alpha(theme.palette.grey._500, 0.16),
                    border: f"1px solid transparent",
                    "slots": {
                        "hover": {
                            backgroundColor: alpha(theme.palette.grey._500, 0.20),
                        },
                        "focus": {
                            backgroundColor: alpha(theme.palette.grey._500, 0.24),
                        },
                        'error': {
                            borderColor: theme.palette.error.main
                        },
                        'disabled': {
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
                "title": {
                    top: 6,
                    left: 8,
                    "props": {
                        "hasStartAdornment": {
                            left: 30,
                        },
                    }
                },
                "inputField": {
                    "root": {
                        paddingLeft: 8,
                        "props": {
                            "hasValue": {
                                "small": {
                                    paddingTop: 12,
                                },
                                "medium": {
                                    paddingTop: 16,
                                },
                            },
                            "hasStartAdornment": {
                                paddingLeft: 0,
                            },
                        }
                    }
                }
            },
        },
    }