import enum
from kabaret import flow
from kabaret.flow_entities.entities import Entity, Property
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict

from ..utils.kabaret.flow_entities.entities import EntityView

from .file import FileSystemMap, FileSystemRefCollection, FileJobs
from .task_manager import CreateTaskDefaultFiles, CreateTaskDefaultFilesPage2
from .users import PresetSessionValue, ToggleBookmarkAction


class IconSize(enum.Enum):

    SMALL  = 0
    MEDIUM = 1
    LARGE  = 2


class Task(Entity):
    """
    Defines an arbitrary task containing a list of files.

    Instances provide the `task` and `task_display_name` keys
    in their contextual dictionary (`settings` context).
    """
    
    display_name = Property().ui(hidden=True)
    code         = Property().ui(hidden=True)
    prefix       = Property().ui(hidden=True)
    position     = Property().ui(hidden=True)
    enabled      = Property().ui(hidden=True, editor='bool')
    icon_small   = Property().ui(hidden=True)
    icon_medium  = Property().ui(hidden=True)
    icon_large   = Property().ui(hidden=True)
    color        = Property().ui(hidden=True)

    files = flow.Child(FileSystemMap).ui(
        expanded=True,
        action_submenus=True,
        items_action_submenus=True
    )
    file_refs = flow.Child(FileSystemRefCollection).ui(
        expanded=True,
        action_submenus=True,
        items_action_submenus=True
    )

    settings = flow.Child(ContextualView).ui(hidden=True)
    primary_files = Property().ui(hidden=True)
    priority_actions  = Property().ui(hidden=True)

    toggle_bookmark = flow.Child(ToggleBookmarkAction).ui(hidden=True)

    jobs = flow.Child(FileJobs).ui(hidden=True)

    ordered_site_names = flow.SessionParam({}, PresetSessionValue).ui(hidden=True)

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                task=self.name(),
                task_display_name=self.get_display_name(),
                task_code=self.get_code(),
                task_prefix=self.get_prefix(),
            )
    
    def get_display_name(self):
        return self.display_name.get() or self.name()
    
    def get_code(self):
        return self.code.get() or self.name()
    
    def get_prefix(self):
        return self.prefix.get() or ''
    
    def get_position(self):
        return self.position.get() or 0
    
    def get_icon(self, size=IconSize.SMALL):
        icon = self.get_sized_icon(size)
        if not icon:
            icon = ('icons.gui', 'cog-wheel-silhouette')

        return tuple(icon)
    
    def get_sized_icon(self, size):
        icon = None
        if size == IconSize.SMALL:
            icon = self.icon_small.get()
        elif size == IconSize.MEDIUM:
            icon = self.icon_medium.get()
        else:
            icon = self.icon_large.get()
        return icon
    
    def get_color(self):
        return self.color.get() or None
    
    def has_file_ref(self, file_oid):
        '''
        Returns True if this task has a reference to the file with
        oid `file_oid`.
        '''
        return self.file_refs.has_ref(file_oid)
    
    def get_files(self, include_links=False, file_type=None, primary_only=False):
        '''
        Returns a list of files related to this task.
        
        The items in the output list are `FileSystemItem` instances
        sorted by oid.
        By default, only files existing in the `files` map of this
        task are returned. If `include_links` is true, the output
        list will also contain files existing as references in the
        `file_refs` map.
        The `file_type` argument can be used to filter the returned
        elements by their type. This can be a single type (string)
        or a list of types (list of strings). Linked files are
        filtered according to the type they belong to in this task.
        If `primary_only` is true, only primary files are returned.
        '''
        files = self.files.mapped_items()
        
        if file_type is not None:
            if isinstance(file_type, str):
                file_type = [file_type]
            
            files = [
                f for f in files
                if f.file_type.get() in file_type
            ]
        
        if include_links:
            files += [
                ref.get()
                for ref in self.file_refs.mapped_items()
                if file_type is None or ref.file_type.get() in file_type
            ]
        
        if primary_only:
            files = [
                f for f in files
                if f.is_primary_file.get()
            ]
        
        files = sorted(files, key=lambda f: f.oid())
        
        return files

    def get_primary_files(self):
        '''
        Returns the oids of the primary files of this task as a list.
        '''
        primary_names = [n.replace('.', '_') for n in self.get_primary_file_names() or []]
        mapped_names = self.files.mapped_names()
        primary_files = []
        
        for n in mapped_names:
            if n in primary_names or self.files[n].is_primary_file.get():
                primary_files.append(self.files[n].oid())
        
        return primary_files
    
    def get_primary_file_names(self):
        return self.primary_files.get() or None
    
    def _fill_ui(self, ui):
        ui['custom_page'] = 'libreflow.baseflow.ui.task.TaskPageWidget'


