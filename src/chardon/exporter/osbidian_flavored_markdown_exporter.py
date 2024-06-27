"""
implementation of export content to Markdown
"""

from chardon.article_builder.content import ContentType, Content
from chardon.exporter.markdown_exporter import joins, MarkdownContentExport,\
    MarkdownContentBreaklineType


# pylint: disable=too-few-public-methods
class ObsidianFlavoredMarkdownContentExport(MarkdownContentExport):
    """
    Export Content To Obsidian Flavored Markdown
    """
    BREAKLINE_IN_TABLE: str = "<br>"

    # Override default breakline for ObsidianFlavoredMD
    BREAKLINE: MarkdownContentBreaklineType = MarkdownContentBreaklineType.NONE

    def _list_entry_export(self, entry: Content, ordered: bool = False, index: int = 0) -> str:
        """
        Export list entry to string
        @param entry: Content
        @param ordered: Whether this entry is from an ordered list or unordered
        @param index: Index of entry in the list
        @return: Exported content
        """
        tab = "    " * entry.attributes['level']
        head = f'{index}. ' if ordered else "- "
        checkbox = ""
        if 'completed' in entry.attributes:
            checkbox = f'[{"x" if entry.attributes["completed"] else " "}] '
        content = self._export(entry.attributes['entry'])
        return f"{tab}{head}{checkbox}{content}"

    def _export(self, content: Content) -> str:
        """
        Export content, without considering the breaklines yet
        """
        exported_content: str
        match content.type:
            case ContentType.LIST:
                ordered = content.attributes['ordered']
                entries = [self._list_entry_export(entry, ordered, i)
                           for i, entry in enumerate(content.attributes['children'])]

                exported_content = joins(
                    elements=entries,
                    between_each="\n"
                )

            case ContentType.QUOTE:
                exported_content: str = ""
                if 'callout' in content.attributes:
                    exported_content = f'\n> [!{content.attributes["callout"]}]'
                    if content.attributes.get('foldable', False):
                        indicator = "+"
                        if content.attributes.get('collapses-by-default', False):
                            indicator = "-"
                        exported_content += indicator

                    if 'callout-title' in content.attributes:
                        exported_content += f" {content.attributes['callout-title']}"

                return exported_content + super()._export(content)

            case ContentType.LINK:
                if content.attributes.get('internal-link', False):
                    text: str = ('|' + content.attributes['text']) \
                        if 'text' in content.attributes else ''
                    exported_content = f"[[#{content.attributes['target']}{text}]]"

                    if 'embed' in content.attributes and content.attributes['embed']:
                        exported_content = '!' + exported_content

                elif content.attributes.get('link_to_another_page', False):
                    exported_content = f"[[{content.attributes['text']}]]"

                else:
                    return super()._export(content)

            case _:
                return super()._export(content)

        return exported_content
