from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def drawer(_theme) -> Dict:
    theme: ThemeState = _theme

    darkMode = theme.palette.mode == "dark"

    return {
        'PyDrawer': {
            'styles': {
                'root': lambda ownerState: {
                    # backgroundColor: f"rgba({0 if darkMode else 255}, {0 if darkMode else 255}, {0 if darkMode else 255}, 0.8)",
                    backgroundColor: theme.palette.background.paper,
                    # "background": "transparent",
                    # boxShadow: f"40px 40px 80px -8px {alpha(theme.palette.grey._500 if lightMode else theme.palette.common.black, 0.24)}" if ownerState.get("anchor") == "left" else f"-40px 40px 80px -8px {alpha(theme.palette.grey._500 if lightMode else theme.palette.common.black, 0.24)}"
                },
                'contentFrame': lambda ownerState: {
                    backgroundColor: theme.palette.background.paper,
                }
            }
        }
    }