class EnableDefaultTaskAction(flow.Action):

    _item = flow.Parent()
    _map  = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        if self._item.exists():
            return
        
        self._item.enabled.set(
            not self._item.enabled.get()
        )
        self._item.touch()


class DefaultTaskViewItem(flow.Object):

    display_name = flow.SessionParam().ui(hidden=True)
    enabled      = flow.SessionParam().ui(editor='bool')

    toggle_enabled = flow.Child(EnableDefaultTaskAction)

    _map = flow.Parent()
    _action = flow.Parent(2)

    def __init__(self, parent, name):
        super(DefaultTaskViewItem, self).__init__(parent, name)
        self.default = None

    def refresh(self):
        self.default = self._map.get_default_task(self.name())
        self.display_name.set(self.default.display_name.get())
        self.enabled.set(
            not self.exists() and self.default.enabled.get()
        )
    
    def exists(self):
        return self._action.get_task_map().has_mapped_name(self.name())
    
    def create(self):
        task = self._action.get_task_map().add(self.name())
        task.enabled.set(True)
        self._action.get_task_map().touch()
    
    def get_icon(self):
        return self.default.get_icon()


class RefreshDefaultTaskView(flow.Action):
    
    ICON = ('icons.libreflow', 'refresh')
    _map = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._map.refresh()


class DefaultTaskView(flow.DynamicMap):

    refresh_action = flow.Child(RefreshDefaultTaskView).ui(label='Refresh')
    _action = flow.Parent()
    _map = flow.Parent(2)
    _entity = flow.Parent(3)

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(DefaultTaskViewItem)
    
    def __init__(self, parent, name):
        super(DefaultTaskView, self).__init__(parent, name)
        self._cache = None
        self._names = None
    
    def mapped_names(self, page_num=0, page_size=None):
        if self._cache is None:
            self._mng.children.clear()

            settings = get_contextual_dict(self._entity, 'settings')
            entity_type = 'asset' if 'asset' in settings else 'shot'
            default_tasks = self._map.get_task_manager().get_default_tasks(
                template_name=entity_type,
                exclude_optional=not self._action.show_optional.get(),
                entity_oid=self._entity.oid() if not self._action.show_filtered.get() else None
            )
            self._names = [dt.name() for dt in default_tasks]
            self._cache = {dt.name(): dt for dt in default_tasks}

        return self._names
    
    def columns(self):       
        return ['Enabled', 'Name']
    
    def refresh(self):
        self.reset_cache()
        self.touch()
    
    def reset_cache(self):
        self._cache = None
    
    def get_default_task(self, name):
        self.mapped_names()
        return self._cache[name]
    
    def _configure_child(self, item):
        item.refresh()
    
    def _fill_row_cells(self, row, item):
        row['Enabled'] = ''
        row['Name'] = item.display_name.get()
    
    def _fill_row_style(self, style, item, row):
        style['Name_icon'] = item.get_icon()

        if item.exists():
            style['Enabled_icon'] = ('icons.gui', 'check-box-empty-dark')
            for col in self.columns():
                style['%s_foreground-color' % col] = '#4e5255'
        elif item.enabled.get():
            style['Enabled_icon'] = ('icons.gui', 'check')
        else:
            style['Enabled_icon'] = ('icons.gui', 'check-box-empty')
        
        for col in ['Enabled', 'Name']:
            style['%s_activate_oid' % col] = item.toggle_enabled.oid()


