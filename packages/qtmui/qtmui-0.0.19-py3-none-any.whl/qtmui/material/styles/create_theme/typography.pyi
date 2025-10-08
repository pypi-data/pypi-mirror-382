from dataclasses import dataclass
class TypographyType:
    fontWeight: int
    lineHeight: float
    fontSize: str
    responsiveSizes: dict
    textTransform: str
class TypographyStyle:
    def __init__(self, fontWeight, lineHeight, fontSize, responsiveSizes, textTransform): ...
    def __repr__(self): ...
    def to_qss_props(self): ...
class Typography:
    h1: TypographyType
    h2: TypographyType
    h3: TypographyType
    h4: TypographyType
    h5: TypographyType
    h6: TypographyType
    subtitle1: TypographyType
    subtitle2: TypographyType
    body1: TypographyType
    body2: TypographyType
    caption: TypographyType
    overline: TypographyType
    button: TypographyType
    def __init__(self): ...
    def int_to_px(value: int): ...
    def px_to_rem(value: int): ...
    def responsive_font_sizes(self, sm: int, md: int, lg: int): ...