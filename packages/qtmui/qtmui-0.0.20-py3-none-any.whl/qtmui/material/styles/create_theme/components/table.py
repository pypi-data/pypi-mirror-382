from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha
from .....qtmui_assets import QTMUI_ASSETS


def table(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == 'light'

    return {
        "PyTableWidget": {
            "styles": {
                "root": f"""
                    QTableView {{
                        background: transparent;
                        outline: none;
                        /* border: none; */
                        border-radius: 8px;
                        /* font: 13px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
                        selection-background-color: transparent;
                        alternate-background-color: transparent;
                        color: {theme.palette.text.secondary};
                        font-size: {theme.typography.body2.fontSize};
                        font-weight: {theme.typography.body2.fontWeight};
                        line-height: {theme.typography.body2.lineHeight};
                    }}

                    QTableView[isBorderVisible=true] {{
                        border: 1px solid {alpha(theme.palette.grey._500, 0.24)};
                    }}

                    QTableView[isBorderVisible=true] QHeaderView::section {{
                        border: 1px solid {alpha(theme.palette.grey._500, 0.24)};
                    }}

                    QTableView::item {{
                        background: transparent;
                        border: 0px;
                        padding-left: 16px;
                        padding-right: 16px;
                        height: 35px;
                        color: {theme.palette.text.secondary};
                    }}

                    QTableView::indicator {{
                        width: 18px;
                        height: 18px;
                        border-radius: 5px;
                        border: none;
                        background-color: transparent;
                    }}

                    QHeaderView {{
                        background-color: {theme.palette.background.content};
                        color: {theme.palette.text.primary};
                    }}

                    QHeaderView::section {{
                        background-color: transparent;
                        color: {theme.palette.text.disabled};
                        padding-left: 5px;
                        padding-right: 5px;
                        font-size: {theme.typography.button.fontSize};
                        font-weight: {theme.typography.button.fontWeight};
                        line-height: {theme.typography.button.lineHeight};
                    }}

                    QHeaderView::section:horizontal {{
                        border-left: none;
                        height: 50px;
                    }}

                    QTableView[isBorderVisible=true] QHeaderView::section:horizontal {{
                        border-top: none;
                    }}

                    QHeaderView::section:horizontal:last {{
                        border-right: none;
                    }}

                    QHeaderView::section:horizontal:first {{
                        padding-left: 50px;
                    }}

                    QHeaderView::section:vertical {{
                        border-top: none;
                    }}

                    QHeaderView::section:checked {{
                        background-color: transparent;
                    }}

                    QHeaderView::down-arrow {{
                        subcontrol-origin: padding;
                        subcontrol-position: center right;
                        margin-right: 6px;
                        image: url({QTMUI_ASSETS.ICONS.ARROW_DROP_DOWN});
                    }}

                    QHeaderView::up-arrow {{
                        subcontrol-origin: padding;
                        subcontrol-position: center right;
                        margin-right: 6px;
                        image: url({QTMUI_ASSETS.ICONS.ARROW_DROP_UP});
                    }}

                    QTableCornerButton::section {{
                        background-color: transparent;
                        border: 1px solid {alpha(theme.palette.grey._500, 0.24)};
                    }}

                    QTableCornerButton::section:pressed {{
                        background-color: {alpha(theme.palette.grey._500, 0.12)};
                    }}

                    QTableWidgetItem {{
                        background-color: {theme.palette.text.secondary};
                        color: {theme.palette.text.secondary};
                    }}
                """,
                "lineEdit": f"""
                    LineEdit, TextEdit, PlainTextEdit, TextBrowser {{
                        background-color: {theme.palette.common.white if lightMode else theme.palette.common.black};
                        border: 1px solid {alpha(theme.palette.common.white, 0.08) if lightMode else alpha(theme.palette.common.black, 0.08)};
                        border-bottom: 1px solid {theme.palette.primary.main};
                        border-radius: 5px;
                        /* font: 14px "Segoe UI", "Microsoft YaHei"; */
                        padding: 0px 10px;
                        color: {theme.palette.common.black if lightMode else theme.palette.common.white};
                        selection-background-color: {theme.palette.primary.main};
                        selection-color: white;
                    }}

                    TextEdit, PlainTextEdit, TextBrowser  {{
                        padding: 2px 3px 2px 8px;
                    }}

                    LineEdit:hover, TextEdit:hover, PlainTextEdit:hover, TextBrowser:hover {{
                        background: {theme.palette.common.white if lightMode else theme.palette.common.black};
                    }}

                    LineEdit:focus[transparent=true] {{
                        background: {theme.palette.common.white if lightMode else  theme.palette.common.black};
                        border-bottom: 1px solid {theme.palette.common.white if lightMode else theme.palette.common.black};
                    }}

                    LineEdit[transparent=false]:focus {{
                        background: {theme.palette.common.white if lightMode else  theme.palette.common.black};
                    }}

                    TextEdit:focus, PlainTextEdit:focus, TextBrowser:focus {{
                        border-bottom: 1px solid {theme.palette.primary.main};
                        background-color: {theme.palette.common.white if lightMode else theme.palette.common.black};

                    }}

                    LineEdit:disabled, TextEdit:disabled, PlainTextEdit:disabled, TextBrowser:disabled {{
                        color: rgba(255, 255, 255, 92);
                        background-color: {theme.palette.action.disabled};
                        border: 1px solid {alpha(theme.palette.action.disabled, 0.04)};
                    }}

                    #lineEditButton {{
                        background-color: transparent;
                        border-radius: 4px;
                        margin: 0;
                    }}

                    #lineEditButton:hover {{
                        background-color: rgba(255, 255, 255, 9);
                    }}

                    #lineEditButton:pressed {{
                        background-color: rgba(255, 255, 255, 6);
                    }}

                """
            },
           
        },
    }
