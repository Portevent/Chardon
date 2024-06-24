"""
Structure normalisation of information
"""
from enum import Enum, auto, Flag
from typing import List

from src.article_builder.parser.text_parser import TextParser


class ContentType(Enum):
    """
    Content can have a type to represent their struct and what kind of information they store
    """
    SECTION = auto()
    HEADER = auto()
    TEXT = auto()
    SPAN = auto()
    LIST = auto()
    LIST_ENTRY = auto()
    TITLE = auto()
    QUOTE = auto()
    CODE = auto()
    SEPARATOR = auto()
    TABLE = auto()
    IMAGE = auto()
    LINK = auto()
    COMMENT = auto()


class TextStyle(Flag):
    """
    Style variant for emphasized text
    """
    REGULAR = auto()
    ITALIC = auto()
    BOLD = auto()
    UNDERLINED = auto()
    STRIKETHROUGH = auto()


class TableCell:
    """
    A single Table Cell
    """

    def __init__(self, content: 'Content', size: int = 1):
        self.content = content
        self.size = size

    def get_size(self) -> int:
        """
        Get the size of the cell
        @return: size
        """
        return self.size

    def set_size(self, size: int):
        """
        Set the size of the cell
        @param size: New size
        """
        self.size = size

    def get_content(self) -> 'Content':
        """
        Get the Content of the cell
        @return: Content
        """
        return self.content

    def set_content(self, content: 'Content'):
        """
        Set the Content of the cell
        @param content: New content
        """
        self.content = content


# pylint: disable=too-few-public-methods
class TableRow:
    """
    A Table Row, containing cells
    """

    def __init__(self, cells: List[str] | List['Content'] | List[TableCell]):
        """
        Create a row, from either a list of str or a list of TableCell
        @param cells: cells within this row
        @return: TableRow
        """
        if len(cells) == 0:
            self.cells = []
            return

        if isinstance(cells[0], str):
            self.cells = [TableCell(Content.FromText(text)) for text in cells]
        elif isinstance(cells[0], Content):
            content: Content
            self.cells = [TableCell(content) for content in cells]
        else:
            self.cells = cells


