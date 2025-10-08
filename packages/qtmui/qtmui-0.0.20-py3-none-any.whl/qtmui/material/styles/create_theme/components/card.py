from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def card(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyCard': {
            'styles': {
                'root': {
                    backgroundColor: theme.palette.background.paper,
                    boxShadow: theme.customShadows.card,
                    border: f"1px solid {alpha(theme.palette.grey._500, 0.12)}",
                    borderRadius: theme.shape.borderRadius * 4,
                },
            },
        },
        'PyCardHeader': {
            'styles': {
                'root': {
                    'padding': theme.spacing(3, 3, 0),
                },
            },
        },
        'PyCardContent': {
            'styles': {
                'root': {
                    'padding': theme.spacing(3),
                },
            },
        },
    }
