import datetime
import timeago
from kabaret import flow
from libreflow.baseflow.users import SessionUserStatus
from libreflow.baseflow.users import User as BaseUser
from libreflow.baseflow.users import Users as BaseUsers


class KitsuUsersChoiceValue(flow.values.MultiChoiceValue):

    init = True
    kitsu_list = []

    def choices(self):
        if self.init == True:
            self.kitsu_list = self.root().project().kitsu_api().get_users()
            
            users = self.root().project().get_users().mapped_items()
            for user in users:
                if user.login.get() in self.kitsu_list:
                    self.kitsu_list.remove(user.login.get())
            
            self.init = False
        
        if self.kitsu_list == ['']:
            self.kitsu_list = []

        return self.kitsu_list

    def revert_to_default(self):
        self.choices()
        self.set([])
    
    def _fill_ui(self, ui):
        super(KitsuUsersChoiceValue, self)._fill_ui(ui)
        if self.choices() == []:
            ui['hidden'] = True


class KitsuUsersCreateAll(flow.values.SessionValue):

    DEFAULT_EDITOR = 'bool'

    _action = flow.Parent()

    def _fill_ui(self, ui):
        super(KitsuUsersCreateAll, self)._fill_ui(ui)
        if self._action.users_choices.choices() == []:
            ui['hidden'] = True


class User(BaseUser):

    last_visit = flow.Computed()
    libreflow_version = flow.Computed().ui(label="libreflow") 
    project_version = flow.Computed().ui(label="libreflow.flows") 
    _last_visit = flow.IntParam(0)
    _last_libreflow_used_version = flow.Param(None)
    _last_project_used_version = flow.Param(None)

    def compute_child_value(self, child_value):
        if child_value is self.last_visit:
            if self._last_visit.get() == 0:
                child_value.set("never")
            else:
                
                last_connection = datetime.datetime.fromtimestamp(self._last_visit.get())
                now = datetime.datetime.now()
                child_value.set(timeago.format(last_connection, now))
        elif child_value is self.libreflow_version:
            from packaging import version
            requiered_version = version.parse(self.root().project().admin.project_settings.libreflow_version.get())
            user_current_version = self._last_libreflow_used_version.get()
            if not user_current_version:
                child_value.set("Unknown")
            else:
                user_current_version = version.parse(user_current_version)
                if requiered_version > user_current_version:
                    child_value.set("%s (!)" % str(user_current_version))
                else:
                    child_value.set("%s" % str(user_current_version))
        elif child_value is self.project_version:
            from packaging import version
            requiered_version = version.parse(self.root().project().admin.project_settings.project_version.get())
            user_current_version = self._last_project_used_version.get()
            if not user_current_version:
                child_value.set("Unknown")
            else:
                user_current_version = version.parse(user_current_version)
                if requiered_version > user_current_version:
                    child_value.set("%s (!)" % str(user_current_version))
                else:
                    child_value.set("%s" % str(user_current_version))


class CreateKitsuUsersPage1(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    select_all    = flow.SessionParam(False, KitsuUsersCreateAll).ui(editor='bool').watched()
    users_choices = flow.Param([], KitsuUsersChoiceValue).ui(label='Users')

    _map = flow.Parent()

    def get_buttons(self):
        if self.users_choices.choices() == []:
            self.message.set('No new users were found on Kitsu.')
            return ['Cancel']
        self.users_choices.revert_to_default()
        self.message.set('<h2>Select users to create</h2>')
        return ['Select', 'Cancel']

    def child_value_changed(self, child_value):
        if child_value is self.select_all:
            if child_value.get():
                self.users_choices.set(self.users_choices.choices())
            else:
                self.users_choices.revert_to_default()
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        return self.get_result(next_action=self._map.create_users_page_2.oid())


class KitsuUserData(flow.Object):

    ICON = ("icons.gui", "user")

    user_login = flow.Param()
    user_status = flow.SessionParam("User", SessionUserStatus)


class KitsuUsersChoices(flow.DynamicMap):

    ICON = ("icons.gui", "team")

    STYLE_BY_STATUS = {
        'User': ('icons.gui', 'user'),
        'Admin': ('icons.gui', 'user-admin'),
        'Supervisor': ('icons.gui', 'user-lead')
    }
    
    _map = flow.Parent(2)

    def __init__(self, parent, name):
        super(KitsuUsersChoices, self).__init__(parent, name)
        self.users = None

    @classmethod
    def mapped_type(cls):
        return KitsuUserData
    
    def mapped_names(self, page_num=0, page_size=None):
        choices = self._map.create_users.users_choices.get()

        self.users = {}
        for i, user in enumerate(choices):
            data = {}
            data.update(dict(
                user_login=user
            ))
            self.users['user'+str(i)] = data
        
        return self.users.keys()

    def columns(self):
        return ['Login', 'Status']

    def _configure_child(self, child):
        child.user_login.set(self.users[child.name()]['user_login'])

    def _fill_row_cells(self, row, item):
        row['Login'] = item.user_login.get()
        row['Status'] = item.user_status.get()

    def _fill_row_style(self, style, item, row):
        style['icon'] = self.STYLE_BY_STATUS[item.user_status.get()]


class CreateKitsuUsersPage2(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    users = flow.Child(KitsuUsersChoices).ui(expanded=True)

    _map = flow.Parent()

    def allow_context(self, context):
        return context and context.endswith('.details')

    def get_buttons(self):
        self.message.set('<h2>Change status if needed</h2>')
        return ['Create users', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
       
        for item in self.users.mapped_items():
            user_name = item.user_login.get().replace('.', '').replace('-', '')
            if not self._map.get_user(item.user_login.get()):
                self.root().session().log_info(f'[Create Kitsu Users] Creating User {item.user_login.get()}')
                self._map.add_user(user_name, item.user_login.get(), item.user_status.get())
        
        self._map.touch()


class Users(BaseUsers):

    create_users = flow.Child(CreateKitsuUsersPage1)
    create_users_page_2 = flow.Child(CreateKitsuUsersPage2).ui(hidden=True)


class CheckUsersAction(flow.Action):

    def get_buttons(self):
        return ['Cancel']

    def needs_dialog(self):
        return False

    def run(self, button):
        project = self.root().project()
        users = project.admin.users
        print("\n                       #### USERS LAST CONNECTIONS AND VERSIONS ####")
        head = "|         user         |   last seen    |          libreflow         |      libreflow.thesiren    |"
        
        h = "" 
        for i in range(0,len(head)):
            h+= "-"
        print(h)
        print(head)
        print(h)

        for u in users.mapped_items():
            name = u.name()


            print("| %-20s | %14s | %-26s | %-26s |" % (name,
                    u.last_visit.get(),
                    u.libreflow_version.get(),
                    u.project_version.get(),
                    ))

        print(h + "\n")
