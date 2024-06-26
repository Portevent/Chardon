"""
Article for Documentation
"""
import logging
from pathlib import Path
import re
from typing import List

from src.article_builder.content.article import Article
from src.article_builder.content.content import Content, TableRow, TextStyle
from src.article_builder.exporter.osbidian_flavored_markdown_exporter import ObsidianCalloutType
from src.code_parser.structure.array_of_type import ArrayOfType
from src.code_parser.structure.dict_of_type import DictOfType
from src.code_parser.structure.specific_type import SpecificType
from src.code_parser.structure.class_ import Class, ClassVariant
from src.code_parser.structure.field import Field
from src.code_parser.structure.function import Function
from src.code_parser.structure.parameter import Parameter
from src.code_parser.structure.type import Type

SUMMARY_MAX_SIZE = 100


def beautiful_class_name(text: str) -> str:
    """
    Rearrange class name from MyName to My Name
    @param text: class name
    @return: beautiful
    """
    return re.sub(r"(\w)([A-Z])", r"\1 \2", text)


def find_summary(field: Field) -> str:
    """
    Find summary from a Field
    @param field: Field
    @return: Summary
    """
    if 'comments' in field.attributes:
        if 'summary' in field.attributes['comments']:
            tag = field.attributes['comments']['summary']
            if len(tag.content) > SUMMARY_MAX_SIZE:
                logging.warning("Summary of %s is a too long : %s", field.name, len(tag.content))
            return tag.content

    logging.error("Summary of %s is missing", field.name)
    return "*missing summary*"


def type_representation(type_: Type | Class) -> Content:
    """
    Convert type to str, or link to their Class
    @param type_: Type
    @return: Content
    """
    if isinstance(type_, Class):
        return Content.Link(type_.name, type_.attributes['uri'])
    if isinstance(type_, ArrayOfType):
        return Content.Span([type_representation(type_.type_), Content.FromText("[]")])
    if isinstance(type_, DictOfType):
        return Content.Span([
            Content.FromText('Dict{'),
            type_representation(type_.key),
            Content.FromText(' : '),
            type_representation(type_.value),
            Content.FromText('}')
        ])
    if isinstance(type_, SpecificType):
        span: Content = Content.Span([
            type_representation(type_.type_),
            Content.FromText('<'),
            type_representation(type_.specific1),
        ])

        if type_.specific2 is not None:
            span.add_children(Content.FromText(', '))
            span.add_children(type_representation(type_.specific2))


        span.add_children(Content.FromText('>'))

        return span

    return type_.name


def param_representation(params: Parameter) -> Content:
    """
    Represent a Parameter to a list of their possible types
    @param params: Parameter
    @return: List of Content
    """
    return Content.Span([
            type_representation(type_) for type_ in params.types
        ], attributes={'separator': ' or '})


def param_list_representation(params: List[Parameter]) -> Content:
    """
    Represent a list of params
    @param params: Params
    @return: List of Content
    """
    return Content.Span(
        [param_representation(param) for param in params],
        attributes={'separator': ' | '})


class DocArticle(Article):
    """
    Generate an Article from a Class
    """

    def __init__(self, class_: Class, path: Path):
        super().__init__()
        self.class_ = class_
        self.presentation = Content.Section([])
        self.table_of_content = Content.Table(['Name', 'Description'], [])

        self.set_metadata('title', self.class_.name)
        self.set_metadata('path', str(path))
        self.set_metadata('scope', str(self.class_.scope))
        self.add_tag("class")
        self.add_alias(beautiful_class_name(self.class_.name))

        if self.class_.variant != ClassVariant.NONE:
            self.set_metadata('variant', str(self.class_.variant))

        # Class modificator, such as [Serializable'] or @Data are called attributes
        # This is a bit confusing as the dict holding customisations is called the same
        # So we get class attributes from customisation
        if 'attributes' in self.class_.attributes:
            self.set_metadata('attributes', self.class_.attributes['attributes'])

        # Parse class comments
        for type_, comment in self.class_.attributes.get('comments', {}).items():
            match type_:
                case 'summary':
                    self.presentation.add_children(Content.FromText(comment.content))
                case 'remarks':
                    self.presentation.add_children(
                        Content.QuoteText(comment.content,
                                          attributes={'callout': ObsidianCalloutType.INFO}))
                case _:
                    self.presentation.add_children(
                        Content.QuoteText(comment.content,
                                          attributes={
                                              'callout': ObsidianCalloutType.INFO,
                                              'callout-title': type_
                                          }))

        for field in self.class_.fields:
            self.add_field(field)

    def _get_field_types(self, field: Field) -> Content:
        """
        Convert field types to Contents
        @param field: Field
        @return Content
        """

        if isinstance(field.type, Function):
            return param_list_representation(field.outputs)
        return type_representation(field.type)

    def _get_field_head(self, field: Field) -> Content:
        """
        Return the head of a field representation
        @param field: Field
        @return: Content
        """
        # Field name
        field_title: Content = Content.Title(field.name, level=2)
        # Return type of function or type of Field
        field_type: Content = Content.Span([self._get_field_types(field)], TextStyle.BOLD)
        # Field scope (public, private, protected)
        field_scope: Content = Content.Span([Content.FromText(field.scope.name)], TextStyle.ITALIC)

        return Content.Span([field_title, Content.Span([
            field_scope,
            field_type
        ], attributes={'separator': ' '})])

    def _get_default_value(self, field: Field) -> Content:
        """
        Return the representation of a field's default value
        @param field: Field
        @return: Content
        """

        return Content.FromText(f"Default value : {field.default_value}")

    def _get_function_inputs(self, function: Function) -> Content:
        """
        Return the representation of a function's inputs
        @param function: Function
        @return: Content
        """
        table = Content.Table(["Name", "Type", "Description"], [])

        param: Parameter
        for param in function.inputs:
            table.add_row(TableRow([
                Content.FromText(param.name),
                param_representation(param),
                Content.FromText("Not Implemented")
            ]))

        return table

    def add_field(self, field: Field):
        """
        Add a class field in the article
        @param field: Field
        """
        summary: str = find_summary(field)

        # Add entry to table of content
        self.table_of_content.add_row(TableRow([
            Content.InternalLink(field.name),
            Content.FromText(summary)
        ]))

        self.add_content(self._get_field_head(field))
        self.add_content(Content.FromText(summary))

        if field.default_value is not None:
            self.add_content(self._get_default_value(field))

        if isinstance(field.type, Function):
            self.add_content(self._get_function_inputs(field))


    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header, self.presentation, Content.Separator(), Content.Title("Summary :"),
                self.table_of_content, Content.Separator()] + self.content
