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
from src.code_parser.language.csharp import TagComment
from src.code_parser.structure.class_ import Class, ClassVariant
from src.code_parser.structure.field import Field
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
    comment: TagComment
    if 'comments' in field.attributes:
        if 'summary' in field.attributes['comments']:
            tag = field.attributes['comments']['summary']
            if len(tag.content) > SUMMARY_MAX_SIZE:
                logging.warning(f"Summary of {field.name} is a too long : {len(tag.content)}")
            return tag.content

    logging.error(f"Summary of {field.name} is missing")
    return "*missing summary*"


def link_to_type(type_: Type | str) -> Content:
    """
    Convert type to link
    @param type_: Type
    @return: Content
    """
    if isinstance(type_, str):
        return Content.FromText(type_)
    return Content.Link(type_.name, type_.name)


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
        self.set_metadata('visibility', str(self.class_.visibility))
        if self.class_.variant != ClassVariant.NONE:
            self.set_metadata('variant', str(self.class_.variant))

        self.add_alias(beautiful_class_name(self.class_.name))
        self.add_tag("class")

        # Class modificator, such as [Serializable'] or @Data are called attributes
        # This is a bit confusing as the dict holding customisations is called the same
        # So we get class attributes from customisation
        if 'attributes' in self.class_.attributes:
            self.set_metadata('attributes', self.class_.attributes['attributes'])

        for type, comment in self.class_.attributes.get('comments', {}).items():
            match type:
                case 'summary':
                    self.presentation.add_children(Content.FromText(comment.content))
                case 'remarks':
                    self.presentation.add_children(
                        Content.QuoteText(comment.content,
                                          attributes={'callout': ObsidianCalloutType.INFO}))
                case _:
                    self.presentation.add_children(Content.QuoteText(comment.content,
                                                                     attributes={
                                                                         'callout': ObsidianCalloutType.INFO,
                                                                         'callout-title': type
                                                                     }))

        for field in self.class_.fields:
            self.add_field(field)

    def add_field(self, field: Field):
        summary: str = find_summary(field)

        self.table_of_content.add_row(TableRow([
            Content.InternalLink(field.name),
            Content.FromText(summary)
        ]))

        field_head: Content = Content.Span([
            Content.Title(field.name, level=2)
        ])

        field_type: Content = Content.Span([], TextStyle.BOLD)

        # TODO Fixme
        # if isinstance(field.type, Function):
        #     field_type.add_children(Content.Span([
        #         link_to_type(output.type) for output in field.type.outputs
        #     ], attributes={'separator': ' '}))
        # else:
        #     field_type.add_children(link_to_type(field.type))

        field_head.add_children(Content.Span([
            Content.Span([Content.FromText(field.visibility.name)], TextStyle.ITALIC),
            field_type
        ], attributes={'separator': ' '}))

        self.add_content(field_head)
        self.add_content(Content.FromText(summary))

    def to_contents(self) -> List[Content]:
        """
        Return Article as a List of Content
        Used to export it afterward
        @return: List of Contents
        """
        return [self.header, self.presentation, Content.Separator(), Content.Title("Summary :"),
                self.table_of_content, Content.Separator()] + self.content
