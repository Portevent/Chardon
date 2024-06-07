"""
Parameter
"""
from code_parser.structure.type import Type


# pylint: disable=too-few-public-methods
class Parameter:
    """
    Store Function parameters
    """

    def __init__(self, name: str, _type: Type | str, comment: str = "",
                 default_value=None, attributes: dict = None):
        """
        Init a Parameter
        @param name: name
        @param _type: Type, can be string if Class or Type is not yet documented
        @param comment: Comment linked to this parameter
        @param default_value: Has a default value
        @param attributes: custom attributes
        """
        self.name = name
        self.type = _type
        self.comment = comment
        self.default_value = default_value
        self.attributes = attributes or {}

    def __str__(self) -> str:
        return self.name
