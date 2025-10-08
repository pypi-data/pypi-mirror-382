import sys
from qtpy.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QLabel
from qtpy.QtCore import QDate

class Calendar(QWidget):
    def __init__(self):
        super().__init__()

        self._init_ui()

    def _init_ui(self):
        self.setLayout(QVBoxLayout())

        # Tạo Calendar Widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)  # Hiển thị lưới

        self.layout().addWidget(self.calendar)

