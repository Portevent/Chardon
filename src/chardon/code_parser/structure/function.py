"""
Function
"""
from typing import List

# pylint: disable=too-few-public-methods
from chardon.code_parser.structure import Parameter


class Function:
    """
    Store a Function, with Parameters
    """

    outputs: List[Parameter]

    def __init__(self, inputs: List[Parameter] = None, outputs: List[Parameter] = None, ):
        """
        Init Function
        @param inputs: input parameters
        @param outputs: output parameters
        """
        self.inputs = inputs or []
        self.outputs = outputs or []

    def __str__(self):
        return f"<Function {' '.join(list(map(str, self.inputs)))}>"
