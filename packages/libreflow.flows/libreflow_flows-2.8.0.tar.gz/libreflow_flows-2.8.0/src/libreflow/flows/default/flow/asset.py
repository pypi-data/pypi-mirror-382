from kabaret import flow
from libreflow.baseflow.asset import (
    Asset               as BaseAsset,
    AssetFamily         as BaseAssetFamily,
    AssetType           as BaseAssetType,
    AssetTypeCollection as BaseAssetTypeCollection,
    AssetLibrary        as BaseAssetLibrary,
    AssetLibraryCollection as BaseAssetLibraryCollection,
    AssetCollection
)

from .task import Tasks


class Asset(BaseAsset):
    
    tasks = flow.Child(Tasks).ui(expanded=True)

    def ensure_tasks(self):
        """
        Creates the tasks of this asset based on the default
        tasks created with a template named `asset`, skipping
        any existing task.
        """
        mgr = self.root().project().get_task_manager()

        for dt in mgr.get_default_tasks(template_name='asset', exclude_optional=True, entity_oid=self.oid()):
            if not self.tasks.has_mapped_name(dt.name()):
                t = self.tasks.add(dt.name())
                t.enabled.set(dt.enabled.get())
        
        self.tasks.touch()
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.baseflow.ui.task.TasksCustomWidget'


