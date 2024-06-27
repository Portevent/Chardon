"""
Basic List Table Of Content
"""
from typing import List

from chardon.article_builder.content import Content,  TableRow
from chardon.article_builder.summary import TableOfContentABC


class TableTableOfContent(TableOfContentABC):
    """
    Table table of content :
    # Table of content
    Name | Description
    Hello World - First Title
    Who left that rake on the floor ? - Second Title
    Bonk - Unexpected End of the Story
    """

    def __init__(self):
        self.entries = []

    def add_entry(self, text: str, uri: str, description: str = None):
        self.entries.append([text, uri, description])

    def get_contents(self) -> List[Content]:
        if len(self.entries) == 0:
            return []

        return [
            Content.Title("Table Of Content", 1),
            Content.Table(['Name', 'Description'], [
                TableRow([
                    Content.InternalLink(text, uri),
                    Content.FromText(description)
                ]) for (text, uri, description) in self.entries
            ]),
            Content.Separator()
        ]
