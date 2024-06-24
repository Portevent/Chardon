"""Parsing MD string into Contents"""
import re
from typing import List

from src.article_builder.content.content import Content, TextStyle
from src.article_builder.parser.text_parser import TextParser


class MarkdownParserBuffer:
    """
    Struct holding information used during parsing
    """

    def __init__(self):
        self.text = ""
        self.asterisk_counter = 0
        self.underscore_counter = 0

    def add(self, text: str):
        """
        Append text à the end of the buffer
        @param text:
        """
        self.text += text

    def reset(self):
        """
        Reset parameters to default values
        """
        self.text = ""
        self.asterisk_counter = 0
        self.underscore_counter = 0


class MarkdownParser(TextParser):
    """
    Parse Markdown strings into Content
    """

    italicRegex = {
        '_': r"(?P<text>.*?[^\\])\_",
        '*': r"(?P<text>.*?[^\\])\*"
    }

    boldRegex = {
        '_': r"(?P<text>.*?[^\\])\_\_",
        '*': r"(?P<text>.*?[^\\])\*\*"
    }

    italicBoldRegex = {
        '_': r"(?P<text>.*?[^\\])\_\_\_",
        '*': r"(?P<text>.*?[^\\])\*\*\*"
    }

    linkRegex = r"(?P<text>.*?)]\((?P<url>[^ ]+?)(?P<title> \".*?[^\\]\")?\)"

    def __init__(self, text: str):
        super().__init__(text)
        self._buffer = MarkdownParserBuffer()
        self._enum = None
        self._enum_index = 0
        self._contents: List[Content] = []

    def set_text(self, text: str):
        """
        Set the text to be parsed
        @param text: new text
        """
        self._text = text

    def _start_enum_text(self):
        """
        Setup the enumerator at the beginning of the text
        """
        self._enum = enumerate(self._text)
        self._enum_index = 0

    def _enum_text(self) -> (int, str):
        """
        Return the next char in text
        @return: The position and the next char
        """
        try:
            index, char = next(self._enum)
        except StopIteration:
            return -1, None

        self._enum_index = index
        return index, char

    def _skip_enum_text_to(self, skip_to: int):
        """
        Advance in the enum to reach certain position
        @param skip_to: Position to reach
        """
        while self._enum_index + 1 < skip_to:
            self._enum_text()

    def _skip_enum_text(self, skips: int):
        """
        Skip a certain amount of char
        @param skips: Number of char to skip
        """
        for _ in range(skips):
            self._enum_text()

    def parse(self) -> List[Content]:
        self._start_enum_text()
        self._contents = []
        self._buffer.reset()

        self._parse()

        return self._contents

    def _match(self, regex: str):
        res = re.match(regex, self._text[self._enum_index:], re.S)
        if res is None:
            return {}, -1

        return res.groupdict(), self._enum_index + len(res.group())

    def _register_span(self, text: str, style: TextStyle):
        self._contents.append(Content.Span(MarkdownParser(text).parse(), style))

    def _register_text(self, text: str):
        self._contents.append(Content.Text(text))

    def _parse(self):
        escaped: bool = False

        char: str
        while True:
            _, char = self._enum_text()

            if char is None:
                break

            if escaped:
                self._buffer.text += char
                escaped = False
                continue

            if char == '\\':
                escaped = True
                continue

            if char == '*':
                self._buffer.asterisk_counter += 1
            elif self._buffer.asterisk_counter > 0:
                new_index = self._check_for_emphasis('*', self._buffer.asterisk_counter)
                if new_index != -1:
                    self._buffer.reset()
                    self._skip_enum_text_to(new_index)
                    continue

            if char == '_':
                self._buffer.underscore_counter += 1
            elif self._buffer.underscore_counter > 0:
                new_index = self._check_for_emphasis('_', self._buffer.underscore_counter)
                if new_index != -1:
                    self._buffer.reset()
                    self._skip_enum_text_to(new_index)
                    continue

            self._buffer.text += char

        self._register_text(self._buffer.text)

    def _check_for_emphasis(self, char: str, count: int):
        if count >= 3:
            res, new_index = self._match(MarkdownParser.italicBoldRegex[char])
            if new_index != -1:
                self._register_text(self._buffer.text[:-3])
                self._register_span(res['text'], TextStyle.ITALIC | TextStyle.BOLD)
                return new_index

        if count >= 2:
            res, new_index = self._match(MarkdownParser.boldRegex[char])
            if new_index != -1:
                self._register_text(self._buffer.text[:-2])
                self._register_span(res['text'], TextStyle.BOLD)
                return new_index

        if count >= 1:
            res, new_index = self._match(MarkdownParser.italicRegex[char])
            if new_index != -1:
                self._register_text(self._buffer.text[:-1])
                self._register_span(res['text'], TextStyle.ITALIC)
                return new_index

        return -1
