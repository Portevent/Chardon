"""
Function
"""
from typing import List

from code_parser.structure.parameter import Parameter
from code_parser.structure.type import Type


# pylint: disable=too-few-public-methods
class Function(Type):
    """
    Store a Function, with Parameters
    """

    def __init__(self, inputs: List[Parameter] = None, outputs: List[Parameter] = None):
        """
        Init Function
        @param inputs: input parameters
        @param outputs: output parameters
        """
        self.inputs = inputs or []
        self.outputs = outputs or []

    def __str__(self):
        return f"<Function {' '.join(list(map(str, self.inputs)))}>"
