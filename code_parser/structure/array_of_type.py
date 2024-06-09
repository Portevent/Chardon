"""
Array of Type
"""


# pylint: disable=too-few-public-methods
from code_parser.structure.type import Type


class ArrayOfType(Type):
    """
    Array of Type (often written as Object[], List[Object], List<Object> in commons languages)
    """

    def __init__(self, type_: Type, attributes: dict = None):
        super().__init__(type_.name, attributes)
        self.type_ = type_
