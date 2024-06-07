"""
Basic Article
"""
from typing import List

from doc_generator.article_builder.content.content import Content
from doc_generator.article_builder.content.obsidian_note import ObsidianNote


class Article(ObsidianNote):
    """
    Meta Content to store a basic Article layout, containing slug metadata and summary
    """
    def __init__(self):
        super().__init__()
        self.summary: Content = Content.Table(['Name', 'Description'], [])
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
            self.summary.add_children(Content.InternalLink(content.attributes['text']))

    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header, Content.Title("Summary :"),
                self.summary, Content.Separator()] + self.content
