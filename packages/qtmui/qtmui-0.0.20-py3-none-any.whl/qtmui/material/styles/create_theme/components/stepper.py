from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def stepper(_theme) -> Dict:
    theme: ThemeState = _theme
    # theme = _theme
    return {
        'PyStepper': {
            'styles': {
                "root": {
                    backgroundColor: "transparent"
                },
            },
        },
    }
