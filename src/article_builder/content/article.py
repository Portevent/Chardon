"""
Basic Article
"""
from typing import List

from src.article_builder.content.content import Content
from src.article_builder.content.obsidian_note import HeaderAndContent


class Article(HeaderAndContent):
    """
    Meta Content to store a basic Article layout, with table of content
    """
    def __init__(self):
        super().__init__()
        self.table_of_contents: Content = Content.List([])

    def add_content(self, content, create_link=False):
        """
        Add Content to the Article
        @param content: Content
        @param create_link: Add a link in the summary (default is False)
        """
        self.content.append(content)
        if create_link:
            self.table_of_contents.add_children(Content.InternalLink(content.attributes['text']))

    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header, Content.Title("Table of contents :"),
                self.table_of_contents, Content.Separator()] + self.content
