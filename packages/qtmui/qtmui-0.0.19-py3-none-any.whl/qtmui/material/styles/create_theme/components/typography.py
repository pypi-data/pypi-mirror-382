from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def typography(_theme) -> Dict:
    theme: ThemeState = _theme

    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    return {
        'PyTypography': {
            'styles': {
                "root": {
                    **{
                        "textPrimary": {
                            'color': theme.palette.text.primary,
                        },
                        "textSecondary": {
                            'color': theme.palette.text.secondary,
                        },
                        "textDisabled": {
                            'color': theme.palette.text.disabled,
                        },
                    },
                    **{
                        f"{_color}": {
                            'color': getattr(theme.palette, _color).main,
                        }
                        for _color in COLORS
                    }
                },
                "paragraph": {
                    marginBottom: theme.spacing(2),
                },
                "gutterBottom": {
                    marginBottom: theme.spacing(1),
                },
            },
        },
    }
