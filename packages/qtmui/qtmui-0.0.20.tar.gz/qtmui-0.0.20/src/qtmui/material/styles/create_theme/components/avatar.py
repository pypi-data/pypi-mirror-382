from typing import TYPE_CHECKING
from ....system.color_manipulator import alpha

if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState


from .properties_name import *

COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

def color_by_name(name: str) -> str:
    char_at = name[0].lower()
    if char_at in ['a', 'c', 'f']:
        return 'primary'
    elif char_at in ['e', 'd', 'h']:
        return 'secondary'
    elif char_at in ['i', 'k', 'l']:
        return 'info'
    elif char_at in ['m', 'n', 'p']:
        return 'success'
    elif char_at in ['q', 's', 't']:
        return 'warning'
    elif char_at in ['v', 'x', 'y']:
        return 'error'
    return 'default'

def avatar(_theme):
    theme: ThemeState = _theme
    theme_palette = theme.palette

    return {
        'PyAvatar': {
            'styles': {
                'root': lambda ownerState: {
                    **{
                        _color: {
                            color: getattr(theme.palette, _color).contrastText,
                            fontSize: theme.typography.button.fontSize,
                            lineHeight: theme.typography.button.lineHeight,
                            fontWeight: theme.typography.button.fontWeight,
                            "props": {
                                "circularVariant": {
                                    borderRadius: int(ownerState.get("size")/2),
                                },
                                "roundedVariant": {
                                    borderRadius: int(theme.shape.borderRadius * 1.5)
                                },
                                "squareVariant": {
                                    borderRadius: "0px"
                                },
                                "hasIcon": {
                                    backgroundColor: getattr(theme.palette, _color).main,
                                    borderRadius: ownerState.get("size")/2
                                },
                            },
                        } 
                        for _color in COLORS
                    },
                    **{
                        "default": {
                            color: theme_palette.text.secondary,
                            fontSize: theme.typography.button.fontSize,
                            lineHeight: theme.typography.button.lineHeight,
                            fontWeight: theme.typography.button.fontWeight,
                            "props": {
                                "circularVariant": {
                                    borderRadius: int(ownerState.get("size")/2),
                                },
                                "roundedVariant": {
                                    borderRadius: int(theme.shape.borderRadius * 1.5)
                                },
                                "squareVariant": {
                                    borderRadius: "0px"
                                },
                                "hasIcon": {
                                    backgroundColor: alpha(theme_palette.grey._500, 0.24),
                                    borderRadius: ownerState.get("size")/2
                                },
                            },
                        },

                    }
                },
            },
        },

        'PyAvatarGroup': {
            'styles': {
                'root': lambda ownerState: {
                    'justifyContent': 'flex-end',
                    **({
                        width: 40,
                        height: 40,
                        'position': 'relative',
                        "avatar": {
                            m: 0,
                            width: 28,
                            height: 28,
                            'position': 'absolute',
                            'first-of-type': {
                                'left': 0,
                                'bottom': 0,
                                'zIndex': 9,
                            },
                            'last-of-type': {
                                'top': 0,
                                'right': 0,
                            },
                        }
                    } if ownerState.get('variant') == 'compact' else {}),
                },
                'avatar': {
                    fontSize: 16,
                    'fontWeight': theme.typography.fontWeightSemiBold,
                    '&:first-of-type': {
                        fontSize: 12,
                        'color': theme_palette.primary.dark,
                        backgroundColor: theme_palette.primary.lighter,
                    },
                },
            },
        },
    }
