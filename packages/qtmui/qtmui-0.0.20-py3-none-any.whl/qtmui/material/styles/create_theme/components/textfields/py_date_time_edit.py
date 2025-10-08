from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ...theme_reducer import ThemeState

from ..properties_name import *
from .....system.color_manipulator import alpha

def py_date_time_edit(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyDateTimeEdit': {
            'styles': {
                'root': {
                    lineHeight: theme.typography.body2.lineHeight,
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: 600,
                    color: theme.palette.text.primary,
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