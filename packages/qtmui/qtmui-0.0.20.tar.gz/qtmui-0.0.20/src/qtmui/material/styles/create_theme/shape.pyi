from dataclasses import dataclass, field
from typing import Optional
class ShapeOptions:
    borderRadius: Optional[float]
class Shape:
    borderRadius: int
def createShape(options: Optional[ShapeOptions]): ...