"""
C# Parser
"""
import logging
import re
from typing import List

from code_parser.parser.parser import Parser, ParsingError
from code_parser.structure.class_ import Class, ClassVariant
from code_parser.structure.field import Field, Visibility
from code_parser.structure.function import Function
from code_parser.structure.parameter import Parameter

SCOPES = {
    'public': Visibility.PUBLIC,
    'protected': Visibility.PROTECTED,
    'private': Visibility.PRIVATE,
}

BLOCK_REGEX = r'(?P<attributes>\[.*\])? ?(?P<declaration>[\w ]+[\w]) ?:? ?' \
              r'(?P<parameters>\(.*\))?(?P<inheritance>.+)?'
ATTRIBUTE_REGEX = r'\[(?P<attribute>.*?)\]'
INHERIT_REGEX = r'(?P<inherit>\w+)'
PARAMETER_REGEX = r'(?P<modificator>in |out |ref readonly |ref )?(?P<type>[\w<>\[\]]+) ' \
                  r'(?P<name>\w+) ?=? ?(?P<def_value> ?[\w\'\"<>\{\}]+)?'
COMMENT_REGEX = r'<(?P<name>\w+)(?P<params>[^>]*)>(?P<content>.*?)<\/(?P=name)>'
COMMENT_TAG_ATTRIBUTES_REGEX = r'(?P<key>[\w\-\_]+) ?= ?(?P<quote>[\'\"])(?P<value>.+?)(?P=quote)'

FUNCTION_MODIFIERS = [
    'abstract',
    'async',
    'const',
    'extern',
    'in',
    'new',
    'out',
    'override',
    'readonly',
    'sealed',
    'static',
    'unsafe',
    'virtual',
    'volatile',
]


# pylint: disable=too-few-public-methods
class TagComment:
    """
    Tag in comments
    eg. <link to="EntityAI" type="double-arrow">Play turn</link>
    """

    def __init__(self, tag: str, content: str, attributes: dict = None):
        self.tag = tag
        self.content = content
        self.attributes = attributes or {}


# pylint: disable=too-few-public-methods
class Block:
    """
    C# code yet to be parsed
    """

    # I don't really like this name, can't find a better one
    def __init__(self, comment: str, declaration: str):
        self.comment = comment
        self.declaration = declaration


# pylint: disable=too-few-public-methods
def _parse_attributes(text: str) -> List[str]:
    """
    Parse text to a list of Attributes
    @param text: Input
    @return: List of attributes
    """
    return re.findall(ATTRIBUTE_REGEX, text)


def _parse_inheritance(text: str) -> List[str]:
    """
    Parse text to a list of Inheritance
    @param text: Input
    @return: List of classes
    """
    return re.findall(INHERIT_REGEX, text)


def _parse_parameter(text: str) -> List[Parameter]:
    """
    Parse text to a list of Parameter
    @param text: Input
    @return: List of Parameter
    """
    return [Parameter(name, _type, "",
                      default_value=def_value if def_value != "" else None,
                      attributes={'modificator': modificator})
            for modificator, _type, name, def_value in re.findall(PARAMETER_REGEX, text)]


def _parse_comment_tag(text: str) -> dict:
    """
    Parse a tag into a dict of attributes
    @param text: Input
    @return: Dict of attributes
    """
    res: dict = {}
    for key, _, value in re.findall(COMMENT_TAG_ATTRIBUTES_REGEX, text):
        res[key] = value
    return res


def _parse_comment(text: str) -> List[TagComment]:
    """
    Parse a comment into a doc dict
    @param text: Input
    @return: List of fields
    """
    return [TagComment(name, content, attributes=_parse_comment_tag(params))
            for name, params, content in re.findall(COMMENT_REGEX, text, re.DOTALL)]


def _find_scope(keywords: List[str], pop: bool = True) -> (Visibility, List[str]):
    """
    Find the score keyword among a list
    @param keywords: List of keywords
    @param pop: Remove it from the list
    @return: The score and the rest of the keywords
    """
    for keyword, scope in SCOPES.items():
        if keyword in keywords:
            if pop:
                keywords.remove(keyword)
            return scope, keywords

    raise ParsingError("No scope among keywords")


def _clean_line(line: str) -> str:
    """
    Clean a line from Byte Order Mask and trailing space
    @param line: input
    @return: Clean line
    """
    line = line.strip()
    # Clear Byte Order Mask from file
    if line.startswith("ï»¿"):
        line = line[len("ï»¿"):]
    if line.startswith("\ufeff"):
        line = line[len("\ufeff"):]

    return line


