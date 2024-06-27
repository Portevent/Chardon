"""
Basic Article
"""
from typing import List

from chardon.article_builder.content import Content
from chardon.article_builder.summary.abc_table_of_content import TableOfContentABC
from chardon.article_builder.summary.list_table_of_content import ListTableOfContent


class Article:
    """
    Meta Content to store the basis of an article :
    metadata (Header), summary (TableOfContent) and the article itself (Contents)
    """
    TABLE_OF_CONTENT: type[TableOfContentABC] = ListTableOfContent

    def __init__(self):
        self.header: Content = Content.Header({
            'title': '',
            'aliases': [],
            'tags': []
        })
        self.table_of_contents = self.TABLE_OF_CONTENT()
        self.contents: list[Content] = []

    def add_content(self, content):
        """
        Add Content to the Article
        @param content: Content
        """
        self.contents.append(content)

    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header] + self.table_of_contents.get_contents() + self.contents

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
