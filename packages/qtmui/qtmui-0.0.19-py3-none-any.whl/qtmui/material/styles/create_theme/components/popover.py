from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def popover(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme

    isLightMode = theme.palette.mode == "light"

    return {
        'PyPopover': {
            'styles': {
                "root": {
                    backgroundColor: f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme.palette.grey._200}, stop:1 {theme.palette.grey._100})" if isLightMode else
                    f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {theme.palette.grey._800}, stop:1 {theme.palette.grey._900})",
                    border: '2px solid transparent',
                    borderRadius: '8px',
                },
                'paper': {
                    paddingTop: "0px",
                    paddingBottom: "0px",
                },
            },
        },
    }
