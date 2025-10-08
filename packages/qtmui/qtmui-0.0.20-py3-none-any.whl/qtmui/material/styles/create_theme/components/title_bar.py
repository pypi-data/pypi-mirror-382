from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def title_bar(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme
    return {
        'PyTitleBar': {
            'styles': {
                "root": {
                    backgroundColor: theme.palette.background.navigation,
                    borderBottom: f"1px solid {alpha(theme.palette.grey._500, 0.16)}"
                },
            },
        },
    }
