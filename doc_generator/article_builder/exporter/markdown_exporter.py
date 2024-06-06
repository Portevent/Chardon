"""implementation of export content to Markdown"""
from enum import Enum, auto
from typing import List

from doc_generator.article_builder.content import ContentType, Content, TextStyle
from doc_generator.article_builder.exporter.content_export import ContentExport


# pylint: disable=too-many-arguments
def joins(elements: List[str], before: str = '', before_each: str = '',
          after: str = '', after_each: str = '', between_each: str = ''):
    """
    Convert a list into a string
    :param elements: list
    :param before: Text before the list
    :param before_each: Text before each element of the list
    :param after: Text after the list
    :param after_each: Text after each element of the list
    :param between_each: Text between each element of the list
    :return: string
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
    :param element: Element to clean
    :return: Unambiguous text
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
    BREAKLINE: MarkdownContentBreaklineType = MarkdownContentBreaklineType.BACKSLASH

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

        text = "".join([MarkdownContentExport._export(content) for content in contents])

        return text.replace('\n', breakline)

    @staticmethod
    def _export(content: Content) -> str:
        """
        Export content, without considering the breaklines yet
        """
        exported_content: str = ""
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

            case ContentType.LIST:
                if content.attributes['ordered']:
                    exported_content = joins(
                        elements=[f'{i + 1}. {element}' for i, element
                                  in content.attributes['children']],
                        between_each="\n"
                    )
                else:
                    exported_content = joins(
                        elements=list(map(clean_list_element, content.attributes['children'])),
                        before_each='- ',
                        between_each="\n"
                    )

            case ContentType.TEXT:
                exported_content = content.attributes['text']

            case ContentType.SPAN:
                exported_content = "".join([
                    MarkdownContentExport._export(children)
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
                if content.attributes['author']:
                    footer += f" {content.attributes['author']}"
                if content.attributes['date']:
                    footer += f" {content.attributes['date']}"
                if content.attributes['location']:
                    footer += f" {content.attributes['location']}"

                if footer == base_footer:  # If the footer is empty, remove it
                    footer = ""

                exported_content = joins(
                    elements=content.attributes['quote'].export().split('\n'),
                    before_each="> ",
                    between_each="\n",

                    # Put blank line around the quote, for best practices :
                    # https://www.markdownguide.org/basic-syntax/#blockquotes-best-practices
                    before="\n",
                    after=footer + "\n"
                )

            case ContentType.HEADER:
                raise NotImplementedError

            case ContentType.SECTION:
                exported_content = joins(
                    elements=[content.export() for content in content.attributes['children']],
                    between_each="\n"
                )

            case ContentType.IMAGE:
                exported_content = joins(
                    before=f"```{content.attributes['language']}\n",
                    after="```",

                    elements=content.attributes['text'].split('\n'),
                    before_each="  ",
                    between_each="\n"
                )

            case ContentType.TITLE:
                # Put blank line around the title, for best practices :
                # https://www.markdownguide.org/basic-syntax/#heading-best-practices
                exported_content = f"\n{'#' * content.attributes['level']}" \
                                   f" {content.attributes['text']}\n"

            case ContentType.TABLE:
                raise NotImplementedError

        return exported_content
