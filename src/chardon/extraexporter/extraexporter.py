
from chardon.documentation.project_manager import ProjectManager

class ExtraExporter:

    project: ProjectManager

    def __init__(self, project: ProjectManager):
        self.project = project

    def export(self, *wargs, **kwargs):
        pass
