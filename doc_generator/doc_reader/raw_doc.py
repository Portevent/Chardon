import logging
import re


class KnownTypes:
    """List of known types that can be safely linked"""
    known = {}

    @staticmethod
    def Add(type: str):
        KnownTypes.known[type] = True

    @staticmethod
    def Has(type: str) -> bool:
        return type in KnownTypes.known


class Parameter:

    def __repr__(self):
        return f"<{self.name} : {self.type}>"

    def __init__(self, type, name, default, description=""):
        self.type = Type(type)
        self.name = name
        self.default = default
        self.description = description


class Tag:
    def __init__(self, name, content, attributs={}):
        self.name = name
        self.content = content
        self.attributs = attributs

    def __repr__(self):
        return f'{self.name} = {self.content} : {self.attributs}'


class Type:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return f"[[{self.type}]]" if KnownTypes.Has(self.type) else f"`{self.type}`"


class Function:

    def __init__(self, name, description, return_type=None, parameters=[], exceptions=[]):
        self.name = name
        self.description = description
        self.return_type = return_type
        self.parameters = parameters
        self.exceptions = exceptions


class RawDoc:

    def __init__(self, declaration, comment):
        self.declaration = declaration
        self.comment = comment

        if self.isClass() or self.isStruct():
            KnownTypes.Add(self.getName())

        logging.info(f"Created Doc {declaration=}\n{comment=}")

    def __repr__(self):
        return f"<{self.declaration}>"

    def getName(self) -> str:
        if self.isClass() or self.isStruct():
            return self.declaration.split(':')[0].strip().split(' ')[-1]

        if self.isFunction():
            return self.declaration.split('(')[-2].split(" ")[-1].strip()

        return self.declaration

    def getAlias(self):
        alias = self.getName()
        if self.isClass() or self.isStruct():
            return re.sub('([A-Z][a-z]{2,})', r' \1', alias).strip()

        if self.isFunction():
            pass

        return alias

    def isFunction(self):
        return not self.isClass() and not self.isStruct() and self.declaration.__contains__('(')

    def isClass(self):
        return self.declaration.__contains__('class')

    def isStruct(self):
        return self.declaration.__contains__('struct')

    def getReturnType(self) -> Parameter:
        if self.isFunction():
            return Parameter(self.declaration.split('(')[-2].split(" ")[-2].strip(), "", "", "")

        else:
            raise Exception(f'Trying to get return type on something that isn\'t a function : {self.declaration}')

    def getParameters(self) -> dict[Parameter]:
        if self.isFunction():
            params = {}
            for rawParams in self.declaration.split('(')[-1].split(")")[0].split(', '):
                rawParams = rawParams.strip()
                if rawParams != "":
                    name, paramType, default = "", "", ""
                    if rawParams.__contains__("="):
                        definition, default = rawParams.split('=')
                        paramType, name = definition.strip().split(' ')
                    else:
                        paramType, name = rawParams.split(' ')

                    params[name] = Parameter(type=paramType.strip(), name=name.strip(), default=default.strip())

            return params

        else:
            raise Exception(f'Trying to get parameters on something that isn\'t a function : {self.declaration}')

    def getTags(self) -> list[Tag]:
        tags = []

        insideTagName = False
        tagName = ""

        tagAttributes = {}
        insideTagAttribute = False
        tagAttribute = ""
        insideTagAttributeValue = False
        afterFirstBrackOfAttributeValue = False
        tagAttributeValue = ""

        insideTagContent = False
        tagContent = ""

        insideTagTail = False

        escaping = False

        # Template : <tag param="value">content</tag>

        for char in self.comment:

            if insideTagName:
                if char == " ":  # Passage à un parametre
                    insideTagName = False
                    insideTagAttribute = True

                elif char == ">":  # Fin du tag
                    insideTagName = False
                    insideTagContent = True

                else:
                    tagName += char

            elif insideTagAttribute:
                if char == "=":  # Passage à la value
                    insideTagAttribute = False
                    insideTagAttributeValue = True

                else:
                    tagAttribute += char

            elif insideTagAttributeValue:
                # Opening or closing bracket
                if char == "\"":
                    if not afterFirstBrackOfAttributeValue:  # If it is the first, don't do anything
                        afterFirstBrackOfAttributeValue = True
                        continue

                    afterFirstBrackOfAttributeValue = False
                    insideTagAttributeValue = False
                    insideTagName = True

                    # Ajout du parameter à la liste
                    tagAttributes[tagAttribute] = tagAttributeValue
                    tagAttribute = ""
                    tagAttributeValue = ""

                else:
                    tagAttributeValue += char

            elif insideTagContent:
                # Escape character after \
                if escaping:
                    tagContent += char
                    escaping = False
                    continue

                if char == "\\":
                    escaping = True
                elif char == "<":
                    insideTagContent = False
                    insideTagTail = True
                else:
                    tagContent += char

            elif insideTagTail:
                if char == ">":
                    tags.append(Tag(tagName, tagContent, tagAttributes))

                    tagName = ""
                    tagContent = ""
                    tagAttributes = {}
                    insideTagTail = False

                elif char == "<":
                    logging.warning(f"A `<` has been found in closing tag {tagName}. "
                                    f"Documentation for {self.getName()} probably has a format default.")
            else:
                if char == "<":
                    insideTagName = True

        return tags

    def getDeclarationType(self):
        if self.isClass():
            return "class"
        if self.isFunction():
            return "function"
        if self.isStruct():
            return "struct"
        else:
            raise Exception(f'Can\'t get the type of {self.declaration}')