# pylint: disable=invalid-name
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

    def __repr__(self):
        return f"<{self.type.name}{' '.join(map(str, self.attributes.get('children', [])))}>"

    def __str__(self):
        return f"<{self.type.name}{' '.join(map(str, self.attributes.get('children', [])))}>"

    def add_children(self, child: 'Content'):
        """
        Insert a child inside the content
        (only if the content is from a type that can holds children)
        @param child: Content to add
        """
        if 'children' in self.attributes:
            self.attributes['children'].append(child)
        else:
            raise AttributeError(f'Trying to fit a children inside a {self.type} content')

    def add_row(self, row: 'Content'):
        """
        Insert a row inside the content
        (only if the content is from a type that can holds rows)
        @param row: Content to add
        """
        if 'rows' in self.attributes:
            self.attributes['rows'].append(row)
        else:
            raise AttributeError(f'Trying to fit a row inside a {self.type} content')

    @staticmethod
    def Section(contents: List['Content'], attributes: dict = None) -> 'Content':
        """
        Create a Section Content, which hold children
        @param contents: contents within it
        @param attributes: optional custom attributes
        @return: Section Content
        """
        attr = attributes or {}
        attr['children'] = contents
        return Content(ContentType.SECTION, attr)

    @staticmethod
    def Header(attributes: dict) -> 'Content':
        """
        Create a Header Content, which hold attributes and metadata
        @param attributes: attributes
        @param attributes: optional custom attributes
        @return: Header Content
        """
        return Content(ContentType.HEADER, attributes)

    @staticmethod
    def Text(text: str, attributes: dict = None) -> 'Content':
        """
        Create a Text Content, which hold plain text
        @param text: Text
        @param attributes: optional custom attributes
        @return: Text Content
        """
        attr = attributes or {}
        attr['text'] = text
        return Content(ContentType.TEXT, attr)

    @staticmethod
    def FromText(text: str) -> 'Content':
        """
        Create a Span Content, from text that will be parsed
        @param text: text to parse
        @return: Span Content with parsed text inside
        """
        return Content.Span(Content.parser(text).parse())

    @staticmethod
    def Span(children: List['Content'], style: TextStyle = TextStyle.REGULAR,
             attributes: dict = None) -> 'Content':
        """
        Create a Span Content, which hold formatting and sub-span or text Content
        @param children: Contents within this span
        @param style: Formatting this span gives
        @param attributes: optional custom attributes
        @return: Span Content
        """
        attr = attributes or {}
        attr['style'] = style
        attr['children'] = children
        return Content(ContentType.SPAN, attr)

    @staticmethod
    def Title(title: str, level: int = 1, attributes: dict = None) -> 'Content':
        """
        Create a Title Content
        @param title: Title
        @param level: Level of the title (starting from 1, which is the default)
        @param attributes: optional custom attributes
        @return: Title Content
        """
        attr = attributes or {}
        attr['text'] = title
        attr['level'] = level
        return Content(ContentType.TITLE, attr)

    @staticmethod
    def QuoteText(quote: str, author: str = None,
                  date: str = None, location: str = None,
                  attributes: dict = None) -> 'Content':
        """
        Create a Quote Content from a text (use .Quote for quoting a content block)
        @param quote: content to quote
        @param author: Who made this quote
        @param date: When this quote was made
        @param location: Where this quote was made
        @param attributes: optional custom attributes
        @return: Quote Content
        """
        return Content.Quote(Content.FromText(quote), author, date, location, attributes)

    @staticmethod
    def Quote(quote: 'Content', author: str = None,
              date: str = None, location: str = None,
              attributes: dict = None) -> 'Content':
        """
        Create a Quote Content from another content (use .QuoteText for quoting a string)
        A Quote contains a quote, made by someone, at some time
        @param quote: content to quote
        @param author: Who made this quote
        @param date: When this quote was made
        @param location: Where this quote was made
        @param attributes: optional custom attributes
        @return: Quote Content
        """
        attr = attributes or {}
        attr['quote'] = quote
        if author:
            attr['author'] = author
        if date:
            attr['date'] = date
        if location:
            attr['location'] = location
        return Content(ContentType.QUOTE, attr)

    @staticmethod
    def Code(code: str, language: str = None, attributes: dict = None) -> 'Content':
        """
        Create a Code Content, which hold code from a specific language
        @param code: Code
        @param language: Name of the language
        @param attributes: optional custom attributes
        @return: Code Content
        """
        attr = attributes or {}
        attr['text'] = code
        attr['language'] = language
        return Content(ContentType.CODE, attributes)

    @staticmethod
    def Separator(attributes: dict = None) -> 'Content':
        """
        Create an horizontal Separator
        @param attributes: optional custom attributes
        @return: Separator Content
        """
        return Content(ContentType.SEPARATOR, attributes or {})

    @staticmethod
    def Table(headers: List[str] | List['Content'], rows: List[TableRow | List[str]],
              attributes: dict = None) -> 'Content':
        """
        Create a Table Content
        @param headers: Name of the columns
        @param rows: Rows within it
        @param attributes: optional custom attributes
        @return: Table Content
        """

        attr = attributes or {}
        attr['headers'] = headers
        attr['rows'] = []

        if len(headers) > 0:
            if isinstance(headers[0], str):
                attr['headers'] = [Content.FromText(text) for text in headers]

        if len(rows) > 0:
            if isinstance(rows[0], TableRow):
                attr['rows'] = rows
            else:  # Convert each str[] to TableRow
                attr['rows'] = [TableRow(cells) for cells in rows]

        return Content(ContentType.TABLE, attr)

    @staticmethod
    def Image(uri: str, alt: str, link: str = "",
              attributes: dict = None) -> 'Content':
        """
        Create an Image Content
        @note : Some exporter may use way more attributes, such as <title> <width> <height> etc...
        @param uri: URI of the image
        @param alt: Alt text
        @param link: Link to open when clicking the image
        @param attributes: optional custom attributes
        @return: Image Content
        """
        attr = attributes or {}
        attr['uri'] = uri
        attr['alt'] = alt
        if link:
            attr['link'] = link
        return Content(ContentType.IMAGE, attr)

    @staticmethod
    def Link(text: str, target: str, alt: str = "",
             attributes: dict = None) -> 'Content':
        """
        Create a Link Content
        @param text: Text
        @param target: Target where this link points to
        @param alt: Alt text
        @param attributes: optional custom attributes
        @return: Link Content
        """
        attr = attributes or {}
        attr['text'] = text
        attr['target'] = target
        if alt:
            attr['alt'] = alt
        return Content(ContentType.LINK, attr)

    @staticmethod
    def InternalLink(text: str, attributes: dict = None) -> 'Content':
        """
        Create a Link Content that is internal and only has text by default
        @param text: Text
        @param attributes: optional custom attributes
        @return: Link Content
        """
        attr = attributes or {}
        attr['target'] = text
        attr['internal-link'] = True
        return Content(ContentType.LINK, attr)

    @staticmethod
    def Comment(comment: str, attributes: dict = None) -> 'Content':
        """
        Create a Comment Content, for debug purpose
        @param comment: Comment
        @param attributes: optional custom attributes
        @return: Comment Content
        """
        attr = attributes or {}
        attr['text'] = comment
        return Content(ContentType.COMMENT, attr)

    @staticmethod
    def ListEntry(entry: 'Content', level: int = 0,
                  completed: bool = None, attributes: dict = None) -> 'Content':
        """
        Create a List Entry Content, containing ListEntry Content
        @param entry: Entry in the list
        @param level: Level of the entry (starts at 0 for main list)
        @param completed: checked tasked or not (None for no checkbox at all)
        @param attributes: optional custom attributes
        @return: List Entry Content
        """
        attr = attributes or {}
        attr['entry'] = entry
        attr['level'] = level
        if completed is not None:
            attr['completed'] = completed
        return Content(ContentType.LIST_ENTRY, attr)

    # Note : We put this method at the very end, as it confuses Python interpreter
    # After this method, Python will incorrectly assume that typing List refers to this function
    # eg : def sort(my_array: List[int]): will raise 'staticmethod' object is not callable
    @staticmethod
    def List(entries: List[str] | List['Content'],
             ordered: bool = False, attributes: dict = None, checkbox: bool = None) -> 'Content':
        """
        Create a List Content, containing ListEntry Content
        @param entries: Entries in the list
        @param ordered: Ordered list or not
        @param checkbox: Default state of the checkbox (None for no checkbox)
        @param attributes: optional custom attributes
        @return: List Content
        """
        attr = attributes or {}
        attr['children'] = []
        attr['ordered'] = ordered
        if len(entries) > 0:
            if isinstance(entries[0], str):
                attr['children'] = [Content.ListEntry(Content.FromText(text), completed=checkbox)
                                    for text in entries]
            else:
                content: 'Content'
                # Encapsulate all content that are not List Entry into a List Entry Content
                attr['children'] = [content if content.type == ContentType.LIST_ENTRY
                                    else Content.ListEntry(content)
                                    for content in entries]

        return Content(ContentType.LIST, attr)
