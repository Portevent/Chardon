"""
Parse a project and export classes
"""
import re
from pathlib import Path
from typing import List

from article_builder.content.content import Content
from article_builder.exporter.content_export import ContentExport
from code_parser.language.parser import Parser
from code_parser.structure.array_of_type import ArrayOfType
from code_parser.structure.class_ import Class
from code_parser.structure.function import Function


# pylint: disable=too-few-public-methods
class ParsingResult:
    """
    Result of file parsing
    """
    def __init__(self, file: Path, clean_path: Path, results: List[Class]):
        self.file = file
        self.clean_path = clean_path
        self.results = results


# pylint: disable=too-few-public-methods
class ProjectManager:
    """
    Scan a project and parse all file within it
    """

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-instance-attributes
    # TODO : Remove the too-many-nested-blocks as ### 1 get reworked
    def __init__(self, parser: Parser, exporter: ContentExport,
                 directory: Path, out_directory: Path, file_regex: str = r'.*', encoding="utf-8"):
        self.parser = parser
        self.exporter = exporter
        self.directory = directory
        self.out_directory = out_directory
        self.file_regex = file_regex
        self.encoding = encoding
        self.results: List[ParsingResult] = []
        self.classes: dict[str: Class] = {}

        # Parse all files
        self.parse(self.directory, Path(''))
        class_: Class

        # Loop through known class and replace type to their actual class
        # When we parse the code, we don't know if a class will be parsed, thus
        # most type are saved as string first, and we have to correctly reference them afterwards
        for class_ in self.classes.values():
            for inherit in class_.inherits:
                if isinstance(inherit, str) and inherit in self.classes:
                    # TODO : This doesn't update value within class
                    inherit = self.classes[inherit]

            for field in class_.fields:
                if isinstance(field.type, str) and field.type in self.classes:
                    field.type = self.classes[field.type]

                if isinstance(field.type, Function):
                    ### 1 - TO REWORK
                    for param in field.type.inputs:
                        for type_ in param.types:
                            if type_.name in self.classes:
                                if isinstance(type_, ArrayOfType):
                                    # TODO : This doesn't update the element within the Function
                                    type_ = ArrayOfType(self.classes[type_.name])
                                else:
                                    type_ = self.classes[type_.name]
                    for param in field.type.outputs:
                        for type_ in param.types:
                            if type_.name in self.classes:
                                if isinstance(type_, ArrayOfType):
                                    type_ = ArrayOfType(self.classes[type_.name])
                                else:
                                    type_ = self.classes[type_.name]

    def parse(self, directory: Path, clean_path: Path):
        """
        Recursively parse all file inside a directory and save them in self.results
        @param directory: File path
        @param clean_path: Path from the root project
        """
        res: ParsingResult
        for path in directory.iterdir():
            if path.is_dir():
                self.parse(path, clean_path / path.name)
            elif re.match(self.file_regex, path.name):
                res = ParsingResult(path, clean_path / path.name, self.parser.parse(path))
                for class_ in res.results:
                    self.classes[class_.name] = class_
                self.results.append(res)

    def export(self):
        """
        Export all parsed classes
        """
        for result in self.results:
            for class_ in result.results:
                # TODO : Create DocArticle
                # contents = DocArticle(class_, result.clean_path.parent).to_contents()
                contents: List[Content] = []

                (self.out_directory / result.clean_path.parent).mkdir(parents=True, exist_ok=True)
                with open(self.out_directory / result.clean_path.parent /
                          (class_.name + self.exporter.PREFERRED_EXTENSION),
                          'w', encoding=self.encoding) as f:
                    f.write(self.exporter.export(contents))
