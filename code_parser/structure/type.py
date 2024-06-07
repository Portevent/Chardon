"""
Type
"""
from typing import List


# pylint: disable=too-few-public-methods
class Type:
    """
    Basic type
    """

    def __init__(self, name: str, inherits: List['Type'] = None):
        """
        Init a new Type
        @param name: Name of the type
        @param inherits: Inherits from
        """
        self.name = name
        self.inherits = inherits or []