class CreateDefaultTasksAction(flow.Action):

    default_tasks = flow.Child(DefaultTaskView).ui(expanded=True)
    show_optional = flow.SessionParam(True).ui(
        editor='bool', label='Show optional tasks').watched()
    show_filtered = flow.SessionParam(False).ui(
        editor='bool', label='Show filtered tasks').watched()
    
    _map = flow.Parent()
    _entity = flow.Parent(2)

    def needs_dialog(self):
        self.default_tasks.reset_cache()
        self.show_optional.set_watched(False)
        self.show_filtered.set_watched(False)
        self.show_optional.revert_to_default()
        self.show_filtered.revert_to_default()
        self.show_optional.set_watched(True)
        self.show_filtered.set_watched(True)
        return True
    
    def allow_context(self, context):
        return context

    def get_buttons(self):
        return ['Create', 'Cancel']
      
    def get_task_map(self):
        return self._map
    
    def child_value_changed(self, child_value):
        if child_value in (self.show_optional, self.show_filtered):
            self.default_tasks.refresh()
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        for item in self.default_tasks.mapped_items():
            if item.exists() or not item.enabled.get():
                continue
            
            item.create()


class TaskCollection(EntityView):
    """
    Defines a collection of tasks.
    """

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Task)
    
    def mapped_names(self, page_num=0, page_size=None):
        '''
        Returns task names sorted by task positions.
        '''
        names = super(TaskCollection, self).mapped_names(page_num, page_size)
        return sorted(names, key=self.get_task_position)
    
    def get_task_position(self, task_name):
        '''
        Returns the position of the task `task_name` in this
        collection. If not defined (i.e. not `None` neither `""`),
        returns `0`.
        '''
        super(TaskCollection, self).mapped_names() # ensure cache exists
        oid = f'{self.oid()}/{task_name}'
        pos = self._document_cache[oid].get('position')
        if pos is None or pos == "":
            pos = 0
        return pos
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_task_collection().collection_name()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.get_display_name()

    def _fill_row_style(self, style, item, row):
        style['icon'] = item.get_icon()
        style['foreground-color'] = item.get_color()


# Managed tasks
# -------------------------


class ProjectUserNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    STRICT_CHOICES = False

    _task = flow.Parent(2)

    def choices(self):
        users = set(self.root().project().get_users().mapped_names())
        assigned_users = set(self._task.assigned_users.get())
        
        return list(users - assigned_users)
    
    def revert_to_default(self):
        names = self.choices()
        if names:
            self.set(names[0])


class SubtaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'multichoice'

    STRICT_CHOICES = False

    _action = flow.Parent()
    _task = flow.Parent(2)

    def choices(self):
        tm = self.root().project().get_task_manager()
        return tm.get_subtasks(self._task.name())
    
    def update_assigned_tasks(self):
        assigned_subtasks = self._task.get_assigned_subtasks(
            self._action.user.get()
        )
        self.set(assigned_subtasks)


# class EditUserAssignations(flow.Action):

#     user     = flow.SessionParam(value_type=ProjectUserNames).watched()
#     subtasks = flow.SessionParam(list, value_type=SubtaskNames)

#     _task = flow.Parent()

#     def needs_dialog(self):
#         self.user.revert_to_default()
#         self.subtasks.update_assigned_tasks()
#         return True
    
#     def get_buttons(self):
#         return ['Save', 'Close']
    
#     def run(self, button):
#         if button == 'Close':
#             return
        
#         assigned = set(self.subtasks.get())
#         unassigned = set(self.subtasks.choices()) - assigned

#         for st in assigned:
#             self._task.assign_users(self.user.get(), subtask_name=st)
#         for st in unassigned:
#             self._task.unassign_users(self.user.get(), subtask_name=st)
        
#         return self.get_result(close=False)
    
#     def child_value_changed(self, child_value):
#         if child_value is self.user:
#             self.subtasks.update_assigned_tasks()


