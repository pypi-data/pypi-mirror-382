from kabaret import flow
from kabaret.flow_entities.entities import Entity, Property
from kabaret.flow_contextual_dict import ContextualView

from .maputils import SimpleCreateAction
from ..utils.kabaret.flow_entities.entities import EntityView
from ..utils.flow.process_files import PlaySequenceAction, PlaySequenceActionFromShot


class Shot(Entity):
    """
    Defines a shot.

    Instances provide the `shot` key in their contextual
    dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'shot')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    settings = flow.Child(ContextualView).ui(hidden=True)

    play_sequence = flow.Child(PlaySequenceActionFromShot).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                shot=self.name(),
                shot_code=self.code.get(),
                shot_display_name=self.display_name.get()
            )
    
    def get_default_tasks(self, force_update=False):
        return self.root().project().get_default_tasks().mapped_names()
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.baseflow.ui.task.TasksCustomWidget'


class ShotCollection(EntityView):
    """
    Defines a collection of shots.
    """

    ICON = ('icons.flow', 'shot')

    add_shot_action = flow.Child(SimpleCreateAction).ui(
        label='Add shot'
    )
    
    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Shot)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_shot_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()


class Sequence(Entity):
    """
    Defines a sequence containing a list of shots.

    Instances provide the `sequence` key in their contextual
    dictionary (`settings` context).
    """

    ICON = ('icons.flow', 'sequence')

    code = Property().ui(hidden=True)
    display_name = Property().ui(hidden=True)

    shots = flow.Child(ShotCollection).ui(
        expanded=True, 
        show_filter=True
    )

    settings = flow.Child(ContextualView).ui(hidden=True)

    play_sequence = flow.Child(PlaySequenceAction).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])

    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                sequence=self.name(),
                sequence_code=self.code.get(),
                sequence_display_name=self.display_name.get()
            )


class SequenceCollection(EntityView):
    """
    Defines a collection of sequences.
    """

    ICON = ('icons.flow', 'sequence')
    
    add_sequence = flow.Child(SimpleCreateAction)
    
    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Sequence)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_sequence_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get() or item.name()
