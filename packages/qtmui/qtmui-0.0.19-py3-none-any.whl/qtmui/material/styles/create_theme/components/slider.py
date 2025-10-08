from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha

def slider(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == 'light'

    return {
        "PySlider": {
            "styles": {
                "root": {
                    "slots": {
                        "disabled": {
                            color: theme.palette.action.disabled,
                        }
                    }
                },
                "rail": {
                    "opacity": 0.32,
                },
                "markLabel": {
                    "fontSize": 13,
                    "color": theme.palette.text.disabled,
                },
                "valueLabel": {
                    color: theme.palette.text.secondary,
                    fontSize: theme.typography.button.fontSize,
                    fontWeight: theme.typography.button.fontWeight,
                    lineHeight: theme.typography.button.lineHeight,
                    # "borderRadius": 8,
                    # "backgroundColor": theme.palette.grey._800 if lightMode else theme.palette.grey._700,
                },
            },
        },
    }
