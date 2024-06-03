import logging
from enum import Enum


class LinkPreset(Enum):
    LINE = 1
    ARROW = 2
    ARROW_FROM = 3
    DOUBLE_ARROW = 4
    DASHED_ARROW = 5


class ArrowType(Enum):
    NONE = 1
    ARROW = 2
    DIAMOND = 3

    def __json__(self):
        return self.__str__()


class LineType(Enum):
    NONE = 1
    SOLID = 2
    DASHED = 3

    def __json__(self):
        return self.__str__()


class Link:
    """
    Define a Link between two object
    Positional parameters :
        - objectA, objectB : Object to be linked
    Optional keywords :
        - name : the label to display on the link
        - linkPreset : LinkPreset enum to preset values (will be overriden by other keywords)
        - arrow_from, arrow_to : ArrowType to use to display
        - line_type : LineType to use to display
    """

    def __init__(self, objectA, objectB, label="", labelA="", labelB="", linkPreset=None,
                 arrow_from=None,
                 arrow_to=None,
                 line_type=None,
                 active=True):
        match linkPreset:
            case LinkPreset.LINE:
                self.line_type = LineType.SOLID
                self.arrow_from = ArrowType.NONE
                self.arrow_to = ArrowType.NONE

            case LinkPreset.ARROW:
                self.line_type = LineType.SOLID
                self.arrow_from = ArrowType.NONE
                self.arrow_to = ArrowType.ARROW

            case LinkPreset.DASHED_ARROW:
                self.line_type = LineType.DASHED
                self.arrow_from = ArrowType.NONE
                self.arrow_to = ArrowType.ARROW

            case LinkPreset.DOUBLE_ARROW:
                self.line_type = LineType.SOLID
                self.arrow_from = ArrowType.ARROW
                self.arrow_to = ArrowType.ARROW

        self.objectA = objectA
        self.objectB = objectB
        self.label = label
        self.labelA = labelA
        self.labelB = labelB
        self.arrow_from = arrow_from or self.arrow_from
        self.arrow_to = arrow_to or self.arrow_to
        self.line_type = line_type or self.line_type
        self.active = active

    def __json__(self, **options):
        return {
            'objectA': self.objectA,
            'objectB': self.objectB,
            'label': self.label,
            'labelA': self.labelA,
            'labelB': self.labelB,
            'arrow_from': self.arrow_from,
            'arrow_to': self.arrow_to,
            'line_type': self.line_type,
        }
