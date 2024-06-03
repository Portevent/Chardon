import logging
import os
import subprocess

from .diagramcontent import DiagramContent
from .links import Link, LineType, ArrowType


def _render_line_type(line_type: LineType):
    match line_type:
        case LineType.SOLID:
            return ""
        case LineType.NONE:
            return "style.opacity: 0"
        case LineType.DASHED:
            return "style.stroke-dash: 3"
        case _:
            return ""


def _render_arrow_type(arrow_type: ArrowType):
    match arrow_type:
        case ArrowType.NONE:
            return "{}"
        case ArrowType.ARROW:
            return "{shape: arrow}"
        case ArrowType.DIAMOND:
            return "{shape: diamond}"
        case _:
            return "{}"


def render_link_arrows(link: Link):
    return ("" if link.arrow_from == ArrowType.NONE else "<") \
           + ("--" if link.arrow_from == ArrowType.NONE and link.arrow_to == ArrowType.NONE else "-") \
           + ("" if link.arrow_to == ArrowType.NONE else ">")


class D2Renderer:

    def __init__(self, content: DiagramContent, output_d2="", output_svg=""):
        self.content = content
        self.output_d2 = output_d2
        self.output_svg = output_svg
        self.nodes = {}

    def export(self, limit_to=None):
        if not os.path.exists(self.output_d2):
            os.makedirs(self.output_d2)
        if not os.path.exists(self.output_svg):
            os.makedirs(self.output_svg)

        filename_d2 = f'{self.output_d2}/{limit_to or "global"}.d2'
        filename_svg = f'{self.output_svg}/{limit_to or "global"}.svg'

        allowed_nodes = None
        if limit_to:
            allowed_nodes = {}

            # Get all node related to "limit_to"
            node_included = {}
            for node in self.content.aliases[limit_to]['related'].keys():
                node_included[node] = True
            if limit_to in self.content.auto_links:
                for node, active in self.content.auto_links[limit_to].items():
                    if active:
                        node_included[node] = True

            # Allow allowed node and their group
            for node in node_included.keys():
                allowed_nodes[node] = True
                if self.content.aliases[node]['path'] is None:
                    logging.error(f'Path of {node} is None : {self.content.aliases[node]=}')
                for path in self.content.aliases[node]['path']:
                    allowed_nodes[path] = True

            allowed_nodes = list(allowed_nodes.keys())

        logging.info(f'Render {limit_to or "Brume"} digram')
        logging.debug(f'{allowed_nodes=}')
        self._export_to_file(filename_d2, allowed_nodes, limit_to)
        self._export_to_svg(filename_d2, filename_svg)

        return filename_d2

    def _export_to_file(self, filename, allowed_nodes, limit_to):
        with open(filename, 'w') as diagram:
            if allowed_nodes == []:
                return

            diagram.write("# Nodes :\n")
            diagram.write("\n".join(self._render_node(self.content.objects['children'], allowed_nodes=allowed_nodes)))

            diagram.write('\n\n# Links :\n')
            for node in self.content.auto_links:
                for relation, active in self.content.auto_links[node].items():
                    if not active:
                        continue
                    if node < relation:  # Only do one way
                        if limit_to and (limit_to not in [node, relation]):
                            continue
                        diagram.write(self._render_simple_dashed_link(node, relation))

            for link in self.content.links:
                if limit_to and (limit_to not in [link.objectA, link.objectB]):
                    continue
                diagram.write(self._render_link(link))

    def _render_node(self, group, allowed_nodes=None):
        text = []
        for key, node in group.items():
            if allowed_nodes and key not in allowed_nodes:
                continue
            if node['type'] == 'group':
                text.append(key + ": {")
                text = text + [("    " + line) for line in
                               self._render_node(node['children'], allowed_nodes=allowed_nodes)]
                text.append("}")
            else:
                text.append(f"{key}: {node['label']} " + "{")
                text.append(f'   link: {key}')
                text.append("}")

        return text

    def _path(self, object):
        if self.content.aliases[object]['path'] is None:
            logging.error(f'No path for {object=} : {self.content.aliases[object]=}')
        return ".".join(self.content.aliases[object]['path'] + [object])

    def _render_simple_dashed_link(self, objectA, objectB):
        return f"{self._path(objectA)} -- {self._path(objectB)}:" + " {style.stroke-dash: 3}\n"

    def _render_link(self, link: Link):
        if not link.active:
            return ""

        styles = f"{_render_line_type(link.line_type)}\n" \
                 f"source-arrowhead: {link.labelA}{_render_arrow_type(link.arrow_from)}\n" \
                 f"target-arrowhead: {link.labelB}{_render_arrow_type(link.arrow_to)}\n"
        return f"{self._path(link.objectA)} {render_link_arrows(link)} {self._path(link.objectB)}: {link.label}" + " {" + styles + "}\n"

    def _export_to_svg(self, filename_d2, filename_svg):
        subprocess.run(["d2", filename_d2, filename_svg])
