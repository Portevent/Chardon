import logging

from .article import Article, Content, SummaryLink
from .. import doc_reader
from .. import diagram_builder


class DocArticle(Article):
    """
    Generate an Article from a Class and Function
    """

    def __init__(self):
        super().__init__()
        self.d2graph = None
        self.class_content = None
        self.functions_content = []
        self.types_used = {}

    def _markTypeAsUsed(self, type: doc_reader.Type):
        self.types_used[type.type] = True

    def AddFunction(self, function: doc_reader.RawDoc):
        if not function.isFunction():
            raise TypeError(f'Raw Doc : {function.getName()} is not a function')

        self.functions_content.append(FunctionContent(function))

        self._markTypeAsUsed(function.getReturnType().type)
        for parameter in function.getParameters().values():
            self._markTypeAsUsed(parameter.type)

    def SetGraph(self, graph_file):
        with open(graph_file, 'r') as file:
            self.d2graph = file.read()

    def SetClass(self, class_raw_doc: doc_reader.RawDoc):
        if not class_raw_doc.isClass() and not class_raw_doc.isStruct():
            raise TypeError(f'Raw Doc : {class_raw_doc.getName()} is not a class')

        self.AddTag(class_raw_doc.getDeclarationType())
        self.AddAlias(class_raw_doc.getAlias())
        self.SetName(class_raw_doc.getName())
        self.SetSlug(class_raw_doc.getName())

        self.class_content = ClassContent(class_raw_doc)

    def GetMetadata(self):
        metadata = f"title: {self.name}\n"
        metadata += f"path: {self.group}\n"

        if self.HasAliases():
            metadata += f"alias: \n"
            for alias in self.aliases:
                metadata += f'- {alias}\n'

        if self.HasTag():
            metadata += f"tag: \n"
            for tag in self.tags:
                metadata += f'- {tag}\n'

        return metadata

    def Export(self):
        logging.info(f"Export {self.name} : {self.class_content.getContent()}")
        article = "---\n"
        article += self.GetMetadata()
        article += "---\n"

        article += self.class_content.getContent()

        if self.d2graph != "":
            article += f'```d2\n{self.d2graph}\n```'

        if len(self.functions_content) > 0:
            functions = "\n---\n# Functions :\n"

            summary = "\n---\n# Summary :\n"
            summary += f"name|description\n----|----\n"

            for function_content in self.functions_content:
                link = SummaryLink(function_content)
                summary += f"[[#{link.ref}\\|{link.name}]] | `{link.description}`\n"

                functions += function_content.getContent()

            article += summary
            article += functions

        return article

    def getRelatedArticles(self) -> list[str]:
        return [type for type in self.types_used if doc_reader.KnownTypes.Has(type)]


class ClassContent(Content):
    def __init__(self, doc: doc_reader.RawDoc):
        self.name = doc.getName()
        self.summary = ""
        self.remarks = ""
        self.links = []
        for tag in doc.getTags():
            if tag.name == 'summary':
                self.summary = tag.content.strip()
            if tag.name == 'remarks':
                self.remarks = tag.content.strip()
            if tag.name == 'link':
                self.links.append(diagram_builder.Link(
                    objectA=tag.attributs.get('from') or self.name,
                    objectB=tag.attributs.get('to') or self.name,
                    label=tag.content,
                    labelA=tag.attributs.get('fromLabel') or "",
                    labelB=tag.attributs.get('toLabel') or "",
                    linkPreset=diagram_builder.LinkPreset.ARROW if tag.attributs.get('type', 'arrow') == 'arrow'
                    else (
                        diagram_builder.LinkPreset.DOUBLE_ARROW if tag.attributs.get('type', 'arrow') == 'double-arrow'
                        else diagram_builder.LinkPreset.LINE
                    ),
                    line_type=diagram_builder.LineType.DASHED if tag.attributs.get('line') == 'dashed' else None,
                    active=tag.attributs.get('type') != "not_important"
                ))

    def getContent(self):
        content = ""
        if self.summary != "":
            content += self.summary + "  \n"
        if self.remarks != "":
            content += self.remarks + "  \n"

        return content


class FunctionContent(Content):
    def __init__(self, doc: doc_reader.RawDoc):
        self.name = doc.getName()
        self.parameters: list[doc_reader.Parameter] = []
        self.out: doc_reader.Parameter = None
        self.exception: list[doc_reader.Parameter] = []
        functionParams = doc.getParameters()

        for tag in doc.getTags():
            if tag.name == 'summary':
                self.summary = tag.content.strip()

            if tag.name == "param":
                if not tag.attributs['name'] in functionParams:
                    logging.warning(f"{doc.getName()}'s documentation contains {tag.attributs['name']} but the code itself doesn't.")
                    continue
                param: doc_reader.Parameter = functionParams[tag.attributs['name']]
                param.description = tag.content
                self.parameters.append(param)

            if tag.name == "returns":
                self.out = doc.getReturnType()
                self.out.description = tag.content

            if tag.name == "exception":
                self.exception.append(doc_reader.Parameter(tag.attributs['cref'], "", "", tag.content))

    def getContent(self):
        content = f"\n---\n### {self.name}\n"
        content += f'{self.summary}\n'

        mode = "Table"
        if len(self.parameters) > 0:
            content += "\n#### Parameters\n"
            if mode == "List":
                for param in self.parameters:
                    content += f"- **{param.name}** ({param.type}) : {param.description}\n"
            elif mode == "Table":
                content += "name|type|description\n"
                content += "-----|-----|-----\n"
                for param in self.parameters:
                    content += f"**{param.name}**|{param.type}|{param.description}\n"
            else:
                content += f"==unsuported param mode : {mode}=="

        if self.out is not None:
            content += "\n#### Return\n"
            content += f"- {self.out.type} : {self.out.description}\n"

        if len(self.exception) > 0:
            content += "\n#### Exceptions\n"
            for param in self.exception:
                content += f"- {param.type} : {param.description}\n"

        return content

    def getLinkDescription(self):
        return self.summary
