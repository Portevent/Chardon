"""
Field
"""
from enum import Enum, auto

from chardon.code_parser.structure import Function
from chardon.code_parser.structure import Type


class Scope(Enum):
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

    # pylint: disable=too-many-arguments
    def __init__(self, name: str, type_: Type | Function, scope: Scope, comment: str = "",
                 default_value: str = "",
                 attributes: dict = None):
        """
        Init a Field
        @param name: name
        @param type_: Can be Type or a Function
        @param scope: Scope
        @param comment: Comment
        @param default_value: Default value
        @param attributes: custom attributes
        """
        self.name = name
        self.type = type_
        self.scope = scope
        self.comment = comment
        self.default_value = default_value
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
