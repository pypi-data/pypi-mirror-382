from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def checkbox(_theme) -> Dict:
    theme: ThemeState = _theme
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']
    lightMode = theme.palette.mode == 'light'

    return {
        # CHECKBOX, RADIO, SWITCH
        'PyFormControlLabel': {
            'styles': {
                'label': {
                    fontSize: theme.typography.body2.fontSize,
                    fontWeight: theme.typography.body2.fontWeight,
                    lineHeight: theme.typography.body2.lineHeight,
                }
            },
        },
        'PyCheckbox': {
            'styles': {
                'root': lambda ownerState: {
                    **{
                        "default": {
                            color: theme.palette.grey._900 if lightMode else theme.palette.common.white,
                            # p: theme.spacing,
                            p: '0px',
                            borderRadius: "15px" if ownerState.get("size") == "small" else "18px",
                            backgroundColor: "transparent"
                        },
                        "inherit": {
                            color: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            # p: theme.spacing,
                            p: '0px',
                            borderRadius: "15px" if ownerState.get("size") == "small" else "18px",
                            backgroundColor: "transparent"
                        }
                    },
                    **{
                        f"{_color}": {
                            color: getattr(theme.palette, _color).main,
                            # p: theme.spacing,
                            p: '0px',
                            borderRadius: "15px" if ownerState.get("size") == "small" else "18px",
                            backgroundColor: "transparent"
                        }
                        for _color in COLORS
                    }
                },
                "icon": {
                    color: theme.palette.text.disabled
                },
                "checkedIndicator": {
                    borderWidth: 1,
                    borderRadius: 3,
                    p: 8,
                }
            }
        },
    }
