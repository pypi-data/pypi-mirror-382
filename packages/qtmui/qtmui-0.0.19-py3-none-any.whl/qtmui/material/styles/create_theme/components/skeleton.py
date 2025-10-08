from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def skeleton(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme

    # border: 1px solid transparent;
    # border-radius: {self._radius}px;
    # color: white;

    return {
        'PySkeleton': {
            'styles': {
                "root": {
                    border: f"1px solid transparent",
                    borderRadius: f"{theme.shape.borderRadius*2}px",
                    backgroundImage: "none",
                },
                'outlined': {
                    borderColor: alpha(theme.palette.grey._500, 0.16),
                },
            },
        },
    }
