from kabaret.app.session import KabaretSession
from kabaret.subprocess_manager import SubprocessManager


class SessionCLI(KabaretSession):

    def __init__(self, session_name=None, debug=False):
        super(SessionCLI, self).__init__(session_name, debug)
        self.cmds.Cluster.connect_from_env()

    def _create_actors(self):
        super(SessionCLI, self)._create_actors()
        SubprocessManager(self)
