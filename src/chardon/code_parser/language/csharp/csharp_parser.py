"""
Selective C# Parser
"""
import logging
from typing import List

# pylint: disable=too-few-public-methods
from chardon.code_parser.language.csharp.csharp_block_parsing import Block, \
    _parse_block, _clean_line
from chardon.code_parser.language import LanguageParser, ParsingError
from chardon.code_parser.structure import Class, Field


class CSharpParser(LanguageParser):
    """
    C# Parser to extract Class and Functions from a File
    Note : this is a selective parser, it will only parse documented code
    Algorithm explanation :

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
    caught block inside it except when the catch block's
    Declaration is another class or struct.
    This is a greedy approach and can lead to a lot of issues :
    if two class are in the same file, but one of them is not commented,
    all fields will be mistakenly associated to the first class
    Correctly counting opening and closing brackets,
    avoiding those in comments and string is out of scope yet.
    This issue will only occurs times to times,
    but user may have hard times understanding how fields can be properly parsed but
    mistakenly placed in another class.
    I will open an Issue on Github to keep track of it for latter,
    and meanwhile a message will be displayed when a class has been
    parsed in the file and the language read another 'class' somewhere else
    """

    def _parse(self, lines: List[str]) -> List[Class]:
        """
        """
        blocks: List[Block] = self._parse_raw_code(lines)
        classes: List[Class] = []
        current_class: Class | None = None

        # Parse all block
        for block in blocks:
            try:
                res: Class | Field = _parse_block(block)
            except ParsingError as e:
                raise e
            except NotImplementedError as e:
                logging.warning(e)
                continue
            except Exception as e:
                raise ParsingError(str(e), line=block.comment + "\n" + block.declaration) from e

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

        multilines_comment_in_declaration: bool = False

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

                # Check for comments
                comment_index = line.find("//")
                if comment_index != -1:
                    line = line[:comment_index]

                # If inside a multilines comment, check for the end of it
                if multilines_comment_in_declaration:
                    end_multi_comment = line.find("*/")
                    if end_multi_comment != -1:
                        line = line[end_multi_comment:]
                        multilines_comment_in_declaration = False
                    else:
                        continue

                # Check for multilines comment
                multi_comment = line.find("/*")
                if multi_comment != -1:
                    line = line[:multi_comment]
                    multilines_comment_in_declaration = True

                # We reached the end of the declaration
                if '{' in line:
                    current_declaration += line.split('{')[0]  # Get the name before the line
                    inside_code = False

                # We reached the end of the declaration
                if ';' in line:
                    current_declaration += line.split(';')[0]  # Get the name before the line
                    inside_code = False

                # If we are no longer inside declaration (we hit either { or ;)
                if not inside_code:
                    blocks.append(Block(current_comment, current_declaration))

                    # Reset value
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
                if self.parameters.get('analyse_uncommented_code', False):
                    if 'class' in line:
                        logging.info("Undocumented class at %s %s", index, line)

        return blocks
