from ....system.color_manipulator import alpha
from .properties_name import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState


COLORS = ['primary', 'secondary', 'info', 'success', 'warning', 'error']

def button_group(_theme):
    theme: ThemeState = _theme
    
    VARIANTS = ["contained", "outlined", "text", "soft"]


        # default_style = {
        #     f"& .{buttonGroupClasses.grouped}": {
        #         '&:not(:last-of-type)': {
        #             **({
        #                 'borderStyle': 'solid',
        #                 **({
        #                     borderColor: alpha(theme.palette.grey._500, 0.32),
        #                 } if inherit_color else {}),
        #                 **({
        #                     'borderWidth': '0px 1px 0px 0px',
        #                 } if horizontal_orientation else {}),
        #                 **({
        #                     'borderWidth': '0px 0px 1px 0px',
        #                 } if vertical_orientation else {}),
        #             } if not outlined_variant else {}),
        #         },
        #     },
        # }

        # color_styles = [
        #     {
        #         f"& .{buttonGroupClasses.grouped}": {
        #             '&:not(:last-of-type)': {
        #                 **({
        #                     **({
        #                         borderColor: alpha(getattr(theme.palette, color).dark, 0.48),
        #                     } if contained_variant else {}),
        #                     **({
        #                         borderColor: alpha(getattr(theme.palette, color).main, 0.48),
        #                     } if text_variant else {}),
        #                     **({
        #                         borderColor: alpha(getattr(theme.palette, color).dark, 0.24),
        #                     } if soft_variant else {}),
        #                 } if owner_state.get('color') == color else {}),
        #             },
        #         },
        #     } for color in COLORS
        # ]

        # disabled_state = {
        #     f"& .{buttonGroupClasses.grouped}": {
        #         f"&.{buttonGroupClasses.disabled}": {
        #             '&:not(:last-of-type)': {
        #                 borderColor: theme.palette.action.disabledBackground,
        #             },
        #         },
        #     },
        # }


    return {
        'PyButtonGroup': {
            'styles': {
                'root': {
                        f"{variant}": {
                            "first": {
                                borderRadius: '0px',
                                "orientation": {
                                    "vertical": {
                                        borderTopLeftRadius: "4px",
                                        borderTopRightRadius: "4px",
                                        borderWidth: "0px 0px 1px 0px"
                                    },
                                    "horizontal": {
                                        borderTopLeftRadius: "4px",
                                        borderBottomLeftRadius: "4px",
                                        borderWidth: "0px 1px 0px 0px"
                                    },
                                },
                                "borderColorDefault": theme.palette.grey._500,
                                "borderColorRender": lambda color, _variant=variant: 
                                getattr(theme.palette, color).dark if _variant == "contained" 
                                else  alpha(getattr(theme.palette, color).main, 0.48) if _variant == "text" 
                                else  alpha(getattr(theme.palette, color).main, 0.24) if _variant == "soft" 
                                else None
                            },
                            "middle": {
                                borderRadius: '0px',
                                "orientation": {
                                    "vertical": {
                                        borderWidth: "0px 0px 1px 0px"
                                    },
                                    "horizontal": {
                                        borderWidth: "0px 1px 0px 0px"
                                    },
                                },
                            },
                            "last": {
                                borderRadius: '0px',
                                borderWidth: "0px",
                                "orientation": {
                                    "vertical": {
                                        borderBottomLeftRadius: "4px",
                                        borderBottomRightRadius: "4px",
                                    },
                                    "horizontal": {
                                        borderTopRightRadius: "4px",
                                        borderBottomRightRadius: "4px",
                                    },
                                },
                            },
                        }
                        for variant in VARIANTS
                    }
            },
        },
    }
