"""
Abstract Table of Content
"""
from abc import ABC, abstractmethod
from typing import List

from chardon.article_builder.content import Content


class TableOfContentABC(ABC):
    """
    Abstract Table of Content
    """

    @abstractmethod
    def add_entry(self, text: str, uri: str, description: str = None):
        """
        Add entry to the table of content
        @param text: Entry
        @param uri: Uri
        @param description: (optional) add detail to entry
        """
        raise NotImplementedError

    @abstractmethod
    def get_contents(self) -> List[Content]:
        """
        Return all contents representing this table of content
        @return: summary
        """
        raise NotImplementedError
