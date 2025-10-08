from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from ....system.color_manipulator import alpha
from .properties_name import *

def breadcrumbs(_theme):
    theme: ThemeState = _theme
    
    return {
        'PyBreadcrumbs': {
            'styles': {
                'root': {
                    color: theme.palette.text.secondary,
                    fontSize: theme.typography.button.fontSize,
                    fontWeight: theme.typography.button.fontWeight,
                    lineHeight: theme.typography.button.lineHeight
                },
                'separator': {
                    marginLeft: theme.spacing(2),
                    marginRight: theme.spacing(2),
                },
                'li': {
                    'display': 'inline-flex',
                    m: theme.spacing(0.25, 0),
                },
            },
        },
    }
