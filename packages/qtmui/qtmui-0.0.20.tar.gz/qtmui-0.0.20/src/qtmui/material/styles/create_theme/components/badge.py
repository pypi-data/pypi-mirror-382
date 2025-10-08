from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from ....system.color_manipulator import alpha
from .properties_name import *

class RadioStyle:
    MuiFormControlLabel: str = "" 
    MuiRadio: str = "" 



def badge(_theme) -> Dict:
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

        'PyBadge': {
            'styles': {
                'root': lambda ownerState: {
                    **{
                        "default": {
                            backgroundColor: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            color: theme.palette.common.white if lightMode else theme.palette.grey._800,
                            "props": {
                                "onlineVariant": {
                                    color: theme.palette.success.main,
                                },
                                "busyVariant": {
                                    color: theme.palette.error.main,
                                },
                                "offlineVariant": {
                                    color: theme.palette.text.disabled,
                                },
                                "alwayVariant": {
                                    color: theme.palette.warning.main,
                                },
                                "invisibleVariant": {
                                    color: "transparent",
                                },
                                "hasIcon": {
                                    borderRadius: ownerState.get("size")/2
                                },
                                "hasText": {
                                    color: theme.palette.common.white if not lightMode else theme.palette.grey._900,
                                    fontWeight: theme.typography.button.fontWeight,
                                    lineHeight: theme.typography.button.lineHeight,
                                    fontSize: theme.typography.button.fontSize,
                                },
                            },
                        },
                        "inherit": {
                            backgroundColor: theme.palette.grey._800 if lightMode else theme.palette.common.white,
                            color: theme.palette.common.white if lightMode else theme.palette.grey._900,
                            "props": {
                                "onlineVariant": {
                                    color: theme.palette.success.main,
                                },
                                "busyVariant": {
                                    color: theme.palette.error.main,
                                },
                                "offlineVariant": {
                                    color: theme.palette.text.disabled,
                                },
                                "alwayVariant": {
                                    color: theme.palette.warning.main,
                                },
                                "invisibleVariant": {
                                    color: "transparent",
                                },
                                "hasIcon": {
                                    borderRadius: ownerState.get("size")/2
                                },
                                "hasText": {
                                    color: theme.palette.common.white if not lightMode else theme.palette.grey._900,
                                    fontWeight: theme.typography.button.fontWeight,
                                    lineHeight: theme.typography.button.lineHeight,
                                    fontSize: theme.typography.button.fontSize,
                                },
                            },
                        },
                    },
                    **{
                        f"{_color}": {
                            backgroundColor: getattr(theme.palette, _color).main,
                            color: getattr(theme.palette, _color).contrastText,
                            "props": {
                                "onlineVariant": {
                                    color: theme.palette.success.main,
                                },
                                "busyVariant": {
                                    color: theme.palette.error.main,
                                },
                                "offlineVariant": {
                                    color: theme.palette.text.disabled,
                                },
                                "alwayVariant": {
                                    color: theme.palette.warning.main,
                                },
                                "invisibleVariant": {
                                    color: "transparent",
                                },
                                "hasIcon": {
                                    borderRadius: ownerState.get("size")/2
                                },
                                "hasText": {
                                    color: theme.palette.common.white if not lightMode else theme.palette.grey._900,
                                    fontWeight: theme.typography.button.fontWeight,
                                    lineHeight: theme.typography.button.lineHeight,
                                    fontSize: theme.typography.button.fontSize,
                                },
                            },
                        }
                        for _color in COLORS
                    }
                }
            }
        },

    }
