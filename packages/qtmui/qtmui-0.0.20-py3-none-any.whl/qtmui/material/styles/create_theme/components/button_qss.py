from typing import TYPE_CHECKING, Optional

from ....system.color_manipulator import alpha

from .properties_name import *


if TYPE_CHECKING:
    from ..theme_reducer import ThemeState


def button(_theme):
    theme: ThemeState = _theme

    VARIANTS = ['contained', 'outlined', 'text', 'soft']
    SIZES = ['small', 'medium', 'large']
    COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

    lightMode = theme.palette.mode == 'light'

    return {
        'PyButtonContained': {
            'styles': f'''

                {
                    "\n".join(
                    f"""
                    #PyButtonContained[p-color="{color}"] {{
                        border: 1px solid transparent;
                        border-color: 1px solid transparent;
                        border-radius: 4px;
                        color: {theme.palette.common.white if lightMode else theme.palette.grey._800};
                        background-color: {getattr(theme.palette, color).main};
                    }}
                    """ for color in COLORS)
                }

                {
                    "\n".join(
                    f"""
                    #PyButtonContained[p-size="{size}"] {{
                        min-height: {30 if size == "small" else 36 if size == "medium" else 48}px;
                        max-height: {30 if size == "small" else 36 if size == "medium" else 48}px;
                        padding-left: {8 if size == "small" else 12 if size == "medium" else 16}px;
                        padding-right: {8 if size == "small" else 12 if size == "medium" else 16}px;
                    }}

                    """ for size in SIZES)
                }

                {
                    "\n".join(
                    f"""
                    #PyButtonContained[p-variant="{variant}"] {{
                        {"border-color: transparent;" if variant != "outlined" else ""}
                        {"background-color: transparent;" if variant == "text" else ""}
                    }}

                    """ for variant in VARIANTS)
                }

                {
                    "\n".join(
                    f"""
                    #ContentLabel[p-color="{color}"] {{
                        color: {theme.palette.grey._500 if color == "default" else getattr(theme.palette, color).contrastText};
                    }}
                    """ for color in COLORS)
                }

                {
                    "\n".join(
                    f"""
                    #ContentLabel[p-size="{size}"] {{
                        font-size: {13 if size == "small" else 14 if size == "medium" else 15}px;
                        font-weight: {theme.typography.button.fontWeight};
                        line-height: {theme.typography.button.lineHeight};
                    }}
                    """ for size in SIZES)
                }

                #StartIcon, #EndIcon {{
                    background-color: transparent;
                    border-radius: 5px;
                }}

            ''',

        },
    }
