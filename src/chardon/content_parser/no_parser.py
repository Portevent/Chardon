"""Debug class to parse text as is"""
from typing import List

# pylint: disable=too-few-public-methods
from chardon.article_builder import ContentParser, Content


class NoParser(ContentParser):
    """
    Simple language that just return text as is
    """

    def parse(self) -> List[Content]:
        """
        Return text without parsing
        """
        return [Content.Text('\n'.join(self._text))]
