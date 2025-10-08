from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def upload(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyUpload': {
            'styles': {
                'root': {
                    border: f"1px dashed {theme.palette.grey._500}",
                    borderRadius: "10px",
                    backgroundColor: theme.palette.background.paper,
                },
            },
        },

    }
