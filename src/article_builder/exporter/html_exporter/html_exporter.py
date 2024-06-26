"""
implementation of export content to Markdown
"""
from enum import Enum, auto
from typing import List

from src.article_builder.content.content import ContentType, Content, TextStyle
from src.article_builder.exporter.content_export import ContentExport


class HTMLContentExport(ContentExport):
    """
    Export Content To Html
    """

    def export(self, contents: List[Content]) -> str:
        """
        Export content
        """
        raise NotImplementedError
        