from dataclasses import dataclass
from typing import Optional


@dataclass
class PaletteColor:
    root: Optional[str] = ''
    rounded: Optional[str] = ''
    expanded: str = ""
    disabled: Optional[str] = ''
    gutters: Optional[str] = ''
    region: Optional[str] = ''