from enum import Enum, auto, Flag
from typing import List

from doc_generator.article_builder.parser.text_parser import TextParser


class ContentType(Enum):
    """
    Content can have a type to represent their struct and what kind of information they store
    """
    SECTION = auto()
    HEADER = auto()
    TEXT = auto()
    SPAN = auto()
    LIST = auto()
    TITLE = auto()
    QUOTE = auto()
    CODE = auto()
    SEPARATOR = auto()
    TABLE = auto()
    IMAGE = auto()


class TextStyle(Flag):
    REGULAR = auto()
    ITALIC = auto()
    BOLD = auto()
    UNDERLINED = auto()
    STRIKETHROUGH = auto()


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

        if isinstance(cells[0], str):
            self.cells = [TableCell(text) for text in cells]
        else:
            self.cells = cells



class Content:
    """
    Class that define the bases of content registration.
    It allows to represent information disposition non-specific to a language
    Eg : it will store title, and not <h2>...</h2> or ## ...
    """

    parser: type[TextParser]  # Need to be set at runtime, to specify which class to use as Parser

    def __init__(self, content_type: ContentType, attributes: dict):
        self.type = content_type
        self.attributes = attributes

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
        return Content(ContentType.TEXT, {'text': text})

    @staticmethod
    def FromText(text: str) -> 'Content':
        return Content.Span(Content.parser(text).parse())

    @staticmethod
    def Span(children: List['Content'], style: TextStyle = TextStyle.REGULAR) -> 'Content':
        return Content(ContentType.SPAN, {'style': style, 'children': children})

    @staticmethod
    def OrderedList(texts: List[str]) -> 'Content':
        """
        Create an ordered List Content, containing text entries
        :param texts: Elements in the list
        :return: List Content
        """
        return Content(ContentType.LIST, {'children': texts, 'ordered': True})

    @staticmethod
    def UnorderedList(texts: List[str]) -> 'Content':
        """
        Create an unordered List Content, containing text entries
        :param texts: Elements in the list
        :return: List Content
        """
        return Content(ContentType.LIST, {'children': texts, 'ordered': False})

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
    def Quote(quote: 'Content', author: str = None,
                date: str = None, location: str = None) -> 'Content':
        """
        Create a Quote Content, which contains a quote, made by someone, at some time
        :param quote: content to quote
        :param author: Who made this quote
        :param date: When this quote was made
        :param location: Where this quote was made
        :return: Quote Content
        """
        attrs = {'quote': quote}
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
            if isinstance(rows[0], TableRow):
                attr['rows'] = rows
            else:  # Convert each str[] to TableRow
                attr['rows'] = [TableRow(cells) for cells in rows]

        return Content(ContentType.TABLE, attr)

    @staticmethod
    def Image(source: str, alt: str = "", link: str = "",
              title: str = "", caption: str = "") -> 'Content':
        """
        Create an Image Content
        :param source: URI of the image
        :param alt: Alt text
        :param link: Link
        :param title: Title of the image
        :param caption: Caption to display below image
        :return: Image Content
        """
        attrs = {'source': source}
        if alt:
            attrs['alt'] = alt
        if link:
            attrs['link'] = link
        if title:
            attrs['title'] = title
        if caption:
            attrs['caption'] = caption
        return Content(ContentType.IMAGE, attrs)

    def __repr__(self):
        return f"<{self.type.name} {' '.join(map(str, self.attributes['children'] if 'children' in self.attributes else []))}>"

    def __str__(self):
        return f"<{self.type.name} {' '.join(map(str, self.attributes['children'] if 'children' in self.attributes else []))}>"

    def addChildren(self, child: 'Content'):
        if 'children' in self.attributes:
            self.attributes['children'].append(child)
        else:
            raise Exception(f'Trying to fit a children inside a {self.type} content')
