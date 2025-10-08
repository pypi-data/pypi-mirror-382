from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def py_svg_widget(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme
    return {
        'PySvgWidget': {
            'styles': {
                "root": lambda ownerState:  {
                    color: theme.palette.grey._500,
                    "padding": "5px"
                },
            },
        },
    }
