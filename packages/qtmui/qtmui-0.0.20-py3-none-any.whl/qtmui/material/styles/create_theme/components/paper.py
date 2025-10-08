from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def paper(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme
    return {
        'PyPaper': {
            'styles': {
                "root": {
                    border: f"1px solid transparent",
                    borderRadius: f"{theme.shape.borderRadius*2}px",
                    backgroundImage: "none",
                    backgroundColor:  theme.palette.background.paper
                },
                'outlined': {
                    borderColor: alpha(theme.palette.grey._500, 0.16),
                },
            },
        },
    }
