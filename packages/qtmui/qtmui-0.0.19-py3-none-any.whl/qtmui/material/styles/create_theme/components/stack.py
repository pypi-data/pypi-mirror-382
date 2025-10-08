from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def stack(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme
    return {
        'PyStack': {
            'styles': {
                "root": {
                    "props": {
                        "outlinedVariant": {
                            border: f"1px solid {theme.palette.grey._300 if theme.palette.mode == "light" else theme.palette.grey._700}"
                        }
                    }
                },
            },
        },
    }
