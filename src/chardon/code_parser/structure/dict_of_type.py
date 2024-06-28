"""
Dict of Type
"""


# pylint: disable=too-few-public-methods
from chardon.code_parser.structure.type import Type


class DictOfType(Type):
    """
    Dict of Types (often written as {typeA: typeB}, dict[A:B], Dictionary<A:B> in commons languages)
    """

    def __init__(self, key: Type, value: Type, attributes: dict = None):
        super().__init__(key.name, attributes)
        self.key = key
        self.value = value
