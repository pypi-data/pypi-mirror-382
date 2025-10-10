from kabaret import flow
from libreflow.baseflow.shot import ShotCollection, Shot as BaseShot, Sequence as BaseSequence

from .task import Tasks


class Shot(BaseShot):
    
    tasks = flow.Child(Tasks).ui(
        expanded=True,
        show_filter=True
    )
    
    def ensure_tasks(self):
        """
        Creates the tasks of this shot based on the task
        templates of the project, skipping any existing task.
        """
        mgr = self.root().project().get_task_manager()

        for dt in mgr.get_default_tasks(template_name='shot', exclude_optional=True, entity_oid=self.oid()):
            if not self.tasks.has_mapped_name(dt.name()):
                t = self.tasks.add(dt.name())
                t.enabled.set(dt.enabled.get())
        
        self.tasks.touch()


class Shots(ShotCollection):

    def add(self, name, object_type=None):
        """
        Adds a shot to the global shot collection, and creates
        its tasks.
        """
        s = super(Shots, self).add(name, object_type)
        s.ensure_tasks()

        return s


class CreateKitsuShots(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    skip_existing = flow.SessionParam(False).ui(editor='bool')
    create_task_default_files = flow.SessionParam(True).ui(editor='bool')

    _sequence = flow.Parent()
    _film = flow.Parent(3)

    def get_buttons(self):
        return ['Create shots', 'Cancel']

    def allow_context(self, context):
        return context and context.endswith('.details')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        session = self.root().session()

        project_type = self.root().project().kitsu_config().project_type.get()
        
        skip_existing = self.skip_existing.get()
        shots_data = self.root().project().kitsu_api().get_shots_data(
            self._sequence.name(),
            episode_name=self._film.name() if project_type == 'tvshow' else None
        )
        for data in shots_data:
            name = data['name']

            if not self._sequence.shots.has_mapped_name(name):
                session.log_info(f'[Create Kitsu Shots] Creating Shot {name}')
                s = self._sequence.shots.add(name)
            elif not skip_existing:
                s = self._sequence.shots[name]
                session.log_info(f'[Create Kitsu Shots] Updating Default Tasks {name}')
                s.ensure_tasks()
            else:
                continue
            
            if self.create_task_default_files.get():
                for t in s.tasks.mapped_items():
                    session.log_info(f'[Create Kitsu Shots] Updating Default Files {name} {t.name()}')
                    t.create_dft_files.files.update()
                    t.create_dft_files.run(None)
        
        self._sequence.shots.touch()


class Sequence(BaseSequence):
    
    shots = flow.Child(Shots).ui(
        expanded=True,
        show_filter=True,
        default_height=600
    )

    create_shots = flow.Child(CreateKitsuShots)
