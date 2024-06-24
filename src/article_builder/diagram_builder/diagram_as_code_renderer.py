import logging

from .diagramcontent import DiagramContent

from diagrams import Diagram, Cluster, Edge, Node


class DiagramAsCodeRenderer:

    def __init__(self, content: DiagramContent):
        self.content = content
        self.nodes = {}

    def export(self):
        with Diagram('Brume', filename='Global diagram', outformat='svg', show=False):
            # logging.info(f'Export Brume diagram {self.content.objects.keys()=}')
            self._render_node(self.content.objects['children'])

            for node in self.nodes.keys():
                if node not in self.content.auto_links:
                    continue
                for relation in self.content.auto_links[node]:
                    if node < relation: #Only do one way
                        self.nodes[node] - Edge(style="dashed") - self.nodes[relation]

    def _render_node(self, group, direction='TB'):
        for key, node in group.items():
            if node['type'] == 'group':
                with Cluster(key, direction=direction):
                    self._render_node(node['children'], direction=self._invert_direction(direction))
            else:
                label = node['label']
                height = 0.4 + 0.15 * label.count(' ')

                self.nodes[key] = Node(label.replace(' ', '\n'), labelloc='c', height=str(height))

    def _invert_direction(self, direction):
        if direction == 'TB':
            return 'LR'
        return 'TB'