class CreateKitsuAssets(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    skip_existing = flow.SessionParam(False).ui(editor='bool')
    create_task_default_files = flow.SessionParam(True).ui(editor='bool')

    _asset_lib = flow.Parent(4)
    _asset_type = flow.Parent(2)
    _assets = flow.Parent()

    def allow_context(self, context):
        return context

    def get_buttons(self):
        return ['Create assets', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        session = self.root().session()
        kitsu_api = self.root().project().kitsu_api()
        kitsu_config = self.root().project().kitsu_config()

        episode_name = None
        if kitsu_config.project_type.get() == 'tvshow' and isinstance(self._asset_lib, AssetLibrary):
            episode_name = self._asset_lib.name()
            if episode_name.lower() == 'main_pack':
                episode_name = 'default_episode'

        skip_existing = self.skip_existing.get()
        assets_data = self.root().project().kitsu_api().get_assets_data(self._asset_type.name(), episode_name)
        for data in assets_data:
            name = data['name']

            if not self._assets.has_mapped_name(name):
                session.log_info(f'[Create Kitsu Assets] Creating Asset {name}')
                a = self._assets.add(name)
            elif not skip_existing:
                a = self._assets[name]
                session.log_info(f'[Create Kitsu Assets] Updating Default Tasks {name}')
                a.ensure_tasks()
            else:
                continue

            if self.create_task_default_files.get():
                for t in a.tasks.mapped_items():
                    session.log_info(f'[Create Kitsu Assets] Updating Default Files {name} {t.name()}')
                    t.create_dft_files.files.update()
                    t.create_dft_files.run(None)
        
        self._assets.touch()


class Assets(AssetCollection):

    create_assets = flow.Child(CreateKitsuAssets)

    def add(self, name, object_type=None):
        a = super(Assets, self).add(name, object_type)
        a.ensure_tasks()
        
        return a


class AssetFamily(BaseAssetFamily):
    
    assets = flow.Child(Assets).ui(expanded=True, show_filter=True, default_height=600)

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            edits = super(AssetFamily, self).get_default_contextual_edits(context_name)
            edits['path_format'] = 'lib/{asset_type}/{asset_family}/{asset}/{task}/{file}/{revision}/{asset}_{file_base_name}'
            return edits


class AssetType(BaseAssetType):
    
    assets = flow.Child(Assets).ui(expanded=True, show_filter=True)

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            edits = super(AssetType, self).get_default_contextual_edits(context_name)
            edits['path_format'] = 'lib/{asset_type}/{asset}/{task}/{file}/{revision}/{asset}_{file_base_name}'
            return edits


class AssetModules(AssetType):
    
    asset_families = flow.Child(flow.Object).ui(hidden=True)

    assets = flow.Child(Assets).ui(expanded=True)

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                path_format='lib/{asset_type}/{asset}/{task}/{file}/{revision}/{asset}_{file_base_name}'
            )


class CreateKitsuAssetTypes(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    skip_existing = flow.SessionParam(False).ui(editor='bool')
    create_assets = flow.SessionParam(False).ui(editor='bool')
    create_task_default_files = flow.SessionParam(False).ui(editor='bool')

    _asset_types = flow.Parent()

    def get_buttons(self):
        return ['Create asset types', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return

        session = self.root().session()
        
        asset_types_data = self.root().project().kitsu_api().get_asset_types_data()
        create_assets = self.create_assets.get()
        skip_existing = self.skip_existing.get()

        for data in asset_types_data:
            name = data['name']

            if name == 'x':
                continue

            if not self._asset_types.has_mapped_name(name):
                session.log_info(f'[Create Kitsu Asset Types] Creating Asset Type {name}')
                at = self._asset_types.add(name)
            elif not skip_existing:
                session.log_info(f'[Create Kitsu Asset Types] Asset Type {name} exists')
                at = self._asset_types[name]
            else:
                continue
            
            if create_assets:
                at.assets.create_assets.skip_existing.set(skip_existing)
                at.assets.create_assets.create_task_default_files.set(self.create_task_default_files.get())
                at.assets.create_assets.run('Create assets')
        
        self._asset_types.touch()


class AssetTypeCollection(BaseAssetTypeCollection):

    create_asset_types = flow.Child(CreateKitsuAssetTypes)

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                path_format='lib/{asset_type}/{asset_family}/{asset}/{task}/{file}/{revision}/{asset}_{file_base_name}'
            )


class AssetLibrary(BaseAssetLibrary):

    asset_types = flow.Child(AssetTypeCollection).ui(expanded=True)


class RefreshKitsuMap(flow.Action):
    
    ICON = ('icons.libreflow', 'refresh')

    _map = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._map.refresh()


class ToggleKitsuAssetLib(flow.Action):

    _asset_lib = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._asset_lib.enabled.set(
            not self._asset_lib.enabled.get())
        self._asset_lib.touch()


class KitsuAssetLib(flow.SessionObject):

    lib_name = flow.Param()
    enabled = flow.BoolParam(True)
    exists = flow.BoolParam(False)

    toggle = flow.Child(ToggleKitsuAssetLib)


class KitsuAssetLibs(flow.DynamicMap):

    ICON = ('icons.libreflow', 'kitsu')

    refresh_action = flow.Child(RefreshKitsuMap).ui(label='Refresh')
    _action = flow.Parent()
    _asset_libs = flow.Parent(2)

    @classmethod
    def mapped_type(cls):
        return KitsuAssetLib
    
    def __init__(self, parent, name):
        super(KitsuAssetLibs, self).__init__(parent, name)
        self._cache = None
        self._names = None
    
    def mapped_names(self, page_num=0, page_size=None):
        if self._cache is None:
            self._mng.children.clear()

            i = 0
            self._cache = {}
            self._names = []
            episodes_data = self.root().project().kitsu_api().get_episodes_data()
            existing_libs = self._asset_libs.mapped_names()

            for episode in episodes_data:
                name = episode['name']

                if name == 'x':
                    continue
                
                mapped_name = f'al{i:04}'
                self._names.append(mapped_name)
                self._cache[mapped_name] = dict(
                    name=name,
                    exists=name in existing_libs
                )
                i += 1
            
            self._names.append(f'al{i:04}')
            self._cache[f'al{i:04}'] = dict(
                name='main_pack',
                exists='main_pack' in existing_libs
            )
        
        # Remove asset libs from list if `skip_existing` is true
        names = self._names
        if self._action.skip_existing.get():
            names = [
                n for n in names
                if not self._cache[n]['exists']
            ]
        
        return names

    def columns(self):
        return ['Name']
    
    def refresh(self):
        self._cache = None
        self.touch()

    def _configure_child(self, child):
        self.mapped_names()
        child.lib_name.set(self._cache[child.name()]['name'])
        child.exists.set(self._cache[child.name()]['exists'])
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.lib_name.get()
    
    def _fill_row_style(self, style, item, row):
        style['Name_activate_oid'] = item.toggle.oid()
        style['icon'] = ('icons.gui',
            'check' if item.enabled.get() else 'check-box-empty')

        if item.exists.get():
            for col in self.columns():
                style[f'{col}_foreground_color'] = '#4e5255'


class CreateKitsuAssetLibs(flow.Action):
    '''
    When `create_assets` is enabled, the action creates types and assets
    all at once.
    '''
    
    ICON = ('icons.libreflow', 'kitsu')

    kitsu_asset_libs = flow.Child(KitsuAssetLibs).ui(expanded=True)

    skip_existing = flow.SessionParam(False).ui(editor='bool').watched()
    select_all = flow.SessionParam(True).ui(editor='bool').watched()
    create_asset_types = flow.SessionParam(False).ui(editor='bool')
    create_assets = flow.SessionParam(False).ui(editor='bool').watched()

    _asset_libs = flow.Parent()

    def needs_dialog(self):
        self.kitsu_asset_libs.refresh()
        self.select_all.set_watched(False)
        self.select_all.revert_to_default()
        self.select_all.set_watched(True)
        return True

    def get_buttons(self):
        return ['Create libraries', 'Cancel']
    
    def child_value_changed(self, child_value):
        if child_value is self.skip_existing:
            self.kitsu_asset_libs.touch()
        elif child_value is self.select_all:
            select_all = self.select_all.get()
            for al in self.kitsu_asset_libs.mapped_items():
                al.enabled.set(select_all)
            self.kitsu_asset_libs.touch()
        elif child_value is self.create_assets:
            self.create_asset_types.set(True)
    
    def run(self, button):
        if button == 'Cancel':
            return

        session = self.root().session()

        create_asset_types = self.create_asset_types.get()
        create_assets = self.create_assets.get()
        skip_existing = self.skip_existing.get()

        for kitsu_al in self.kitsu_asset_libs.mapped_items():
            if not kitsu_al.enabled.get():
                continue
            
            name = kitsu_al.lib_name.get()

            if not self._asset_libs.has_mapped_name(name):
                session.log_info(f'[Create Kitsu Asset Libs] Creating Asset Lib {name}')
                al = self._asset_libs.add(name)
            elif not skip_existing:
                session.log_info(f'[Create Kitsu Asset Libs] Asset Lib {name} exists')
                al = self._asset_libs[name]
            else:
                continue

            if create_asset_types:
                al.asset_types.create_asset_types.skip_existing.set(skip_existing)
                if create_assets:
                    al.asset_types.create_asset_types.create_assets.set(create_assets)
                al.asset_types.create_asset_types.run('Create asset types')
        
        self._asset_libs.touch()


class AssetLibraryCollection(BaseAssetLibraryCollection):
    
    create_libs = flow.Child(CreateKitsuAssetLibs).ui(label='Create asset libraries')