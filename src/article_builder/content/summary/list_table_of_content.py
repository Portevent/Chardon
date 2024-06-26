"""
Basic List Table Of Content
"""
import logging
from typing import List

from src.article_builder.content.content import Content
from src.article_builder.content.summary.abc_table_of_content import TableOfContentABC


class ListTableOfContent(TableOfContentABC):
    """
    List table of content :
    # Table of content
    1 - First Title
    2 - Second Title
    3 - Unexpected End of the Story
    """

    def __init__(self):
        self.entries = []

    def add_entry(self, text: str, uri: str, description: str = None):
        """
        Add an entry in the table of content
        @param text: Text
        @param uri: URI
        @param description: Description (not supported for list)
        """
        self.entries.append([text, uri])

        if description is not None:
            logging.warning("%s recieved description for an entry (%s),"
                            "but doesn't support description."
                            "This content will be skipped",
                            self.__class__.__name__, text)

    def get_contents(self) -> List[Content]:
        """
        Export table of content to Contents
        @return:
        """
        if len(self.entries) == 0:
            return []

        return [
            Content.Title("Table Of Content", 1),
            Content.List([
                Content.InternalLink(text, uri) for (text, uri) in self.entries
            ]),
            Content.Separator()
        ]
