from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...theme_reducer import ThemeState

from ..properties_name import *
from .....system.color_manipulator import alpha

def py_group_box(_theme):
    theme: ThemeState = _theme

    _color = {
        'focused': theme.palette.text.primary,
        'active': theme.palette.text.secondary,
        'placeholder': theme.palette.text.disabled,
    }

    return {
        'PyGroupBox': {
            'styles': {
                'root': {
                    # color: "red",
                    # backgroundColor: "#ffffff",
                    # border: "1px solid red",
                    # borderRadius: "5px",
                    # m: "0px",
                    # marginTop: "10px",
                    # height:"35px",

                    margin: "0px",
                    marginTop: "10px",
                    backgroundColor: "transparent",

                    border: f"1px solid {alpha(theme.palette.grey._500, 0.2)}",
                    borderRadius: f'{theme.shape.borderRadius}px',

                    "slots": {
                        "hover": {
                            borderColor: _color['active']
                        },
                        "focused": {
                            borderColor: _color['focused']
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
                    subcontrolOrigin: "margin",
                    left:"10px",
                    border: "1px solid red",
                    # bottom: "5px",
                    height: 20,
                }
            },
        },
    }