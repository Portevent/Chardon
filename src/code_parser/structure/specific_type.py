"""
Specific Type
"""

from src.code_parser.structure.type import Type


# pylint: disable=too-few-public-methods
class SpecificType(Type):
    """
    Specific Types (often written as MyType<TypeA> in commons languages)
    """

    def __init__(self, type_: Type, specific1: Type, specific2: Type = None,
                 attributes: dict = None):
        super().__init__(type_.name, attributes)
        self.type_ = type_
        self.specific1 = specific1
        self.specific2 = specific2
