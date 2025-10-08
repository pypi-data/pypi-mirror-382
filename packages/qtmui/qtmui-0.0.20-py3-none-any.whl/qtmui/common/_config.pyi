import sys
from enum import Enum
from qtpy.QtCore import QLocale
from ..material.qfluentwidgets import qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, OptionsValidator, RangeConfigItem, RangeValidator, FolderListValidator, Theme, FolderValidator, ConfigSerializer, __version__
class Language:
class LanguageSerializer:
    def serialize(self, language): ...
    def deserialize(self, value: str): ...
def isWin11(): ...
class Config: