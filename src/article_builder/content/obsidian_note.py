"""
Obsidian Note
"""
from typing import List
from src.article_builder.content.content import Content


class ObsidianNote:
    """
    Meta Content to store the basis of an ObsidianNote
    metadata (Header) and the article itself (Contents)
    """
    def __init__(self):
        self.header: Content = Content.Header({
            'title': '',
            'aliases': [],
            'tags': []
        })
        self.content: list[Content] = []

    def set_title(self, title: str):
        """
        Set the title of the note
        @param title: title
        """
        self.header.attributes['title'] = title

    def add_alias(self, alias: str):
        """
        Add alias to the note
        @param alias: alias
        """
        self.header.attributes['aliases'].append(alias)

    def add_tag(self, tag: str):
        """
        Add tag to the note
        @param tag: tag
        """
        self.header.attributes['tags'].append(tag)

    def set_metadata(self, key: str, value):
        """
        Set custom metadata
        @param key: Key
        @param value: Value
        """
        self.header.attributes[key] = value

    def add_content(self, content):
        """
        Insert Content in Article
        @param content: Content
        """
        self.content.append(content)

    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header] + self.content
