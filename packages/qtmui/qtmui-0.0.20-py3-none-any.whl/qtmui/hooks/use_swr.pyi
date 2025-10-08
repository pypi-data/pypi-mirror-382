import sys
import json
import traceback
from qtpy.QtCore import QObject, QRunnable, Signal, Slot
from qtpy.QtCore import QObject, Signal, Slot
from qtmui.hooks.use_state import useState
class Signals:
class useSWR:
    def __init__(self, fn, *args, **kwargs): ...
    def run(self): ...