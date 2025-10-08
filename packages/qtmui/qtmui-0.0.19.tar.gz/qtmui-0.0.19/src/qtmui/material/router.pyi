from functools import lru_cache
import time
from qtpy.QtWidgets import QStackedWidget, QPushButton
from qtpy.QtCore import Signal
from qtmui.material import Iconify, Box, LoadingDialog, Skeleton
from qtmui.hooks.use_routes import useRouter
from src.sections._examples.foundation.grid_view import GridView
from src.sections._examples.foundation.colors_view import ColorsView
from src.sections._examples.foundation.typography_view import TypographyView
from src.sections._examples.foundation.shadows_view import ShadowsView
from src.sections._examples.mui.textfield_view import TextFieldView
from src.sections._examples.mui.button_view.index import ButtonsView
from src.sections._examples.mui.accordion_view import AccordionView
from src.sections._examples.mui.breadcrumbs_view import BreadcrumbsView
from src.sections._examples.mui.data_grid_view.index import DataGridView
from src.sections._examples.mui.textfield_view import TextFieldView
from src.sections._examples.mui.autocomplete_view import AutocompleteView
from src.sections._examples.mui.radio_button_view import RadioButtonView
from src.sections._examples.mui.checkbox_view import CheckboxView
from src.sections._examples.mui.switch_view import SwitchView
from src.sections._examples.mui.alert_view import AlertView
from src.sections._examples.mui.chip_view import ChipView
from src.sections._examples.mui.avatar_view import AvatarView
from src.sections._examples.mui.badge_view import BadgeView
from src.sections._examples.mui.skeleton_view import SkeletonView
from src.sections._examples.mui.progress_view import ProgressView
from src.sections._examples.mui.tabs_view import TabsView
from src.sections._examples.mui.table_view.index import BasicTableView
from src.sections._examples.mui.rating_view import RatingView
from src.sections._examples.mui.dialog_view import DialogView
from src.sections._examples.extra.snackbar_view import SnackbarView
from src.sections._examples.extra.navigation_bar_view import NavigationBarView
from src.sections._examples.extra.upload_view import UploadView
class Router:
    def __init__(self): ...
    def resizeEvent(self, e): ...
    def initUI(self): ...
    def handle_path(self, path): ...
    def render(self, path): ...
    def add_widget(self, path, _route): ...
    def start_render(self, path): ...
    def _render(self, path): ...
    def clear_layout(self): ...
    def get_route(self, path): ...