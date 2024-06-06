"""Debug class to parse text as is"""
from typing import List

from doc_generator.article_builder.content import Content
from doc_generator.article_builder.parser.text_parser import TextParser


class NoParser(TextParser):
    """
    Simple parser that just return text as is
    """

    def parse(self) -> List['Content']:
        """
        Return text without parsing
        """
        return [Content.Text(self._text)]
