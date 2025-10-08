from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def tooltip(_theme) -> Dict:
    theme: ThemeState = _theme

    lightMode = theme.palette.mode == "light"

    return {
        "PyTooltip": {
            "styles": {
                "tooltip": {
                    backgroundColor: theme.palette.grey._800 if lightMode else theme.palette.grey._700,
                    color: theme.palette.text.secondary,
                    p: "10px",
                    borderRadius: '17px',
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: theme.typography.body2.fontWeight,
                },
                "arrow": {
                    color: theme.palette.grey._800 if lightMode else theme.palette.grey._700,
                },
            }
        },
    }
