from typing import Dict, List
from qtmui.material.styles.create_theme.theme_reducer import ThemeState
from qtmui.material.styles.create_theme.utils.alpha import alpha  # Giả định alpha đã được định nghĩa

# Định nghĩa các màu sắc
COLORS = ["primary", "secondary", "info", "success", "warning", "error"]

def pagination(theme: ThemeState) -> Dict:
    light_mode = theme.palette.mode == 'light'

    def rootStyles(owner_state: Dict) -> List[Dict]:
        default_color = owner_state.get("color") == "standard"
        filled_variant = owner_state.get("variant") == "text"
        outlined_variant = owner_state.get("variant") == "outlined"
        soft_variant = owner_state.get("variant") == "soft"

        default_style = {
            f"& .{paginationItemClasses.root}": {
                **({"borderColor": alpha(theme.palette.grey[500], 0.24)} if outlined_variant else {}),
                f"&.{paginationItemClasses.selected}": {
                    "fontWeight": theme.typography.fontWeightSemiBold,
                    **({"borderColor": "currentColor"} if outlined_variant else {}),
                    **({
                        "backgroundColor": alpha(theme.palette.grey[500], 0.08),
                        **({
                            "color": theme.palette.common.white if light_mode else theme.palette.grey[800],
                            "backgroundColor": theme.palette.text.primary,
                            "&:hover": {
                                "backgroundColor": theme.palette.grey[700] if light_mode else theme.palette.grey[100],
                            },
                        } if filled_variant else {})
                    } if default_color else {}),
                },
            },
        }

        color_style = [
            {
                **({
                    f"& .{paginationItemClasses.root}": {
                        f"&.{paginationItemClasses.selected}": {
                            **({
                                # SOFT Variant Styles
                                "color": theme.palette[color]["dark" if light_mode else "light"],
                                "backgroundColor": alpha(theme.palette[color].main, 0.08),
                                "&:hover": {
                                    "backgroundColor": alpha(theme.palette[color].main, 0.16),
                                },
                            } if soft_variant else {})
                        }
                    }
                } if owner_state.get("color") == color else {})
            }
            for color in COLORS
        ]

        return [default_style, *color_style]

    return {
        "PyPagination": {
            "styleOverrides": {
                "root": lambda owner_state: rootStyles(owner_state)
            }
        }
    }
