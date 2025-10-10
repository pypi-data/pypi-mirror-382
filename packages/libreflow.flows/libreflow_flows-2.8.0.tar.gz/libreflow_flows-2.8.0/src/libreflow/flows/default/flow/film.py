from kabaret import flow
from libreflow.baseflow.film import (
    Film as BaseFilm,
    FilmCollection as BaseFilmCollection
)


class CreateKitsuSequences(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    skip_existing = flow.SessionParam(False).ui(editor='bool')
    create_shots = flow.SessionParam(False).ui(editor='bool')
    create_task_default_files = flow.SessionParam(False).ui(editor='bool')

    _film = flow.Parent()

    def get_buttons(self):
        return ['Create sequences', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        session = self.root().session()

        project_type = self.root().project().kitsu_config().project_type.get()

        sequences_data = self.root().project().kitsu_api().get_sequences_data(
            episode_name=self._film.name() if project_type == 'tvshow' else None
        )
        create_shots = self.create_shots.get()
        skip_existing = self.skip_existing.get()

        for data in sequences_data:
            name = data['name']

            if not self._film.sequences.has_mapped_name(name):
                session.log_info(f'[Create Kitsu Sequences] Creating Sequence {name}')
                s = self._film.sequences.add(name)
            elif not skip_existing:
                session.log_info(f'[Create Kitsu Sequences] Sequence {name} exists')
                s = self._film.sequences[name]
            else:
                continue

            if create_shots:
                s.create_shots.skip_existing.set(skip_existing)
                s.create_shots.create_task_default_files.set(self.create_task_default_files.get())
                s.create_shots.run('Create shots')
        
        self._film.sequences.touch()


class Film(BaseFilm):

    create_sequences = flow.Child(CreateKitsuSequences)


class CreateKitsuFilms(flow.Action):

    '''
    Create Films based on Kitsu episodes
    '''

    ICON = ('icons.libreflow', 'kitsu')

    skip_existing = flow.SessionParam(False).ui(editor='bool')
    create_sequences = flow.SessionParam(False).ui(editor='bool')
    create_shots = flow.SessionParam(False).ui(editor='bool')
    create_task_default_files = flow.SessionParam(False).ui(editor='bool')

    _films = flow.Parent()

    def allow_context(self, context):
        return context and context.endswith(".inline") and self.root().project().kitsu_config().project_type.get() == 'tvshow'

    def get_buttons(self):
        return ['Create films', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return

        session = self.root().session()

        episodes_data = self.root().project().kitsu_api().get_episodes_data()

        for data in episodes_data:           
            name = data['name']

            if not self._films.has_mapped_name(name):
                session.log_info(f'[Create Kitsu Films] Creating Film {name} exists')
                f = self._films.add(name)
            elif not self.skip_existing.get():
                session.log_info(f'[Create Kitsu Films] Film {name} exists')
                f = self._films[name]
            else:
                continue

            if self.create_sequences.get():
                f.create_sequences.skip_existing.set(self.skip_existing.get())
                f.create_sequences.create_shots.set(self.create_shots.get())
                f.create_sequences.create_task_default_files.set(self.create_task_default_files.get())

                f.create_sequences.run('Create sequences')
        
        self._films.touch()


class FilmCollection(BaseFilmCollection):

    create_films = flow.Child(CreateKitsuFilms)
