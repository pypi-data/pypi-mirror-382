import sys
import os
import argparse
import json

from qtpy import QtCore
from kabaret.app.ui import gui
from kabaret.app.actors.flow import Flow
from kabaret.subprocess_manager import SubprocessManager

from libreflow.resources.icons import libreflow, status
from libreflow.resources import file_templates
from libreflow.utils.kabaret.script_view.script_view import DefaultScriptViewPlugin
from libreflow.utils.kabaret.flow_contextual_dict.view import DefaultContextualDictView
from libreflow.utils.kabaret.subprocess_manager.views.subprocess_view import DefaultSubprocessView
from libreflow.utils.kabaret.ui.flow_view import DefaultFlowViewPlugin
from libreflow.utils.kabaret.ui.main_window import DefaultMainWindowManager
from libreflow.utils.search.actor import Search


CUSTOM_HOME = True
DEBUG = False
JOBS_VIEW = True
SEARCH_ENABLED = True
LAYOUT_MANAGER = True
CONTEXT_VIEW = True

try:
    from libreflow.utils.kabaret.jobs.jobs_view import JobsView
    from libreflow.utils.kabaret.jobs.jobs_actor import Jobs
except ImportError:
    print('ERROR: kabaret.jobs not found')
    JOBS_VIEW = False

if CUSTOM_HOME:
    from .custom_home import MyHomeRoot

from .resources import file_templates, gifs


from libreflow.resources import styles

styles_folder = os.path.dirname(styles.__file__)

current_style_file = os.path.dirname(styles.__file__) + '/current_style.txt'

if not os.path.exists(current_style_file):
    with open(current_style_file, 'w') as f:
        d = dict(current_style = 'classic')
        json.dump(d, f)

else :
    with open(current_style_file, 'rb') as f:
        cs = json.loads(f.read())

try:
    if cs['current_style'] == 'classic' :
        from libreflow.resources.styles.lfs_tech import LfsTechStyle
        LfsTechStyle()
    elif cs['current_style'] == 'dark':
        from libreflow.resources.styles.custom_style import CustomStyle
        CustomStyle()
    else :
        from .resources.gui.styles.default_style import DefaultStyle
        DefaultStyle()

    os.environ['LF_THEME'] = cs['current_style']
except :
    from libreflow.resources.styles.lfs_tech import LfsTechStyle
    LfsTechStyle()
    os.environ['LF_THEME'] = 'classic'


# else :
#     LfsTechStyle()



class SessionGUI(gui.KabaretStandaloneGUISession):

    def __init__(self,
        session_name='Standalone', tick_every_ms=10, debug=False,
        layout_mgr=False, layout_autosave=False, layout_savepath=None,
        search_index_uri=None, search_auto_indexing=False
    ):
        self._search_index_uri = search_index_uri
        self._search_auto_indexing = search_auto_indexing

        if LAYOUT_MANAGER and (layout_mgr is False and '--no-layout-mgr' not in sys.argv):
            layout_mgr = True
            
            if '--no-layout-autosave' not in sys.argv:
                layout_autosave = True
        
        super(SessionGUI, self).__init__(
            session_name, tick_every_ms, debug,
            layout_mgr, layout_autosave, layout_savepath
        )

    def register_plugins(self, plugin_manager):
        super(gui.KabaretStandaloneGUISession, self).register_plugins(plugin_manager)
        
        # Register libreflow default script view plugin
        plugin_manager.register(DefaultScriptViewPlugin, 'kabaret.script_view')

        # Register libreflow default view plugin
        plugin_manager.register(DefaultFlowViewPlugin, 'kabaret.flow_view')

    def create_window_manager(self):
        return DefaultMainWindowManager.create_window(self)

    def register_view_types(self):
        super(SessionGUI, self).register_view_types()

        type_name = self.register_view_type(DefaultSubprocessView)
        if os.environ.get("LIBREFLOW_SHOW_PROCESS_VIEW"):
            subprocess_hidden = not bool(os.environ["LIBREFLOW_SHOW_PROCESS_VIEW"])
            self.main_window_manager.resize(1280, 800)
        else: 
            subprocess_hidden = not DEBUG
        
        self.add_view(
            type_name,
            view_id='Processes',
            hidden=subprocess_hidden,
            area=QtCore.Qt.RightDockWidgetArea,
        )

        if JOBS_VIEW:
            type_name = self.register_view_type(JobsView)
            self.add_view(
                type_name,
                hidden=not DEBUG,
                area=QtCore.Qt.RightDockWidgetArea,
            )

        if CONTEXT_VIEW:
            type_name = self.register_view_type(DefaultContextualDictView)
            self.add_view(
                type_name,
                hidden=True,
                area=QtCore.Qt.RightDockWidgetArea,
            )

    def set_home_oid(self, home_oid):
        if home_oid is None:
            home_oid = os.environ.get('KABARET_HOME_OID')
            if home_oid is None:
                return
            self.log_info(f"Home oid from environment: {home_oid}")

        if not home_oid.startswith('/'):
            # Project name provided: turn into oid
            home_oid = '/'+home_oid
        project_name = home_oid.split('/', 2)[1]
        # Check project separately since undefined name raises an error
        has_project = self.get_actor('Flow').has_project(project_name)
        if not has_project or not self.cmds.Flow.exists(home_oid):
            self.log_warning(f"Home oid {home_oid} not found: fall back to default")
            return

        self.log_info(f"Set home oid to {home_oid}")
        self.cmds.Flow.set_home_oid(home_oid)

    def _create_actors(self):
        '''
        Instanciate the session actors.
        Subclasses can override this to install customs actors or
        replace default ones.
        '''
        if CUSTOM_HOME:
            Flow(self, CustomHomeRootType=MyHomeRoot)
        else:
            return super(SessionGUI, self)._create_actors()
        subprocess_manager = SubprocessManager(self)

        jobs = Jobs(self)

        if SEARCH_ENABLED and self._search_index_uri is not None:
            Search(self, self._search_index_uri, self._search_auto_indexing)


