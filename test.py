from doc_generator.article_builder.exporter.markdown_exporter import MarkdownContentExport
from doc_generator.article_builder.parser.markdown_parser import MarkdownParser

input = """Salut __gras *   
gras__ et   
*italic*"""

parser = MarkdownParser(input)
contents = parser.parse()
export = MarkdownContentExport.export(contents)

print(input)
print(contents)
print(export)

