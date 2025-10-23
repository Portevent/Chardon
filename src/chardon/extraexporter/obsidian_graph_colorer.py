import json
from pathlib import Path
from typing import List

from treelib import Tree

from chardon.extraexporter.extraexporter import ExtraExporter
from chardon.extraexporter.file_tree import FileTree, FileInput, FileNode
from chardon.code_parser.structure.class_ import Class
from chardon.documentation.project_manager import ProjectManager
from colour import Color


def rank_by_level(class_: Class) -> int:
    return len(class_.attributes["uri"].parts)

class ClassNode:
    def __init__(self, class_: Class, color: Color | None = None):
        self.class_ = class_
        self.color = color

class ObsidianGraphColorer(ExtraExporter):
    """
    Write in an obsidian project extra configuration to color nodes in graph view.
    Nodes are colored by folder, so file that are near each other in the hierarchy will have similar color
    """

    classes: List[Class]
    tree: Tree
    class_nodes: List[ClassNode]

    def __init__(self, project: ProjectManager):
        self.classes = list(project.classes.values())
        self.classes.sort(key=rank_by_level)
        self.class_nodes = []
        self.tree = FileTree([
            FileInput(self.add_node(ClassNode(class_)),
                      class_.attributes["uri"].parts[-1],
                      class_.attributes["uri"].parts[:-1])
            for class_ in self.classes
        ])

        self.color_nodes(self.tree.root, Color(hsl=(0,1,0.5)), Color(hsl=(1,1,0.5)))

    def add_node(self, node: ClassNode) -> ClassNode:
        self.class_nodes.append(node)
        return node

    def color_nodes(self, node: FileNode, color: Color, color2: Color, level: int =0):
        if node.children == {}:
            return

        hue_steps = (color2.get_hue() - color.get_hue()) / len(node.children)
        hue = color.get_hue()
        for child in node.children.values():
            if child.data:
                child.data.color = Color(hsl=(hue, 1, 0.5))

            self.color_nodes(child, Color(hsl=(hue-self.get_hue_variation(level), 1, 0.5)), Color(hsl=(hue+self.get_hue_variation(level), 1, 0.5)), level + 1)

            hue += hue_steps

    def get_hue_variation(self, level) -> float:
        match level:
            case 0 | 1:
                return 30 / 360
            case 2:
                return 10 / 360
            case _:
                return 5 / 360

    def colour_to_int(self, color: Color) -> int:
        return (int(color.get_red() * 255) << 16) + (int(color.get_green() * 255) << 8) + int(color.get_blue() * 255)

    def export(self, graph_file_path: Path) -> None:
        with open(graph_file_path, "rb") as graph_file:
            config = json.loads(graph_file.read())

        config['colorGroups'] = [
            {
                "query": f"path:{'/'.join(class_.class_.attributes['uri'].parts)}  ",
                "color": {
                    "a": 1,
                    "rgb": self.colour_to_int(class_.color)
                }
            }
            for class_ in self.class_nodes
        ]

        with open(graph_file_path, "w") as graph_file:
            graph_file.write(json.dumps(config, indent=2))