"""
Basic Article
"""
from typing import List

from article_builder.content.content import Content
from article_builder.content.obsidian_note import ObsidianNote


class Article(ObsidianNote):
    """
    Meta Content to store a basic Article layout, containing slug metadata and table of content
    """
    def __init__(self):
        super().__init__()
        self.table_of_contents: Content = Content.List([])
        self.header.attributes['slug'] = ''

    def set_slug(self, slug: str):
        """
        Set the slug of the Article
        @param slug: slug
        """
        self.header.attributes['slug'] = slug

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
