"""
Specific Type
"""

from src.code_parser.structure.type import Type


# pylint: disable=too-few-public-methods
class SpecificType(Type):
    """
    Specific Types (often written as MyType<TypeA> in commons languages)
    """

    def __init__(self, _type: Type, specific1: Type, specific2: Type = None,
                 attributes: dict = None):
        super().__init__(_type.name, attributes)
        self._type = _type
        self.specific1 = specific1
        self.specific2 = specific2
