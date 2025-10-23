from __future__ import annotations
from typing import List, Dict

class FileInput:
    data: any
    key: str
    hierarchy: List[str]

    def __init__(self, data: any, key: str, hierarchy: List[str]):
        self.data = data
        self.key = key
        self.hierarchy = hierarchy

    def __repr__(self):
        return f"FileInput({self.key}, {self.hierarchy})"

class FileNode:
    data: any
    parent: Self | None
    children: Dict[str, Self]
    key: str

    def __init__(self, data: any, key: str, parent: Self | None = None, children: Dict[str, Self] | None = None):
        self.data = data
        self.key = key
        self.parent = parent
        self.children = children or {}

    def add_child(self, child: Self):
        self.children[child.key] = child
        child.parent = self

    def __repr__(self):
        return f"FileNode({self.parent.key if self.parent else '[root]'}->{self.key}->[{len(self.children)}])"

class FileTree:
    """
    FileTree containing FileNode, created from a list of FileInput
    """
    root: FileNode

    def __init__(self, files: List[FileInput]):
        self.root = FileNode(None, "", None, {})
        for file in files:
            self.add(file)

    def create_empty_nodes(self, nodes: List[str], from_node: FileNode | None = None) -> FileNode:
        parent = from_node or self.root
        for node in nodes:
            child = FileNode(None, node, parent, {})
            parent.add_child(child)
            parent = child

        return parent

    def get_node(self, nodes: List[str], create_if_empty: bool = False) -> FileNode:

        current_node = self.root
        for node in nodes:
            if node in current_node.children:
                current_node = current_node.children[node]
            else:
                if create_if_empty:
                    current_node = self.create_empty_nodes([node], from_node=current_node)
                else:
                    raise Exception(f"Get node couldn't find node {node} in {current_node} (looking for {nodes})")

        return current_node

    def add(self, file: FileInput):
        self.get_node(file.hierarchy, True).add_child(FileNode(file.data, file.key))