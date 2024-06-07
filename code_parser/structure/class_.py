"""
Class

Note : the file is named class_ so that it doesn't confuse Python
"""
from enum import Enum, auto
from typing import List

from code_parser.structure.field import Field, Visibility
from code_parser.structure.type import Type


class ClassVariant(Enum):
    """
    Variant of a class
    """
    NONE = auto()
    STRUCT = auto()
    ENUM = auto()


# pylint: disable=too-few-public-methods
class Class(Type):
    """
    Class have name, fields and can inherits from other class or Type
    """

    # pylint: disable=too-many-arguments
    def __init__(self, name: str, fields: List[Field] = None, comment: str = "",
                 visibility: Visibility = Visibility.PUBLIC,
                 inherits: List[Type | str] = None, variant: ClassVariant = ClassVariant.NONE,
                 attributes: dict = None):
        """
        Init Class
        @param name: name
        @param fields: fields
        @param comment: comment
        @param visibility: Scope of the class
        @param inherits: inherits from classes or type (can be string if not documented yet)
        @param variant: customize class to be a struct or enum
        @param attributes: custom attributes
        """
        super().__init__(name, inherits)
        self.name = name
        self.fields = fields
        self.visibility = visibility
        self.comment = comment
        self.variant = variant
        self.attributes = attributes or {}

    def add_field(self, field: Field):
        """
        Add field in class
        @param field: field
        """
        self.fields.append(field)

    def __str__(self):
        fields_text: str = '\n'.join(list(map(str, self.fields)))
        return f"<Class {self.name} | \n{fields_text}\n>"
