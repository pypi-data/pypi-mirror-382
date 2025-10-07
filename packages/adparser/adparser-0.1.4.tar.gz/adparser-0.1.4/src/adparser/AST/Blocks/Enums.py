from enum import Enum


class BlockType(Enum):
    TextLine = 1
    Link = 2
    Paragraph = 3
    Heading = 4
    List = 5
    Source = 6
    Table = 7
    Admonition = 8
    Audio = 9
    Video = 10
    Image = 11


class TextLineStyle(Enum):
    pass


class ParagraphStyle(Enum):
    pass


class AdmonitionStyle(Enum):
    Note = 1
    Tip = 2
    Important = 3
    Warning = 4
    Caution = 5
