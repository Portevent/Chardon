from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List


class ContentType(Enum):
    SECTION = auto()
    HEADER = auto()
    TEXT = auto()
    LIST = auto()
    TITLE = auto()
    QUOTE = auto()
    CODE = auto()
    SEPARATOR = auto()
    TABLE = auto()


class TableCell:
    """
    A single Table Cell
    """

    def __init__(self, text: str, size: int = 1):
        self.text = text
        self.size = size


class TableRow:
    """
    A Table Row, containing cells
    """

    def __init__(self, cells: List[str] | List[TableCell]):
        """
        Create a row, from either a list of str or a list of TableCell
        :param cells: cells within this row
        :return: TableRow
        """
        if len(cells) == 0:
            self.cells = []
            return

        if type(cells[0]) is str:
            self.cells = [TableCell(text) for text in cells]
        else:
            self.cells = cells


class Content(ABC):
    """
    Abstract class that define the bases of content registration.
    It allows to represent information disposition non-specific to a language (MD, Json, Html)
    Can be inherited to implement exporting to a language.
    """

    def __init__(self, content_type: ContentType, attributes: dict):
        self.type = content_type
        self.attributes = attributes

    @abstractmethod
    def export(self) -> str:
        """
        Export itself to str in the implemented language
        """
        return NotImplemented

    @staticmethod
    def Section(contents: List['Content']) -> 'Content':
        """
        Create a Section Content, which hold children
        :param contents: contents within it
        :return: Section Content
        """
        return Content(ContentType.SECTION, {'children': contents})

    @staticmethod
    def Header(attributes: dict) -> 'Content':
        """
        Create a Header Content, which hold attributes and metadata
        :param attributes: attributes
        :return: Header Content
        """
        return Content(ContentType.HEADER, attributes)

    @staticmethod
    def Text(text: str) -> 'Content':
        """
        Create a Text Content
        :param text: text within content
        :return: Text Content
        """
        return Content(ContentType.TEXT, {'text': text})

    @staticmethod
    def List(texts: List[str]) -> 'Content':
        """
        Create a List Content, containing text entries
        :param texts: Elements in the list
        :return: List Content
        """
        return Content(ContentType.LIST, {'children': texts})

    @staticmethod
    def Title(title: str, level: int = 1) -> 'Content':
        """
        Create a Title Content
        :param title: Title
        :param level: Level of the title (starting from 1, which is the default)
        :return: Title Content
        """
        return Content(ContentType.TITLE, {'text': title, 'level': level})

    @staticmethod
    def Quote(quote: str, author: str = None, date: str = None, location: str = None) -> 'Content':
        """
        Create a Quote Content, which contains a quote, made by someone, at some time
        :param quote: Text
        :param author: Who made this quote
        :param date: When this quote was made
        :param location: Where this quote was made
        :return: Quote Content
        """
        attrs = {'text': quote}
        if author:
            attrs['author'] = author
        if date:
            attrs['date'] = date
        if location:
            attrs['location'] = location
        return Content(ContentType.QUOTE, attrs)

    @staticmethod
    def Code(code: str, language: str = None) -> 'Content':
        """
        Create a Code Content, which hold code from a specific language
        :param code: Code
        :param language: Name of the language
        :return: Code Content
        """
        return Content(ContentType.CODE, {'text': code, 'language': language})

    @staticmethod
    def Separator() -> 'Content':
        """
        Create an horizontal Separator
        :return: Separator Content
        """
        return Content(ContentType.SEPARATOR, {})

    @staticmethod
    def Table(headers: List[str], rows: List[TableRow | List[str]]) -> 'Content':
        """
        Create a Table Content
        :param headers: Name of the columns
        :param rows: Rows within it
        :return: Table Content
        """
        attr = {'headers': headers, 'rows': []}

        if len(rows) > 0:
            if type(rows) is TableRow:
                attr['rows'] = rows
            else:  # Convert each str[] to TableRow
                attr['rows'] = [TableRow(cells) for cells in rows]

                return Content(ContentType.TABLE, attr)
