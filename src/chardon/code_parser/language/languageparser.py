"""
Parser abstract class
"""
from abc import ABC
from pathlib import Path
from typing import List

from chardon.code_parser.structure import Class


class ParsingError(Exception):
    """
    Custom error, that can be linked to a certain line in a file
    """

    def __init__(self, message: str, line: str = "", line_number: int = None, file: str = ""):
        self.message = message
        self.line = line
        self.line_number = line_number
        self.file = file

    def __str__(self):
        return f'{self.file} : {self.line_number} {self.line} \n {self.message}'


# pylint: disable=too-few-public-methods
class LanguageParser(ABC):
    """
    Parse file an extract code
    """

    def __init__(self, parameters: dict = None):
        self.parameters = parameters or {}

    def parse(self, file: Path, encoding="utf-8") -> List[Class]:
        """
        Open a file and parse its content
        @param file: Path to the code
        @param encoding: Encoding, default is utf-8
        @return: List of classes
        """
        with open(file, 'r', encoding=encoding) as f:
            try:
                return self._parse(f.readlines())
            except ParsingError as e:
                e.file = file.name
                raise e
            except BaseException as e:
                print(f"Uncaught exception at {file}")
                raise e

    def _parse(self, lines: List[str]) -> List[Class]:
        raise NotImplementedError
