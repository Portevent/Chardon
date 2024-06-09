"""
Field
"""
from enum import Enum, auto

from code_parser.structure.function import Function
from code_parser.structure.type import Type


class Visibility(Enum):
    """
    Score of a field
    """
    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()


class Field:
    """
    Class have fields, that can be private, protected or public.
    They can have a Type or be a Function
    """

    def __init__(self, name: str, _type: Type | Function, visibility: Visibility, comment: str = "",
                 attributes: dict = None):
        """
        Init a Field
        @param name: name
        @param _type: Can be Type or a Function
        @param visibility: Scope
        @param comment: Comment
        @param attributes: custom attributes
        """
        self.name = name
        self.type = _type
        self.visibility = visibility
        self.comment = comment
        self.attributes = attributes or {}

    def set(self, key: str, value):
        """
        Define a custom attributes
        @param key: Key
        @param value: Value
        """
        self.attributes[key] = value

    def is_function(self) -> bool:
        """
        Is field a Function
        @return:
        """
        return isinstance(self.type, Function)

    def __str__(self):
        return f"<Field {self.name} {self.type}>"