# pylint: disable=too-many-locals
def _parse_block(block: Block) -> Class | Field:
    declaration: str = block.declaration
    declaration.replace('\n', ' ')
    parts: dict = re.match(BLOCK_REGEX, declaration).groupdict()

    attributes: dict = {
        'attributes': _parse_attributes(parts['attributes'] or ""),
        'comments': _parse_comment(block.comment)
    }
    inheritance: List[str] = _parse_inheritance(parts['inheritance'] or "")
    parameters: List[Parameter] = _parse_parameter(parts['parameters'] or "")

    keywords = parts['declaration'].split(' ')
    name: str = keywords.pop()
    visibility: Visibility

    # Is a Class
    if 'class' in keywords:
        keywords.remove('class')

        try:
            visibility, keywords = _find_scope(keywords)
        except ParsingError as e:
            e.line = block.declaration
            raise e

        _class = Class(name, [], "", visibility, inheritance, attributes=attributes)

        return _class

    # Is a Struct
    if 'struct' in keywords:
        struct = Class(keywords[2], [], "", SCOPES[keywords[0]],
                       [], ClassVariant.STRUCT, attributes=attributes)

        return struct

    # Is a Function
    try:
        visibility, keywords = _find_scope(keywords)
    except ParsingError as e:
        e.line = block.declaration
        raise e

    modifiers: List[str] = []
    for modifier in FUNCTION_MODIFIERS:
        if modifier in keywords:
            keywords.remove(modifier)
            modifiers.append(modifier)

    if len(modifiers) > 0:
        attributes['modifiers'] = modifiers

    if len(keywords) == 1:
        return_type: Parameter = Parameter('', keywords[0])
    else:
        raise ParsingError(f"Can't tell what is the return"
                           f"type of {name} : {block.declaration}")

    function = Function(parameters, [return_type])

    return Field(name, function, visibility, attributes=attributes)


class CSharpParser(Parser):
    """

        CSharp code is structured as

        /// Comment ...
        Declaration
        {

        eg.

        /// <summary>
        /// blabla
        /// </summary>
        /// <remarks>
        /// more blabla
        /// </remarks>
        [Attributes]
        [...]
        public class MyClass : InheritsFrom
        {

        We thus approach the parsing with a simple method of looking for ///,
        buffering all comment, and then buffering all char until a { is found.
        There is probably some way to fit { inside the [custom tag],
        i'm not sure yet but will start with this and address this issue later.
        All this stuff will be called Block
        We will call Comment the text inside ///
        We will call Declaration all the text between Comment and {

        When we find a class | struct, we will store all further
        catched block inside it except when the catch block's
        Declaration is another class or struct.
        This is a greedy approach and can lead to a lot of issues :
        if two class are in the same file, but one of them is not commented,
        all fields will be mistakenly associated to the first class
        Correctly counting opening and closing brackets,
        avoiding thoses in comments and string is out of scope yet.
        This issue will only occurs times to times,
        but user may have hard times understanding how fields can be properly parsed but
        mistakenly placed in another class.
        I will open an Issue on Github to keep track of it for latter,
        and meanwhile a message will be displayed when a class has been
        parsed in the file and the parser read another 'class' somewhere else
    """

    def _parse(self, lines: List[str]) -> List[Class]:
        blocks: List[Block] = self._parse_raw_code(lines)
        classes: List[Class] = []
        current_class: Class | None = None

        # Parse all block
        for block in blocks:
            res: Class | Field = _parse_block(block)

            # Focus on the new class
            if isinstance(res, Class):
                if current_class:
                    classes.append(current_class)
                current_class = res

            # Insert field in class
            else:
                if current_class:
                    current_class.add_field(res)
                else:
                    raise ParsingError(message=f"We are parsing {res.name} outside of a class",
                                       line=block.declaration)

        if current_class:
            classes.append(current_class)

        return classes

    # pylint: disable=too-many-branches
    def _parse_raw_code(self, lines: List[str]) -> List[Block]:
        """
        Parse all Comment and associated Declaration
        @param lines: raw code
        @return: List of comment and declaration
        """
        blocks: List[Block] = []
        inside_code: bool = False

        current_comment: str = ""
        current_declaration: str = ""

        for index, line in enumerate(lines):
            line = _clean_line(line)

            # Append any comment inside /// to current_comment
            if line.startswith("///"):
                if inside_code:
                    current_comment += "\n"
                else:
                    inside_code = True

                current_comment += line[3:].strip()  # Remove the '///'

            # Double check for missing format char
            elif '///' in line:  # Pretty intolerant tbh
                raise ParsingError(f"Line contains /// but doesn't start with it (found {line[0]})",
                                   line=line, line_number=index)

            # If there is no comment
            # but we were in a comment before,
            # find the associated declaration
            elif inside_code:
                # We reached the end of the declaration
                if '{' in line:
                    current_declaration += line.split('{')[0]  # Get the name before the line
                    blocks.append(Block(current_comment, current_declaration))

                    # Reset value
                    inside_code = False
                    current_comment = ""
                    current_declaration = ""

                # Keep track of everything until the associated class / struct / function is found
                else:
                    current_declaration += line

            # Uncommented code
            else:
                if 'class' in line and len(blocks) > 0:
                    logging.info("Undocumented class at %s %s, this can lead to parsing error"
                                 " (issue will be created to explain further how this is a problem",
                                 index, line)
                if 'struct' in line and len(blocks) > 0:
                    logging.info("Undocumented struct at %s %s, this can lead to parsing error"
                                 " (issue will be created to explain further how this is a problem",
                                 index, line)

                # pylint: disable=W0511
                # Todo : add code coverage test and such, not in the project scope yet
                if self.parameters.get('analyse_uncommentend_code', False):
                    if 'class' in line:
                        logging.info("Undocumented class at %s %s", index, line)

        return blocks
