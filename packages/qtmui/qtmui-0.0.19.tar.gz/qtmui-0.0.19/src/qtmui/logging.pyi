import logging
import os
from typing import Optional
from dotenv import load_dotenv
def get_logger(name: str): ...
class LogType:
def print_log(code: str, message: str, log_type: str, detail_message: Optional[str]): ...