import os


class Content:
    def __init__(self, name, content):
        self.name = name
        self.content = content

    def getLinkName(self):
        return self.name

    def getLinkRef(self):
        return self.name

    def getLinkDescription(self):
        return self.name

    def getContent(self):
        return self.content


class SummaryLink:
    def __init__(self, content: Content):
        self.name = content.getLinkName()
        self.ref = content.getLinkRef()
        self.description = content.getLinkDescription()


class Article:

    def __init__(self):
        self.header: Content = None
        self.summary: list[SummaryLink] = []
        self.content: list[Content] = []
        self.tags: list[str] = []
        self.name = ""
        self.slug = ""
        self.aliases = []
        self.group = ""
        self.directory = ""

    def SetName(self, name):
        self.name = name

    def SetSlug(self, slug):
        self.slug = slug

    def AddAlias(self, alias):
        self.aliases.append(alias)

    def SetGroup(self, group):
        self.group = group

    def SetDirectory(self, directory):
        self.directory = directory

    # Before Summary
    def SetHeader(self, content):
        self.header = content

    def AddContent(self, content, create_link=False):
        self.content.append(content)
        if create_link:
            self.summary.append(SummaryLink(content))

    def AddTag(self, tag):
        self.tags.append(tag)

    def HasTag(self) -> bool:
        return len(self.tags) > 0

    def HasAliases(self) -> bool:
        return len(self.aliases) > 0

    def HasHeader(self) -> bool:
        return self.header is not None

    def Export(self):
        article = "---\n"

        # Doing metadata
        article += f"title: {self.name}\n"
        article += f"slug: {self.slug}\n"

        if self.HasAliases():
            article += f"alias: \n"
            for alias in self.aliases:
                article += f'- {alias}\n'

        if self.HasTag():
            article += f"tag: \n"
            for tag in self.tags:
                article += f'- {tag}\n'

        # End metadata
        article += "---\n"

        if self.HasHeader():
            article += self.header.getContent()

        if len(self.summary) > 0:
            article += "\n---\n# Summary :\n"
            article += f"name|description\n----|----\n"

            for link in self.summary:
                article += f"[[#{link.ref}\\|{link.name}]] | `{link.description}`\n"

        for content in self.content:
            article += content.getContent()

        return article

    def Publish(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        with open(f'{self.directory}/{self.name}.md', 'w') as file:
            file.write(self.Export())
