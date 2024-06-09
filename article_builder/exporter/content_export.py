"""
Abstract content export class
"""

from abc import ABC, abstractmethod
from typing import List

from article_builder.content.content import Content


class ContentExport(ABC):
    """
    Abstract class to represent an Exporter
    Can be implemented to export Contents into a specific format (Markdown, html, etc)
    """

    # Default extension to use
    PREFERRED_EXTENSION: str = ".txt"

    def __init__(self, params: dict = None):
        """
        Init an Exporter, with possible parameters
        @param params: Parameters to setup
        """
        self.params = params or {}

    def param(self, key: str, value):
        """
        Set a parameter
        @param key: Key
        @param value: Value
        """
        self.params[key] = value

    @abstractmethod
    def export(self, contents: List[Content]) -> str:
        """
        Export Contents to str in the implemented language
        @param contents : Contents to export
        """
        return NotImplemented
