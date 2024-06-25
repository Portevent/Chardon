"""Debug class to parse text as is"""
from typing import List

from src.article_builder.content.content import Content
from src.content_parser.text_parser import ContentParser


# pylint: disable=too-few-public-methods
class NoParser(ContentParser):
    """
    Simple language that just return text as is
    """

    def parse(self) -> List[Content]:
        """
        Return text without parsing
        """
        return [Content.Text('\n'.join(self._text))]
