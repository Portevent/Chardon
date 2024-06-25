"""
Class

Note : the file is named class_ so that it doesn't confuse Python
"""
from enum import Enum, auto
from typing import List

from src.code_parser.structure.field import Field, Scope
from src.code_parser.structure.type import Type


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
                 scope: Scope = Scope.PUBLIC,
                 inherits: List[Type] = None, variant: ClassVariant = ClassVariant.NONE,
                 attributes: dict = None):
        """
        Init Class
        @param name: name
        @param fields: fields
        @param comment: comment
        @param scope: Scope of the class
        @param inherits: inherits from classes or type
        @param variant: customize class to be a struct or enum
        @param attributes: custom attributes
        """
        super().__init__(name, inherits)
        self.name = name
        self.fields = fields
        self.scope = scope
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
        fields_text: str = ""
        if len(self.fields):
            fields_text = '\n' + '\n'.join(list(map(str, self.fields))) + '\n'
        return f"<Class {self.name} | {fields_text}>"
