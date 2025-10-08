from src.components.system.color_manipulator import alpha
from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from .properties_name import *

# from ....css import paper, menuItem
from .paper import paper

def autocomplete(_theme):
    theme: ThemeState = _theme
    theme_palette = theme.palette

    return {
        'PyAutocomplete': {
            'styles': {
                'root': {

                    },
                },
                'tag': {
                    **theme.typography.subtitle2,
                    height: 24,
                    minWidth: 24,
                    lineHeight: '24px',
                    textAlign: 'center',
                    p: theme.spacing(0, 0.75),
                    color: theme_palette.text.secondary,
                    borderRadius: theme.shape.borderRadius,
                    backgroundColor: alpha(theme_palette.grey._500, 0.16),
                },
                'paper': paper({'theme': theme, 'dropdown': True}),
                'listbox': {
                    p: "0px",
                    'option': {
                        # {menuItem(theme)},
                    }
                },
                'endAdornment': {
                    "Iconify": {
                        width: 18,
                        height: 18,
                    },
                },
            }
        }
