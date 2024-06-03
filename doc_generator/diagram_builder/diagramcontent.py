import json

from .links import Link
from .color import Color


class DiagramContent:
    objects = {'type': 'group', 'children': {}}
    aliases = {}
    links = []
    auto_links = {}
    colors = {}

    @staticmethod
    def addObject(path, id, label):
        nodes = path.split('/')[1:]

        DiagramContent._createAliasEntry(id, path=nodes)

        tree = DiagramContent.objects

        for node in nodes:
            if node not in tree['children']:
                color = DiagramContent.registerNewColor(tree['color'] if 'color' in tree else None, node)
                tree['children'][node] = {'type': 'group', 'color': color, 'children': {}}
            tree = tree['children'][node]

        tree['children'][id] = {
            'type': 'leaf',
            'label': label
        }

    @staticmethod
    def _createAliasEntry(entry, path=None):
        if entry not in DiagramContent.aliases:
            DiagramContent.aliases[entry] = {
                'path': path,
                'related': {}
            }
        if path:
            DiagramContent.aliases[entry]['path'] = path

    @staticmethod
    def _addReferenceToAliasEntry(objectA, objectB, link):
        DiagramContent._createAliasEntry(objectA)
        related_entries = DiagramContent.aliases[objectA]['related']
        if objectB not in related_entries:
            related_entries[objectB] = []

        related_entries[objectB].append(link)

    @staticmethod
    def addLink(link: Link):
        DiagramContent.links.append(link)

        DiagramContent._addReferenceToAliasEntry(link.objectA, link.objectB, link)
        DiagramContent._addReferenceToAliasEntry(link.objectB, link.objectA, link)

    @staticmethod
    def exportJson():
        with open('nodes.json', 'w') as file:
            file.write(json.dumps(DiagramContent.objects))
        with open('aliases.json', 'w') as file:
            file.write(json.dumps(DiagramContent.aliases))
        with open('links.json', 'w') as file:
            file.write(json.dumps(DiagramContent.links))
        with open('autolinks.json', 'w') as file:
            file.write(json.dumps(DiagramContent.auto_links))
        with open('colors.json', 'w') as file:
            file.write(json.dumps(DiagramContent.colors, indent=4))

    @staticmethod
    def setNoAutoLink(objectA, objectB):
        DiagramContent._addAutoLinkFromTo(objectA, objectB, active=False)
        DiagramContent._addAutoLinkFromTo(objectB, objectA, active=False)

    @staticmethod
    def addAutoLink(objectA, objectB):
        DiagramContent._addAutoLinkFromTo(objectA, objectB)
        DiagramContent._addAutoLinkFromTo(objectB, objectA)

    @staticmethod
    def _addAutoLinkFromTo(fromObject, toObject, active=True):
        DiagramContent._createAliasEntry(fromObject)
        if toObject in DiagramContent.aliases[fromObject]['related']:
            return
        if fromObject not in DiagramContent.auto_links:
            DiagramContent.auto_links[fromObject] = {}

        if toObject not in DiagramContent.auto_links[fromObject]:
            DiagramContent.auto_links[fromObject][toObject] = active

    @staticmethod
    def deviateColor(color_code: int, name: str):
        h_deviance = [-20, 20]
        v_deviance = [-0.2, -0.1]
        if color_code is None:
            h_deviance = [-180, 180]
            v_deviance = [-0.05, -0.02]
            color = Color(rgb=[1, 0, 0])
        else:
            color = Color(int_value=color_code)

        random = name.__hash__()%1000/1000

        delta_h = h_deviance[0] + (h_deviance[1] - h_deviance[0]) * random
        delta_v = v_deviance[0] + (v_deviance[1] - v_deviance[0]) * random

        color.addHSV(hue=delta_h, saturation=0, value=delta_v)

        return color.getInt()

    @staticmethod
    def registerNewColor(color_code, node):
        DiagramContent.colors[node] = DiagramContent.deviateColor(color_code=color_code, name=node)
