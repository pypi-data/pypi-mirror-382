
from kabaret.app.ui import gui
from kabaret.app.session import KabaretSession
from kabaret.subprocess_manager.actor import SubprocessManager

from libreflow.utils.kabaret.jobs.jobs_node import JobsNodeSession

from .utils.kabaret.jobs.jobs_actor import Jobs


class BaseGUISession(gui.KabaretStandaloneGUISession):
    def register_view_types(self):
        super(BaseGUISession, self).register_view_types()

    def _create_actors(self):
        super(BaseGUISession, self)._create_actors()

        # Configure SubprocessManager
        subprocess_manager = SubprocessManager(self)


class BaseCLISession(KabaretSession):
    def _create_actors(self):
        super(BaseCLISession, self)._create_actors()

        # Configure SubprocessManager
        SubprocessManager(self)
        Jobs(self)


class JobsNodeSession(JobsNodeSession):
    pass