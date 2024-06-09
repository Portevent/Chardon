"""Debug class to parse text as is"""
from typing import List

from article_builder.content.content import Content
from article_builder.parser.text_parser import TextParser


# pylint: disable=too-few-public-methods
class NoParser(TextParser):
    """
    Simple language that just return text as is
    """

    def parse(self) -> List[Content]:
        """
        Return text without parsing
        """
        return [Content.Text(self._text)]