class ManagedTask(Task):
    """
    A ManagedTask provides features handled by the task
    manager of the project.
    """

    assigned_users         = Property().ui(hidden=True)
    subtask_assigned_users = Property().ui(hidden=True)
    current_subtask        = Property().ui(hidden=True)
    
    create_dft_files = flow.Child(CreateTaskDefaultFiles).ui(
        label='Create default files',
        dialog_size=(600, 400)
    )
    create_dft_files_page2 = flow.Child(CreateTaskDefaultFilesPage2).ui(
        hidden=True,
        dialog_size=(600, 400)
    )
    # edit_assignations = flow.Child(EditUserAssignations)

    def get_display_name(self):
        name = self.display_name.get()
        if not name:
            name = self.get_task_manager().get_task_display_name(self.name())
        
        return name
    
    def get_code(self):
        code = self.code.get()
        if not code:
            code = self.get_task_manager().get_task_code(self.name())
        
        return code

    def get_prefix(self):
        prefix = self.prefix.get()
        if not prefix:
            prefix = self.get_task_manager().get_task_prefix(self.name())
        
        return prefix
    
    def get_position(self):
        position = self.position.get()
        if position is None or position == '':
            position = self.get_task_manager().get_task_position(self.name())
        
        return position

    def get_icon(self, size=IconSize.MEDIUM):
        icon = self.get_sized_icon(size)
        if not icon:
            icon = (
                self.get_task_manager().get_task_icon(self.name())
                or ('icons.gui', 'cog-wheel-silhouette'))
        
        return tuple(icon)

    def get_color(self):
        color = self.color.get()
        if not color:
            color = self.get_task_manager().get_task_color(self.name()) or None
        
        return color

    def is_assigned(self, user_name, subtask_name=None):
        assigned_users = self._get_assigned_users(subtask_name)
        assigned = user_name in assigned_users

        if subtask_name is None and not assigned:
            # If not explicitly assigned to the task, check if user is assigned to one of its subtasks
            st_assigned_users = self.subtask_assigned_users.get() or {}
            assigned |= user_name in set().union(*st_assigned_users.values())
        
        return assigned

    # def assign_users(self, *user_names, subtask_name=None):
    #     names = set(self._get_assigned_users(subtask_name))
    #     names |= set(user_names)
    #     self._set_assigned_users(list(names), subtask_name)

    # def unassign_users(self, *user_names, subtask_name=None):
    #     names = set(self._get_assigned_users(subtask_name))
    #     names -= set(user_names)
    #     self._set_assigned_users(list(names), subtask_name)
    
    def get_assigned_subtasks(self, user_name):
        assigned_users = self.subtask_assigned_users.get() or {}
        return [
            st for st, user_names in assigned_users.items()
            if user_name in user_names
        ]
    
    def get_primary_file_names(self):
        names = super(ManagedTask, self).get_primary_file_names()

        if names is None:
            names = self.get_task_manager().get_task_primary_file_names(self.name())
        
        return names
    
    def get_task_manager(self):
        return self.root().project().get_task_manager()
    
    def _get_assigned_users(self, subtask_name=None):
        if subtask_name is None:
            names = self.assigned_users.get() or []
        else:
            assigned_users = self.subtask_assigned_users.get() or {}
            names = assigned_users.get(subtask_name, [])
        
        return names
    
    def _set_assigned_users(self, user_names, subtask_name=None):
        if subtask_name is None:
            self.assigned_users.set(user_names)
        else:
            assigned_users = self.subtask_assigned_users.get() or {}
            assigned_users[subtask_name] = user_names
            self.subtask_assigned_users.set(assigned_users)


class ManagedTaskCollection(TaskCollection):
    
    add_task = flow.Child(CreateDefaultTasksAction).ui(dialog_size=(550, 470))

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(ManagedTask)

    def get_task_position(self, task_name):
        '''
        If defined (i.e. not `None` neither `""`), returns the
        position of the task `task_name` in this collection, or
        the position of the corresponding default task in the
        task manager otherwise.
        If no default task exists with the given name, returns `0`.
        '''
        super(TaskCollection, self).mapped_names() # ensure cache exists
        oid = f'{self.oid()}/{task_name}'
        pos = self._document_cache[oid].get('position')
        if pos is None or pos == "":
            mgr = self.get_task_manager()
            pos = mgr.get_task_position(task_name)
        
        return pos
            
    def get_task_manager(self):
        return self.root().project().get_task_manager()
