"""
implementation of export content to Markdown
"""
from typing import List

from chardon.article_builder.content import Content
from chardon.exporter import ContentExport

class HTMLContentExport(ContentExport):
    """
    Export Content To Html
    """

    def export(self, contents: List[Content]) -> str:
        """
        Export content
        """
        raise NotImplementedError
        