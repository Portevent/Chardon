"""
Parameter
"""
from typing import List


# pylint: disable=too-few-public-methods
from chardon.code_parser.structure import Type


class Parameter:
    """
    Store Function parameters
    """

    # pylint: disable=too-many-arguments
    def __init__(self, name: str, types: List[Type], comment: str = "",
                 default_value=None, attributes: dict = None):
        """
        Init a Parameter
        @param name: name
        @param types: Any possible Type this param can be
        @param comment: Comment linked to this parameter
        @param default_value: Has a default value
        @param attributes: custom attributes
        """
        self.name = name
        self.types = types
        self.comment = comment
        self.default_value = default_value
        self.attributes = attributes or {}

    def __str__(self) -> str:
        return self.name
