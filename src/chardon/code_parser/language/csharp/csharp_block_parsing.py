# pylint: disable=line-too-long
"""
C# Parser
"""
import logging
import re
from typing import List

import regex

from chardon.code_parser.language import ParsingError
from chardon.code_parser.structure import Scope, Type, DictOfType, ArrayOfType, SpecificType, Parameter, Class, Field, \
    ClassVariant, Function

SCOPES = {
    'public': Scope.PUBLIC,
    'protected': Scope.PROTECTED,
    'private': Scope.PRIVATE,
    'internal': Scope.INTERNAL,
    'protected internal': Scope.PROTECTED,
    'private protected': Scope.PRIVATE,
    'internal protected': Scope.PROTECTED,
    'protected private': Scope.PRIVATE,
}
# Parse
# [Serializable] public static class AnimationManager
# private static List<(int startIdx, int endIdx)> _blockTextIdxs = new List<(int startIdx, int endIdx)>(128);
# public static void AddAnimation(AnimationData animationData)
# into [attribute(s)] [declaration] : [inheritance(s)] for classes
# into [attribute(s)] [declaration]([parameters]) for functions
# into [attribute(s)] [declaration] [= default_value] for fields
BLOCK_REGEX = r'(?P<attributes>\[.*\])? ?(?P<declaration>(?:(?<keyword>[\w]+(<(((?&keyword) ?,? ?(?&keyword)?)|(\([\w ,]+\)))>)?(\[\])?) ?)+)(\((?P<parameters>[^;]*)\))?(?P<inheritance> ?: ?[^=;]+)?( ?= ?(?P<default_value>[^;]+))?'

# Parse string with one or multiple attribute(s)
# [Attribute A] [Attribute B] [Attribute <C,dE>]
# into a list of each
ATTRIBUTE_REGEX = r'\[(?P<attribute>.*?)\]'

# Parse a declaration into keywords
# public static class AnimationManager
# private static List<(int startIdx, int endIdx)> _blockTextIdxs
# public static List<A> AddAnimation
# public static st<A, C> AddAnimation
# For instance, the List<...> in the 2nd example must be parsed as one big keyword
# Each of this example has 4 keywords, but they may have more or less
DECLARATION_REGEX = r'(?<keyword>[\w]+(<(((?&keyword) ?,? ?(?&keyword)?)|(\([\w ,]+\)))>)?)'

# Parse class inheritance(s)
# Vehicle, Animal, Person (as in "class Transformer : Vehicle, Animal, Person")
# Into a list of class inherited
INHERIT_REGEX = r'(?P<inherit>\w+)'

# Parse one or multiple attributes
# out Dictionary<Type, List<int>> s_InterfaceEventSystemEvents = null, List<GUIContent> s_PossibleEvents = null, Coordinate coordinate, in Pattern pattern, int minRange, A<B<C, D>, E> variable_tricky = C<A, B>
# Into a list of each of them
# [modificator] [type] [name] [= default_value]
PARAMETER_REGEX = r'(?P<modificator>in |out |ref readonly |ref )?(?P<type>[\w\.]+?(?P<inside_type>\<.*?\>)?(?P<is_array>\[\])? )?>?(?P<name>\w+) ?(?P<def_value>= ?[\w\-\'\"\{\}]+(?P<inside_def_value>\<.*?\>)?)?'

# Parse comment
#     /// <summary>
#     /// Queue a new animation
#     /// </summary>
#     /// <param name="animationData">AnimationData to queue</param>
# Into a list of each of them
# <[tag] [params]>Content</[tag]>
COMMENT_REGEX = r'<(?P<name>\w+)(?P<params>[^>]*)>(?P<content>.*?)<\/(?P=name)>'

# Parse params in tag comment
# to="AnimationData" toLabel="Queue of"
# (as in /// <link to="AnimationData" toLabel="Queue of">Process</link>)
# Into a list of each of them
# [key] = "[value]"
COMMENT_TAG_ATTRIBUTES_REGEX = r'(?P<key>[\w\-\_]+) ?= ?(?P<quote>[\'\"])(?P<value>.+?)(?P=quote)'

# Parse a type
# int
# List<int>
# Type<A<B, C<E>>, D>
# Into their name and specification (List<int> -> name=List | type1=int)
TYPE_REGEX = r'(?P<type>(?P<name>\w+)(?P<specification><(?&type) ?,? ?(?&type)?>)?)'

MODIFIERS = [
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
]  # NOTE : Is internal or partial missing ?


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


def _parse_inheritance(text: str) -> List[Type]:
    """
    Parse text to a list of Inheritance
    @param text: Input
    @return: List of classes
    """
    return [Type(inherit) for inherit in re.findall(INHERIT_REGEX, text)]