def get_dict_with_default(env_var):
    return {"default": os.getenv(env_var)} if os.getenv(env_var) else {}


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Session Arguments'
    )
    parser.add_argument(
        '-u', '--user', dest='user'
    )
    parser.add_argument(
        '-s', '--site', default=os.getenv('LIBREFLOW_SITE', 'lfs'), dest='site'
    )
    parser.add_argument(
        '--layout-mgr', default=False, action='store_true', dest='layout_mgr', help='Enable Layout Manager'
    )
    parser.add_argument(
        '--no-layout-mgr', action='store_false', dest='layout_mgr', help='Disable Layout Manager'
    )
    parser.add_argument(
        '--layout-autosave', default=False, action='store_true', dest='layout_autosave', help='Use Layout Autosave'
    )
    parser.add_argument(
        '--no-layout-autosave', action='store_false', dest='layout_autosave', help='Disable Layout Autosave'
    )
    parser.add_argument(
        '--layout-savepath', default=os.getenv('KABARET_LAYOUT_SAVEPATH', None), dest='layout_savepath', help='Specify Layout Saves Path'
    )
    parser.add_argument(
        '--home-oid', dest='home_oid'
    )
    parser.add_argument(
        '-j', '--jobs_default_filter', dest='jobs_default_filter'
    )
    parser.add_argument(
        '--search-index-uri', **get_dict_with_default('LIBREFLOW_SEARCH_INDEX_URI'), nargs='?', dest='search_index_uri'
    )
    parser.add_argument(
        '--search-auto-indexing', dest='search_auto_indexing', nargs='?', const=True, type=bool
    )
    parser.add_argument(
        '--show-process-view', dest='show_process_view', nargs='?', const=True, type=bool
    )
    values, _ = parser.parse_known_args(args)

    if values.site:
        os.environ['KABARET_SITE_NAME'] = values.site
    if values.user:
        os.environ['USER_NAME'] = values.user
    if values.jobs_default_filter:
        os.environ['JOBS_DEFAULT_FILTER'] = values.jobs_default_filter
    else:
        os.environ['JOBS_DEFAULT_FILTER'] = values.site
    
    if values.search_auto_indexing is None:
        values.search_auto_indexing = 'SEARCH_AUTO_INDEXING' in os.environ
    
    if values.show_process_view:
        os.environ['LIBREFLOW_SHOW_PROCESS_VIEW'] = str(values.show_process_view)
    
    return (
        values.search_index_uri,
        values.search_auto_indexing,
        values.home_oid,
        values.layout_mgr,
        values.layout_autosave,
        values.layout_savepath
    )


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        read_replica_host,
        read_replica_port,
        remaining_args,
    ) = SessionGUI.parse_command_line_args(argv)
    (
        uri,
        auto_indexing,
        home_oid,
        layout_mgr,
        layout_autosave,
        layout_savepath
    ) = process_remaining_args(remaining_args)

    session = SessionGUI(
        session_name=session_name, debug=debug,
        layout_mgr=layout_mgr, layout_autosave=layout_autosave, layout_savepath=layout_savepath,
        search_index_uri=uri, search_auto_indexing=auto_indexing
    )
    session.cmds.Cluster.connect(host, port, cluster_name, db, password, read_replica_host, read_replica_port)
    session.set_home_oid(home_oid)

    session.start()
    session.close()


if __name__ == '__main__':
    main(sys.argv[1:])