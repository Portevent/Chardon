from enum import Enum, auto
from typing import List

from content import Content, ContentType


def joins(elements: List[str], before: str = '', before_each: str = '', after: str = '', after_each: str = '',
          between_each: str = ''):
    return before + between_each.join([before_each + element + after_each for element in elements]) + after


class MarkdownContentBreaklineType(Enum):
    NONE = auto()  # Not doing anything
    TRAILING_WHITESPACE = auto()  # Adding two space
    BACKSLASH = auto()  # Using \
    BR_TAG = auto()  # Using <br>


class MarkdownContent(Content):
    BREAKLINE: MarkdownContentBreaklineType = MarkdownContentBreaklineType.TRAILING_WHITESPACE

    def export(self) -> str:
        breakline: str = {
            MarkdownContentBreaklineType.NONE: '\n',
            MarkdownContentBreaklineType.TRAILING_WHITESPACE: '  \n',
            MarkdownContentBreaklineType.BACKSLASH: '\\\n',
            MarkdownContentBreaklineType.BR_TAG: '<br>\n'
        }[MarkdownContent.BREAKLINE]  # Selecting the appropriate breakline

        return self._export().replace('\n', breakline)

    def _export(self) -> str:
        match self.type:
            case ContentType.SEPARATOR:
                return '---'

            case ContentType.CODE:
                return joins(
                    before=f"```{self.attributes['language']}\n",
                    after="```",

                    elements=self.attributes['text'].split('\n'),
                    before_each="  ",
                    between_each="\n"
                )

            case ContentType.LIST:
                return joins(
                    elements=self.attributes['children'],
                    before_each=f"- ",
                    between_each="\n"
                )

            case ContentType.TEXT:
                return self.attributes['text']

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

                return joins(
                    elements=self.attributes['text'].split('\n'),
                    before_each=f"> ",
                    between_each="\n",

                    after=footer
                )

            case ContentType.HEADER:
                raise NotImplemented

            case ContentType.SECTION:
                return joins(
                    elements=[content.export() for content in self.attributes['children']],
                    between_each="\n"
                )

            case ContentType.TITLE:
                return "#" * self.attributes['level'] + ' ' + self.attributes['text']

            case ContentType.TABLE:
                raise NotImplemented
