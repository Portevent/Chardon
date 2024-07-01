"""
implementation of export content to Markdown
"""
from enum import Enum, auto
from typing import List

from src.article_builder.content import ContentType, Content, TextStyle
from src.article_builder.exporter import ContentExport


class HTMLContentExport(ContentExport):
    """
    Export Content To Html
    """

    def export(self, contents: List[Content]) -> str:
        """
        Export content
        """
        raise NotImplementedError
        