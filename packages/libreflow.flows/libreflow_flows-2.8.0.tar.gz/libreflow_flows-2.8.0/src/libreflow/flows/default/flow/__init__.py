from kabaret import flow
from kabaret.flow_extensions.flow import DynamicTreeManager
from libreflow.baseflow import (
    Project as BaseProject,
    ProjectSettings as BaseProjectSettings,
    LogOut,
    UserProfile,
    Admin as BaseAdmin,
    Synchronization,
    GoToMyTasks
)
from libreflow.baseflow.task_manager import TaskManager
from libreflow.baseflow.mytasks import MyTasks
from libreflow.utils.flow.values import MultiOSParam
from libreflow.utils.flow.import_files import ImportFilesAction

from .entity_manager import EntityManager
from .user import User, Users
from .film import Film, FilmCollection
from .shot import Sequence, Shot
from .task import Task, Tasks
from .asset import Asset, AssetFamily, AssetType, AssetTypeCollection, AssetLibrary, AssetLibraryCollection
from .file import (
    TrackedFile,
    TrackedFolder,
    Revision,
    TrackedFolderRevision,
)


class ProjectSettings(BaseProjectSettings):

    task_manager = flow.Child(TaskManager)
    # image_sequence_prefixes = flow.OrderedStringSetParam()
    shot_types = flow.OrderedStringSetParam()
    shot_indexes = flow.OrderedStringSetParam()
    shot_versions = flow.OrderedStringSetParam()

    ffmpeg_path = MultiOSParam()


class Admin(BaseAdmin):

    entity_manager = flow.Child(EntityManager)

    store = flow.Child(flow.Object).ui(hidden=True)
    dependency_templates = flow.Child(flow.Object).ui(hidden=True)


class Project(BaseProject, flow.InjectionProvider):
    _MANAGER_TYPE = DynamicTreeManager
    _PROPAGATE_MANAGER_TYPE = True
    
    log_out_action  = flow.Child(LogOut).ui(label='Log out')
    goto_my_tasks = flow.Child(GoToMyTasks).ui(label="My Tasks")
    mytasks = flow.Child(MyTasks).ui(hidden=True)
    user            = flow.Child(UserProfile)
    synchronization = flow.Child(Synchronization).ui(expanded=False)
    films           = flow.Child(FilmCollection).ui(expanded=True)
    asset_types     = flow.Child(AssetTypeCollection).ui(expanded=True)
    asset_libs      = flow.Child(AssetLibraryCollection).ui(expanded=True)
    import_files = flow.Child(ImportFilesAction).ui(dialog_size=(800,600))
    admin           = flow.Child(Admin)

    asset_lib = flow.Child(flow.Object).ui(hidden=True)
    sequences = flow.Child(flow.Object).ui(hidden=True)

    

    _RUNNERS_FACTORY = None

    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        if slot_name == 'libreflow.baseflow.film.Film':
            return Film
        elif slot_name == 'libreflow.baseflow.shot.Sequence':
            return Sequence
        elif slot_name == 'libreflow.baseflow.shot.Shot':
            return Shot
        elif slot_name == 'libreflow.baseflow.asset.Asset':
            return Asset
        elif slot_name == 'libreflow.baseflow.asset.AssetFamily':
            return AssetFamily
        elif slot_name == 'libreflow.baseflow.asset.AssetType':
            return AssetType
        elif slot_name == 'libreflow.baseflow.asset.AssetLibrary':
            return AssetLibrary
        elif slot_name == 'libreflow.baseflow.task.ManagedTask':
            return Task
        elif slot_name == 'libreflow.baseflow.task.ManageTaskCollection':
            return Tasks
        elif slot_name == 'libreflow.baseflow.file.TrackedFile':
            return TrackedFile
        elif slot_name == 'libreflow.baseflow.file.TrackedFolder':
            return TrackedFolder
        elif slot_name == 'libreflow.baseflow.file.Revision':
            return Revision
        elif slot_name == 'libreflow.baseflow.file.TrackedFolderRevision':
            return TrackedFolderRevision
        elif slot_name == 'libreflow.baseflow.users.User':
            return User
        elif slot_name == 'libreflow.baseflow.users.Users':
            return Users
        elif slot_name == 'libreflow.baseflow.ProjectSettings':
            return ProjectSettings
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            settings = super(Project, self).get_default_contextual_edits(context_name)
            settings.update(dict(
                path_format='{film}/{sequence}/{shot}/{task}/{file}/{revision}/{file_base_name}',
                user=self.get_user_name(),
                user_code=self.get_user().get_code(),
                site=self.get_current_site_name(),
                site_code=self.get_current_site().get_code(),
            ))
            return settings
        else:
            return super(Project, self).get_default_contextual_edits(context_name)

    def get_context_names(self):
        return ['settings']

    def update_user_last_visit(self):
        user_login = self.get_user_name()
        requiredVersion = self.get_required_versions()

        if not user_login or not requiredVersion:
            return

        users = self.admin.users

        if user_login not in users.mapped_names():
            return
        user = users[user_login]

        user._last_visit.set(time.time())
        for v in requiredVersion:
            if v[0] == 'libreflow.flows':
                user._last_project_used_version.set(v[1])
            elif v[0] == 'libreflow':
                user._last_libreflow_used_version.set(v[1])

    def get_required_versions(self):
        '''
        return a list of dependencies
        [dependecyName, currentVersion, requiredVersion, updateNeeded(0:no|1:yes minor|2: yes major)],[]
        '''
        versions = []

        libreflow_cur_version = version.parse(libreflow_version.get_versions()['version'])
        libreflow_req_version = version.parse(self.admin.project_settings.libreflow_version.get())
        
        if libreflow_cur_version < libreflow_req_version \
                and ((libreflow_cur_version.major < libreflow_req_version.major) or \
                    (libreflow_cur_version.minor < libreflow_req_version.minor)):
            # VERY IMPORTANT UPDATE
            libreflow_needs_update = 2
        elif libreflow_cur_version < libreflow_req_version:
            # MINOR UPDATE
            libreflow_needs_update = 1
        else:
            # NO UDPATE
            libreflow_needs_update = 0

        versions.append(['libreflow', str(libreflow_cur_version), str(libreflow_req_version), libreflow_needs_update])
        
        project_cur_version = version.parse(libreflowthesiren_version.get_versions()['version'])
        project_req_version = version.parse(self.admin.project_settings.project_version.get())

        if project_cur_version < project_req_version \
                and ((project_cur_version.major < project_req_version.major) or \
                    (project_cur_version.minor < project_req_version.minor)):
            # VERY IMPORTANT UPDATE
            project_needs_update = 2
        elif project_cur_version < project_req_version:
            # MINOR UPDATE
            project_needs_update = 1
        else:
            # NO UDPATE
            project_needs_update = 0

       
        versions.append(['libreflow.flows', str(project_cur_version), str(project_req_version), project_needs_update])
    
        for v in versions:
            self.root().session().log_debug(v)
        return versions
    
    def get_default_file_presets(self):
        return self.admin.project_settings.default_files
    
    def get_entity_manager(self):
        return self.admin.entity_manager
    
    def get_task_manager(self):
        return self.admin.project_settings.task_manager

    def get_entity_store(self):
        return self.get_entity_manager().store
    
    def get_action_value_store(self):
        return self.get_entity_manager().action_value_store
