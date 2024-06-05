from enum import Enum, auto
from typing import List

from content import Content, ContentType


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
    return before + 
    between_each.join([before_each + element + after_each for element in elements])
     + after


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
    Markdown allows multiple way of formating breakline, this parameter ensure compatibility accross different Markdown interpreter
    """
    NONE = auto()  # Not doing anything
    TRAILING_WHITESPACE = auto()  # Adding two space
    BACKSLASH = auto()  # Using \
    BR_TAG = auto()  # Using <br>


class MarkdownContent(Content):
    """
    Export Content To Markdown
    """
    BREAKLINE: MarkdownContentBreaklineType = MarkdownContentBreaklineType.TRAILING_WHITESPACE

    def export(self) -> str:
        """
        Export content
        """
        breakline: str = {
            MarkdownContentBreaklineType.NONE: '\n',
            MarkdownContentBreaklineType.TRAILING_WHITESPACE: '  \n',
            MarkdownContentBreaklineType.BACKSLASH: '\\\n',
            MarkdownContentBreaklineType.BR_TAG: '<br>\n'
        }[MarkdownContent.BREAKLINE]  # Selecting the appropriate breakline

        return self._export().replace('\n', breakline)

    def _export(self) -> str:
        """
        Export content, without considering the breaklines yet
        """
        exported_content: str = ""
        match self.type:
            case ContentType.SEPARATOR:
                exported_content = '\n---\n'

            case ContentType.CODE:
                exported_content = joins(
                    before=f"```{self.attributes['language']}\n",
                    after="```",

                    elements=self.attributes['text'].split('\n'),
                    before_each="  ",
                    between_each="\n"
                )

            case ContentType.LIST:
                if self.attributes['ordered']:
                    exported_content = joins(
                        elements=[f'{i+1}. {element}' for i, element in self.attributes['children']],
                        between_each="\n"
                    )
                else:
                    exported_content = joins(
                        elements=list(map(clean_list_element, self.attributes['children'])),
                        before_each='- ',
                        between_each="\n"
                    )

            case ContentType.TEXT:
                exported_content = self.attributes['text']

            case ContentType.QUOTE:
                base_footer = "\n> "
                footer = base_footer

                # Creating the footer
                if self.attributes['author']:
                    footer += f" {self.attributes['author']}"
                if self.attributes['date']:
                    footer += f" {self.attributes['date']}"
                if self.attributes['location']:
                    footer += f" {self.attributes['location']}"

                if footer == base_footer:  # If the footer is empty, remove it
                    footer = ""

                exported_content = joins(
                    elements=self.attributes['quote'].export().split('\n'),
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
                    elements=[content.export() for content in self.attributes['children']],
                    between_each="\n"
                )

            case ContentType.IMAGE:
                exported_content = joins(
                    before=f"```{self.attributes['language']}\n",
                    after="```",

                    elements=self.attributes['text'].split('\n'),
                    before_each="  ",
                    between_each="\n"
                )

            case ContentType.TITLE:
                # Put blank line around the title, for best practices :
                # https://www.markdownguide.org/basic-syntax/#heading-best-practices
                exported_content = f"\n{'#' * self.attributes['level']} {self.attributes['text']}\n"

            case ContentType.TABLE:
                raise NotImplementedError 

        return exported_content
