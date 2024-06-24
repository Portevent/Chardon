"""
Type
"""
from typing import List


# pylint: disable=too-few-public-methods
class Type:
    """
    Basic type
    """

    def __init__(self, name: str, inherits: List['Type'] = None, attributes: dict = None):
        """
        Init a new Type
        @param name: Name of the type
        @param inherits: Inherits from
        @param attributes: Customs attributes
        """
        self.name = name
        self.inherits = inherits or []
        self.attributes = attributes or {}

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"