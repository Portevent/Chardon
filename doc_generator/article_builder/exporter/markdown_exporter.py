"""
implementation of export content to Markdown
"""
from enum import Enum, auto
from typing import List

from doc_generator.article_builder.content.content import ContentType, Content, TextStyle
from doc_generator.article_builder.exporter.content_export import ContentExport


# pylint: disable=too-many-arguments
def joins(elements: List[str], before: str = '', before_each: str = '',
          after: str = '', after_each: str = '', between_each: str = ''):
    """
    Convert a list into a string
    @param elements: list
    @param before: Text before the list
    @param before_each: Text before each element of the list
    @param after: Text after the list
    @param after_each: Text after each element of the list
    @param between_each: Text between each element of the list
    @return: string
    """
    return before + between_each.join(
        [before_each + element + after_each for element in elements]
    ) + after


# pylint: disable=anomalous-backslash-in-string
def clean_list_element(element: str):
    """
    Markdown will improperly convert unsorted array to sorted
    array if the first element starts with a number
    eg. Avoid doing
    - 1 octet is equals to 8 bits
    - This is the second element

    Do this instead :
    - 1\ octet is equals to 8 bits
    - This is the second element
    See https://www.markdownguide.org/basic-syntax/#starting-unordered-list-items-with-numbers
    @param element: Element to clean
    @return: Unambiguous text
    """
    if element[0].isdigit():
        i = 0
        while element[i].isdigit():
            i += 1
        return element[:i] + "\\" + element[i:]
    return element


class MarkdownContentBreaklineType(Enum):
    """
    Markdown allows multiple way of formatting breakline,
    this parameter ensure compatibility across different Markdown interpreter
    """
    NONE = auto()  # Not doing anything
    TRAILING_WHITESPACE = auto()  # Adding two space
    BACKSLASH = auto()  # Using \
    BR_TAG = auto()  # Using <br>


class MarkdownContentExport(ContentExport):
    """
    Export Content To Markdown
    """
    BREAKLINE: MarkdownContentBreaklineType = MarkdownContentBreaklineType.TRAILING_WHITESPACE

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.params['break_line_type'] = MarkdownContentExport.BREAKLINE

    def set_break_line_type(self, new_type: MarkdownContentBreaklineType):
        """
        Specify a breakline type
        @param new_type: Breakline
        """
        self.params['break_line_type'] = new_type

    def export(self, contents: List[Content]) -> str:
        """
        Export content
        """
        breakline: str = {
            MarkdownContentBreaklineType.NONE: '\n',
            MarkdownContentBreaklineType.TRAILING_WHITESPACE: '  \n',
            MarkdownContentBreaklineType.BACKSLASH: '\\\n',
            MarkdownContentBreaklineType.BR_TAG: '<br>\n'
        }[self.params['break_line_type']]  # Selecting the appropriate breakline

        text = "".join([self._export(content) for content in contents])

        return text.replace('\n', breakline)

    # pylint: disable=too-many-branches
    def _export(self, content: Content) -> str:
        """
        Export content, without considering the breaklines yet
        """
        exported_content: str
        match content.type:
            case ContentType.SEPARATOR:
                exported_content = '\n---\n'

            case ContentType.CODE:
                exported_content = joins(
                    before=f"```{content.attributes['language']}\n",
                    after="```",

                    elements=content.attributes['text'].split('\n'),
                    before_each="  ",
                    between_each="\n"
                )

            case ContentType.LIST_ENTRY:
                exported_content = "    " * content.attributes['level'] + \
                                   self._export(content.attributes['entry'])

            case ContentType.LIST:
                ordered = content.attributes['ordered']
                entries = ["    " * entry.attributes['level'] +
                           (f'{i + 1}. ' if ordered else "- ") +
                           self._export(entry.attributes['entry'])
                           for i, entry in enumerate(content.attributes['children'])]

                exported_content = joins(
                    elements=entries,
                    between_each="\n"
                )

            case ContentType.TEXT:
                exported_content = content.attributes['text']

            case ContentType.SPAN:
                exported_content = "".join([
                    self._export(children)
                    for children in content.attributes['children']
                ])

                if TextStyle.ITALIC in content.attributes['style']:
                    exported_content = f'*{exported_content}*'
                if TextStyle.BOLD in content.attributes['style']:
                    exported_content = f'**{exported_content}**'

            case ContentType.QUOTE:
                base_footer = "\n> "
                footer = base_footer

                # Creating the footer
                if 'author' in content.attributes:
                    footer += f" {content.attributes['author']}"
                if 'date' in content.attributes:
                    footer += f" {content.attributes['date']}"
                if 'location' in content.attributes:
                    footer += f" {content.attributes['location']}"

                if footer == base_footer:  # If the footer is empty, remove it
                    footer = ""

                exported_content = joins(
                    elements=self._export(content.attributes['quote']).split('\n'),
                    before_each="> ",
                    between_each="\n",

                    # Put blank line around the quote, for best practices :
                    # https://www.markdownguide.org/basic-syntax/#blockquotes-best-practices
                    before="\n",
                    after=footer + "\n"
                )

            case ContentType.HEADER:
                keys = content.attributes.keys()
                values = {}
                for key in keys:
                    if isinstance(content.attributes[key], list):
                        values[key] = joins(content.attributes[key],
                                            before="\n", before_each="- ", after_each="\n")
                    else:
                        values[key] = content.attributes[key]
                exported_content = '\n'.join([key + ": " + values[key] for key in keys])
                exported_content = f"---\n{exported_content}---"

            case ContentType.SECTION:
                exported_content = joins(
                    elements=[self._export(content)
                              for content in content.attributes['children']],
                    between_each="\n"
                )

            case ContentType.IMAGE:
                title = f" {content.attributes['title']}"\
                    if 'title' in content.attributes else ""
                size = f"|{content.attributes['size']}"\
                    if 'size' in content.attributes else ""

                exported_content = f"![{content.attributes['alt']}{size}" \
                                   f"({content.attributes['uri']}{title})]"
                if 'link' in content.attributes:
                    exported_content = f"[{exported_content}]({content.attributes['link']})"

            case ContentType.TITLE:
                # Put blank line around the title, for best practices :
                # https://www.markdownguide.org/basic-syntax/#heading-best-practices
                exported_content = f"\n{'#' * content.attributes['level']}" \
                                   f" {content.attributes['text']}\n"

            case ContentType.TABLE:
                exported_content = joins(
                    [self._export(head).replace("|", "&#124;") for head in
                     content.attributes['headers']],
                    before="| ", after=" |\n", between_each=" | "
                )

                exported_content += joins(
                    ["---" for _ in content.attributes['headers']],
                    before="| ", after=" |\n", between_each=" | "
                )

                for row in content.attributes['rows']:
                    exported_content += joins(
                        [self._export(cell.content).replace("|", "\|") for cell in row.cells],
                        before="| ", after=" |\n", between_each=" | "
                    )

            case ContentType.LINK:
                if 'internal-link' in content.attributes and content.attributes['internal-link']:
                    exported_content = f"[[{content.attributes['text']}]]"
                else:
                    exported_content = f"[{content.attributes['text']}" \
                                       f"({content.attributes['target'].replace(' ', '%20')})]"

            case _:
                raise NotImplementedError(f'Type {content.type} is not implemented'
                                          f'yet for {self.__class__.__name__}')

        return exported_content
