"""
Article for Documentation
"""
import logging
from pathlib import Path
import re
from typing import List

from chardon.article_builder import Content, TextStyle, TableRow, Article,\
    TableOfContentABC, TableTableOfContent, CalloutType
from chardon.code_parser.structure import ArrayOfType, DictOfType, SpecificType,\
    Parameter, Function, ClassVariant, Field, Type, Class

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
            if '\n' in tag.content:
                logging.warning("Summary of %s contains more than one line."
                                " It may lead to incorrect formatting", field.name)
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
        return Content.Link(type_.name, type_.attributes['uri'],
                            attributes={'link_to_another_page': True})
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

    return Content.FromText(type_.name)


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


def _get_field_types(field: Field) -> Content:
    """
    Convert field types to Contents
    @param field: Field
    @return Content
    """
    span: Content
    if isinstance(field.type, Function):
        if len(field.type.outputs) == 0:
            return Content.Span([])
        span = param_list_representation(field.type.outputs)
    else:
        span = type_representation(field.type)
    span.attributes['style'] = TextStyle.BOLD
    return span


def _get_default_value(field: Field) -> Content:
    """
    Return the representation of a field's default value
    @param field: Field
    @return: Content
    """
    if field.default_value != "":
        return Content.Title(f"= {field.default_value}", 6)
    return Content.Span([])


def _get_field_head(field: Field) -> Content:
    """
    Return the head of a field representation
    @param field: Field
    @return: Content
    """
    # Field name
    field_title: Content = Content.Title(field.name, level=2)
    # Return type of function or type of Field
    field_type: Content = _get_field_types(field)
    # Field scope (public, private, protected)
    field_scope: Content = Content.Span([Content.FromText(field.scope.name)], TextStyle.ITALIC)

    field_default_value: Content = _get_default_value(field)

    return Content.Span([field_title, field_default_value, Content.Span([
        field_scope,
        field_type
    ], attributes={'separator': ' '})])


def _get_function_inputs(function: Function, params_comment: dict[str: str]) -> Content:
    """
    Return the representation of a function's inputs
    @param function: Function
    @return: Content
    """
    table = Content.Table(["Inputs", "Type", "Description"], [])

    param: Parameter
    for param in function.inputs:
        if param.name not in params_comment:
            raise DocumentationError(f"missing {param.name} documentation")

        table.add_row(TableRow([
            Content.FromText(param.name),
            param_representation(param),
            Content.FromText(params_comment[param.name])
        ]))

    return table


def heritage_to_content(inherits: List[Type]) -> Content:
    """
    Export herited class to content
    @param inherits: heritage
    @return: Content
    """
    return Content.Span([
        Content.FromText("Herits from : "),
        Content.Span([
            type_representation(type_) for type_ in inherits
        ], attributes={'separator': ', '})
    ], TextStyle.BOLD)


class DocumentationError(Exception):
    """
    Error in the documentation, such as missing comment
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f'{self.message}'


class DocArticle(Article):
    """
    Generate an Article from a Class
    """
    TABLE_OF_CONTENT: type[TableOfContentABC] = TableTableOfContent

    def __init__(self, class_: Class, path: Path):
        super().__init__()
        self.class_ = class_
        self.presentation = Content.Section([])

        self.set_metadata('title', self.class_.name)
        self.set_metadata('path', str(path))
        self.set_metadata('scope', str(self.class_.scope.name))
        self.add_tag("class")
        self.add_alias(beautiful_class_name(self.class_.name))

        if self.class_.variant != ClassVariant.NONE:
            self.set_metadata('variant', str(self.class_.variant.name))

        # Class modificator, such as [Serializable'] or @Data are called attributes
        # This is a bit confusing as the dict holding customisations is called the same
        # So we get class attributes from customisation
        if 'attributes' in self.class_.attributes:
            self.set_metadata('attributes', self.class_.attributes['attributes'])

        if len(self.class_.inherits) > 0:
            self.presentation.add_children(heritage_to_content(self.class_.inherits))

        # Parse class comments
        for type_, comment in self.class_.attributes.get('comments', {}).items():
            match type_:
                case 'summary':
                    self.presentation.add_children(Content.FromText(comment.content))
                case 'remarks':
                    self.presentation.add_children(
                        Content.QuoteText(comment.content,
                                          attributes={'callout': CalloutType.INFO}))
                case _:
                    pass
                    # self.presentation.add_children(
                    #     Content.QuoteText(comment.content,
                    #                       attributes={
                    #                           'callout': ObsidianCalloutType.INFO,
                    #                           'callout-title': type_
                    #                       }))

        for field in self.class_.fields:
            try:
                self.add_field(field)
            except DocumentationError as e:
                logging.error("Error at %s.%s : %s", class_.name, field.name, e)

    def add_field(self, field: Field):
        """
        Add a class field in the article
        @param field: Field
        """
        summary: str = find_summary(field)

        # Add entry to table of content
        self.table_of_contents.add_entry(field.name, field.name, summary)

        self.add_content(_get_field_head(field))
        self.add_content(Content.FromText(summary))

        if isinstance(field.type, Function) and len(field.type.inputs) > 0:
            self.add_content(_get_function_inputs(field.type, field.attributes.get('params', {})))

    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header, self.presentation, Content.Separator()] \
               + self.table_of_contents.get_contents() + self.contents
