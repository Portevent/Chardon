"""Abstract class for parsing stylized text into content"""
from abc import ABC, abstractmethod
from typing import List


class TextParser(ABC):
    """
    Parse a text into content
    """

    def __init__(self, text: str):
        self._text = text

    @abstractmethod
    def parse(self) -> List['Content']:
        """
        Parse the text into Content
        """
        raise NotImplementedError

    def get_text(self) -> str:
        """
        Return text
        """
        return self._text