def _parse_type(text: str) -> Type:
    """
    Parse a string into a Type
    @param text: input
    @return: Type
    """
    match = regex.match(TYPE_REGEX, text)
    if match is None:
        raise Exception(f"Could not parse type {text}")
    _, name, specification = match.groups()

    if specification is not None:
        if name == "Dictionary":
            key, value = [match[0] for match in regex.findall(TYPE_REGEX, specification)]
            return DictOfType(key, value)
        if name == "List":
            return ArrayOfType(_parse_type(specification))

        specifics = [match[0] for match in regex.findall(TYPE_REGEX, specification)]
        return SpecificType(Type(name), specifics[0] or None, specifics[1] or None)
    return Type(name)


def _parse_parameter(text: str) -> List[Parameter]:
    """
    Parse text to Parameters
    @param text: Input
    @return: Parameters
    """
    parameters: List[Parameter] = []
    for modification, raw_type, _, _, name, def_value, _ in re.findall(PARAMETER_REGEX, text):
        attributes: dict[str: str] = {}
        if modification != "":
            attributes['modification'] = modification

        type_: Type = _parse_type(raw_type)
        parameters.append(Parameter(name, [type_], "", default_value=def_value if def_value != "" else None,
                                    attributes=attributes))

    return parameters


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


def _parse_comment(text: str) -> dict:
    """
    Parse a comment into an attribute dict
    @param text: Input
    @return: Dict
    """
    attributes: dict = {
        'params': {},
        'exceptions': {},
        'returns': {},
        'comments': {}
    }
    for tag_name, params, content in re.findall(COMMENT_REGEX, text, re.DOTALL):
        tag_attributes = _parse_comment_tag(params)
        content = content.strip()
        match tag_name:
            case "param":
                attributes['params'][tag_attributes['name']] = content
            case "exception":
                attributes['exceptions'][tag_attributes['cref']] = ""
            case "returns":
                attributes['exceptions']['default'] = content
            case _:
                attributes['comments'][tag_name] = TagComment(tag_name, content,
                                                              attributes=_parse_comment_tag(params))

    # Return only non-empty items
    return {k: v for k, v in attributes.items() if v}


def _find_scope(keywords: List[str], pop: bool = True) -> (Scope, List[str]):
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
def _parse_declaration(declaration: str) -> [str, str, str, List[str]]:
    """
    Parse declaration into a field name, a field scope, modifiers and keywords
    @param declaration:
    @return: name, scope, modifiers, List of keywords
    """
    keywords = [result[0] for result in regex.findall(DECLARATION_REGEX, declaration)]
    name: str = keywords.pop()
    scope, keywords = _find_scope(keywords)

    # Class or Function modifier are specific tag before a name, such as static or abstract
    modifiers: List[str] = []
    for modifier in MODIFIERS:
        if modifier in keywords:
            keywords.remove(modifier)
            modifiers.append(modifier)

    return name, scope, modifiers, keywords


def _parse_block(block: Block) -> Class | Field:
    declaration: str = block.declaration
    declaration.replace('\n', ' ')

    match = regex.match(BLOCK_REGEX, declaration)
    if match is {}:
        raise Exception(f"Invalid declaration : {block.declaration}")
    parts: dict = match.groupdict()

    attributes: dict = _parse_comment(block.comment)

    attributes['attributes'] = _parse_attributes(parts['attributes'] or "")

    inheritance: List[Type] = _parse_inheritance(parts['inheritance'] or "")
    parameters: List[Parameter] = _parse_parameter(parts['parameters'] or "")

    name: str
    scope: Scope
    modifiers: List[str]
    keywords: List[str]
    name, scope, modifiers, keywords = _parse_declaration(parts['declaration'])

    if len(modifiers) > 0:
        attributes['modifiers'] = modifiers

    result: Class | Field

    # Is a Class
    if 'class' in keywords:
        keywords.remove('class')

        result = Class(name, [], "", scope, inheritance, attributes=attributes)

    # Is a Struct
    elif 'struct' in keywords:
        keywords.remove('struct')

        result = Class(name, [], "", scope,
                       [], ClassVariant.STRUCT, attributes=attributes)

    # Is an Enum
    elif 'enum' in keywords:
        keywords.remove('enum')

        result = Class(name, [], "", scope,
                       [], ClassVariant.ENUM, attributes=attributes)

    # Is a Function
    elif parts['parameters'] is not None:

        return_types: List[Parameter] = []
        if len(keywords) == 1:
            return_type = keywords.pop()
            if return_type != "void":
                return_types.append(Parameter('', [Type(return_type)]))
        else:
            raise ParsingError(f"Can't tell what is the return "
                               f"type of {name} : {block.declaration}")

        function = Function(parameters, return_types)

        result = Field(name, function, scope, attributes=attributes)

    else:
        result = Field(name, Type(keywords.pop()), scope, default_value=parts['default_value'], attributes=attributes)

    if len(keywords) > 0:
        logging.warning("%s has unkown keywords : %s, will be ignored", result, keywords)

    return result
