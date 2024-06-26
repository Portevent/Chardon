"""
Parse a project and export classes
"""
import re
from pathlib import Path
from typing import List

from src.article_builder.content.content import Content
from src.article_builder.content.documentation import DocArticle
from src.article_builder.exporter.content_export import ContentExport
from src.code_parser.language.parser import Parser
from src.code_parser.structure.array_of_type import ArrayOfType
from src.code_parser.structure.class_ import Class
from src.code_parser.structure.function import Function

# pylint: disable=too-few-public-methods
from src.code_parser.structure.type import Type


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
            class_.inherits = list(map(self.type_to_class, class_.inherits))

            for field in class_.fields:
                field.type = self.type_to_class(field.type)

                if isinstance(field.type, Function):
                    for param in field.type.inputs:
                        param.types = list(map(self.type_to_class, param.types))

                    for param in field.type.outputs:
                        param.types = list(map(self.type_to_class, param.types))

    def type_to_class(self, type_: Type) -> Type:
        """
        Try to convert str-type to Class-type from known class
        @param type_: Type, which can be expressed as str
        @return: Corresponding Class if known
        """

        if isinstance(type_, ArrayOfType):
            return ArrayOfType(self.type_to_class(type_.type_))

        if isinstance(type_, Type) and type_.name in self.classes:
            return self.classes[type_.name]

        return type_

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
                    self.classes[class_.name].attributes['uri'] = clean_path / class_.name
                self.results.append(res)

    def export(self):
        """
        Export all parsed classes
        """
        for result in self.results:
            for class_ in result.results:
                contents: List[Content] = DocArticle(class_, result.clean_path.parent).to_contents()

                (self.out_directory / result.clean_path.parent).mkdir(parents=True, exist_ok=True)
                with open(self.out_directory / result.clean_path.parent /
                          (class_.name + self.exporter.PREFERRED_EXTENSION),
                          'w', encoding=self.encoding) as f:
                    f.write(self.exporter.export(contents))
