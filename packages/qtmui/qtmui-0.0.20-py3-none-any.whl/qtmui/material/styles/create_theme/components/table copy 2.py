from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from qtmui.material.styles.create_theme.theme_reducer import ThemeState

from .properties_name import *
from ....system.color_manipulator import alpha


def table(_theme) -> Dict:
    theme: ThemeState = _theme
    lightMode = theme.palette.mode == 'light'

    return {
        "PyTableWidget": {
            "styles": {
                "root": f"""
                    QTableView {{
                        background-color: {theme.palette.background.paper};
                        padding: 0px;
                        border: none;
                        gridline-color: transparent;
                        color: {theme.palette.text.secondary};
                    }}

                    QTableView::item {{
                        padding-left: 0px;
                        padding-right: 5px;
                    }}

                    QTableView::item:selected {{
                        background-color: {alpha(theme.palette.primary.dark, 0.04)};
                    }}

                    QTableView::item:hover {{
                        background-color: {alpha(theme.palette.primary.dark, 0.08)};
                    }}

                    QTableView::section {{
                        background-color: transparent;
                        max-width: 30px;
                        text-align: left;
                    }}

                    QTableView::horizontalHeader {{
                        background-color: red;

                    }}

                    QTableView::section:horizontal {{
                        background-color: transparent;
                        padding: 0px;
                        border: 1px solid red !important;
                        border-bottom: 1px solid red !important;
                    }}


                    QTableView::section:vertical {{
                        border: 1px solid red;
                    }}

                    QTableView .QScrollBar:horizontal {{
                        border: none;
                        background: {theme.palette.grey._500};
                        min-height: 8px;
                        border-radius: 0px;
                        max-width: 79em;
                    }}

                    QTableView .QHeaderView::section {{
                        background-color: transparent!important;
                    }}
                """,
                "lineEdit": f"""
                    LineEdit, TextEdit, PlainTextEdit, TextBrowser {{
                        background-color: rgba(255, 255, 255, 0.0605);
                        border: 1px solid rgba(255, 255, 255, 0.08);
                        border-bottom: 1px solid rgba(255, 255, 255, 0.5442);
                        border-radius: 5px;
                        /* font: 14px "Segoe UI", "Microsoft YaHei"; */
                        padding: 0px 10px;
                        color: white;
                        selection-background-color: --ThemeColorPrimary;
                        selection-color: black;
                    }}

                    TextEdit, PlainTextEdit, TextBrowser  {{
                        padding: 2px 3px 2px 8px;
                    }}

                    LineEdit:hover, TextEdit:hover, PlainTextEdit:hover, TextBrowser:hover {{
                        background: rgba(255, 255, 255, 0.0837);
                    }}

                    LineEdit:focus[transparent=true] {{
                        background: rgba(30, 30, 30, 0.7);
                        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                    }}

                    LineEdit[transparent=false]:focus {{
                        background: rgb(31, 31, 31);
                    }}

                    TextEdit:focus, PlainTextEdit:focus, TextBrowser:focus {{
                        border-bottom: 1px solid --ThemeColorPrimary;
                        background-color: rgba(30, 30, 30, 0.7);
                    }}

                    LineEdit:disabled, TextEdit:disabled, PlainTextEdit:disabled, TextBrowser:disabled {{
                        color: rgba(255, 255, 255, 92);
                        background-color: rgba(255, 255, 255, 0.0419);
                        border: 1px solid rgba(255, 255, 255, 0.0698);
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
            "styles1": f"""
                QTableView {{
                    background: transparent;
                    outline: none;
                    border: none;
                    /* font: 13px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
                    selection-background-color: transparent;
                    alternate-background-color: transparent;
                }}

                QTableView[isBorderVisible=true] {{
                    border: 1px solid rgba(255, 255, 255, 21);
                }}

                QTableView::item {{
                    background: transparent;
                    border: 0px;
                    padding-left: 16px;
                    padding-right: 16px;
                    height: 35px;
                }}

                QTableView::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 5px;
                    border: none;
                    background-color: transparent;
                }}


                QHeaderView {{
                    background-color: transparent;
                }}

                QHeaderView::section {{
                    background-color: transparent;
                    color: rgb(203, 203, 203);
                    padding-left: 5px;
                    padding-right: 5px;
                    border: 1px solid rgba(255, 255, 255, 21);
                    font: 13px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC';
                }}

                QHeaderView::section:horizontal {{
                    border-left: none;
                    height: 33px;
                }}

                QTableView[isBorderVisible=true] QHeaderView::section:horizontal {{
                    border-top: none;
                }}

                QHeaderView::section:horizontal:last {{
                    border-right: none;
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
                    image: url(:/qfluentwidgets/images/table_view/Down_white.svg);
                }}

                QHeaderView::up-arrow {{
                    subcontrol-origin: padding;
                    subcontrol-position: center right;
                    margin-right: 6px;
                    image: url(:/qfluentwidgets/images/table_view/Up_white.svg);
                }}

                QTableCornerButton::section {{
                    background-color: transparent;
                    border: 1px solid rgba(255, 255, 255, 21);
                }}

                QTableCornerButton::section:pressed {{
                    background-color: rgba(255, 255, 255, 16);
                }}
            """,
        },
    }
