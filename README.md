![Version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2FPortevent%2FChardon%2Fmain%2Fpyproject.toml&query=%24.project.version&label=version
)
![Lint](https://github.com/Portevent/Chardon/actions/workflows/pylint.yml/badge.svg)
![GitHub License](https://img.shields.io/github/license/Portevent/Chardon)

# 🌷 Chardon

Chardon is a tool to parse input and generate documents.
It can do basic task, such as parsing a Markdown into HTML.
But it can handle much more complex task, such as parsing a project code, extracting comment, organizing them as several documentation pages and export them as Markdown or HTML.

## Format
![Done](https://img.shields.io/badge/Done-green)
![Doing](https://img.shields.io/badge/Doing-yellow)
![Todo](https://img.shields.io/badge/Todo-red)
### Inputs
- ![C#](https://img.shields.io/badge/C%23-green) : Will parse any properly commented Class, function or field
- ![Markdown](https://img.shields.io/badge/Markdown-yellow) : Partially implemented
- ![Python](https://img.shields.io/badge/Python-red) : Will be working on soon
- More format may be implemented in the future as the project growth and proposal are prioritized

### Outputs
- ![Markdown](https://img.shields.io/badge/Markdown-green) : Fully implemented
- ![Obsidian](https://img.shields.io/badge/ObsidianMarkdown-green) : Fully implemented
- ![Basic HTML](https://img.shields.io/badge/Basic_HTML-red) : Will be working on soon
- ![Advanced HTML](https://img.shields.io/badge/Advanced_HTML-red) : Will be working on soon on a css-stylized HTML
- More format may be implemented in the future as the project growth and proposal are prioritized

### Organization
- Simple conversion
- Code comments to functional documentation
- Plain Article to Website pages with content table

## How to use it
### Github action
Chardon won't be published as Github Action until it reach its first stable release

### PyPI
Install Chardon with pip
```shell
pip install chardon
```

Example code
```python
from pathlib import Path
from chardon import CSharpParser, ObsidianFlavoredMarkdownContentExport, ProjectManager

# Specify the path to my project and the output
project = Path('path/to/project')
out = Path('out/doc')

# Select which parser to use
parser = CSharpParser()
# Select which language to export to
exporter = ObsidianFlavoredMarkdownContentExport()

# Parse all the file within project, and export them
project_manager = ProjectManager(parser, exporter, project, out)
project_manager.export()
```