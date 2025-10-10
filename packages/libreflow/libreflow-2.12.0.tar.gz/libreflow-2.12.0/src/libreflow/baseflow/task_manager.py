import os
import re
import sys
import time
import shutil
from collections import defaultdict 
from kabaret import flow
from kabaret.flow_contextual_dict import get_contextual_dict
from kabaret.flow_entities.entities import Entity, Property, PropertyValue
from kabaret.app.ui.gui.icons import gui

from ..utils.kabaret.flow_entities.entities import CustomEntityCollection, PropertyChoiceValue

from ..resources.icons import gui, libreflow, tasks
from .runners import FILE_EXTENSION_ICONS
from .file import TrackedFile


DEFAULT_PATH_FORMAT = '{film}/{sequence}/{shot}/{task}/{file}/{revision}/{sequence}_{shot}_{file_base_name}'


def get_icon(file_name):
    _, ext = os.path.splitext(file_name)
    icon = ('icons.gui', 'folder-white-shape')
    if ext:
        icon = FILE_EXTENSION_ICONS.get(
            ext[1:], ('icons.gui', 'text-file-1')
        ) 

    return icon


# Task default files
# -------------------------


class SelectDefaultFileAction(flow.Action):

    _default_file = flow.Parent()
    _map          = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        # Do nothing if file already exists and no base file defined
        if self._default_file.exists.get() and not self._default_file.base_file_name.get():
            return
        
        # Do nothing if the file already exists, has a base file and revisions have been created
        # if (
        #     self._default_file.exists.get()
        #     and self._default_file.base_file_name.get()
        #     and self._map._file_has_revisions(self._default_file.file_name.get())
        # ):
        #     return
        
        self._default_file.create.set(
            not self._default_file.create.get()
        )
        self._map.touch()


class ToggleUseBaseFileAction(flow.Action):

    _file = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        self._file.use_base_file.set(
            self._file.exists.get()
            or not self._file.use_base_file.get()
        )
        self._map.touch()


class SelectBaseFileAction(flow.Action):

    base_task = flow.SessionParam('')
    base_file = flow.SessionParam('')

    _file = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        self.base_task.set(self._file.from_task.get())
        self.base_file.set(self._file.base_file_name.get())
        return True
    
    def allow_context(self, context):
        return False
    
    def get_buttons(self):
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._file.from_task.set(self.base_task.get())
        self._file.base_file_name.set(self.base_file.get())
        self._file.use_base_file.set(self.base_task.get() and self.base_file.get())
        self._file.create.set(True)
        self._map.touch()


class FileCreationOptionValue(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    STRICT_CHOICES = False

    _file = flow.Parent(2)

    def choices(self):
        choices = ['scratch']
        base_file_name = self._file.base_file_name.get()

        if base_file_name:
            choices = [f'{self._file.from_task.get()}/{self._file.base_file_name.get()}'] + choices
        
        return choices
    
    def revert_to_default(self):
        self.set(self.choices()[0])


class SelectCreationOptionAction(flow.Action):

    create_from = flow.SessionParam('scratch', FileCreationOptionValue)

    _file = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        self.create_from.revert_to_default()
        return True
    
    def allow_context(self, context):
        return False
    
    def get_buttons(self):
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._file.use_base_file.set(self.create_from.get() != 'scratch')
        self._map.touch()


class TaskDefaultFileViewItem(flow.SessionObject):
    """
    Describes a default file to be created in the list of
    files of a task.
    """
    file_name   = flow.Param()
    file_type   = flow.Param()
    path_format = flow.Param()
    create      = flow.BoolParam()
    exists      = flow.BoolParam()
    is_primary_file = flow.Param()
    use_base_file = flow.BoolParam()
    auto_open = flow.BoolParam()
    with flow.group('Template file settings'):
        template_file          = flow.Connection(related_type=TrackedFile)
        template_file_revision = flow.Param()
    with flow.group('Base file settings'):
        from_task = flow.Param()
        base_file_name = flow.Param()

    select                  = flow.Child(SelectDefaultFileAction)
    select_creation_option  = flow.Child(SelectCreationOptionAction)
    select_base_file        = flow.Child(SelectBaseFileAction)


class TaskDefaultFileView(flow.DynamicMap):

    _task = flow.Parent(2)

    def __init__(self, parent, name):
        super(TaskDefaultFileView, self).__init__(parent, name)
        self._cache = None

    @classmethod
    def mapped_type(cls):
        return TaskDefaultFileViewItem

    def mapped_names(self, page_num=0, page_size=None):
        if self._cache is None:
            mgr = self.root().project().get_task_manager()
            default_files = mgr.get_task_files(
                self._task.name(), enabled_only=True
            )

            self._cache = {}

            for n, (file_name, path_format, file_type, optional, is_primary_file, use_base_file, template_file, template_revision, from_task, base_file_name, target_kitsu_task_type, auto_open) in default_files.items():
                n = file_name.replace('.', '_')
                exists = self._file_exists(file_name)
                self._cache[n] = dict(
                    file_name=file_name,
                    file_type=file_type,
                    path_format=path_format,
                    create=not optional and not exists,
                    exists=exists,
                    is_primary_file=is_primary_file,
                    use_base_file=use_base_file,
                    template_file=template_file,
                    template_file_revision=template_revision,
                    from_task=from_task,
                    base_file_name=base_file_name,
                    target_kitsu_task_type=target_kitsu_task_type,
                    auto_open=auto_open,
                )
        
        return self._cache.keys()
    
    def columns(self):
        return ['Do create', 'File', 'From']
    
    def update(self):
        '''
        Update map content rebuilding all its children.
        '''
        self._cache = None
        self._mng.children.clear()
        self.touch()
    
    def _configure_child(self, child):
        self.mapped_names()
        child.file_name.set(self._cache[child.name()]['file_name'])
        child.file_type.set(self._cache[child.name()]['file_type'])
        child.path_format.set(self._cache[child.name()]['path_format'])
        child.create.set(self._cache[child.name()]['create'])
        child.exists.set(self._cache[child.name()]['exists'])
        child.is_primary_file.set(self._cache[child.name()]['is_primary_file'])
        child.use_base_file.set(self._cache[child.name()]['use_base_file'])
        child.template_file.set(self._cache[child.name()]['template_file'])
        child.template_file_revision.set(self._cache[child.name()]['template_file_revision'])
        child.from_task.set(self._cache[child.name()]['from_task'])
        child.base_file_name.set(self._cache[child.name()]['base_file_name'])
        child.auto_open.set(self._cache[child.name()]['auto_open'])
    
    def _fill_row_cells(self, row, item):
        row['Do create'] = ''
        row['File'] = item.file_name.get()

        if item.use_base_file.get():
            row['From'] = f'{item.from_task.get()}/{item.base_file_name.get()}'
        else:
            row['From'] = 'template'
    
    def _fill_row_style(self, style, item, row):
        style['File_icon'] = get_icon(item.file_name.get())

        if item.create.get():
            style['Do create_icon'] = ('icons.gui', 'check')
        else:
            style['Do create_icon'] = ('icons.gui', 'check-box-empty')

        if item.exists.get():
            style['From_activate_oid'] = item.select_base_file.oid()
            style['File_foreground-color'] = '#4e5255'

            if not item.base_file_name.get():
                style['Do create_icon'] = ('icons.gui', 'check-box-empty-dark')
        else:
            style['From_activate_oid'] = item.select_creation_option.oid()
        
        style['Do create_activate_oid'] = item.select.oid()
    
    def _file_exists(self, file_name):
        name, ext = os.path.splitext(file_name)
        if ext:
            exists = self._task.files.has_file(name, ext[1:])
        else:
            exists = self._task.files.has_folder(name)
        
        return exists

    def _file_has_revisions(self, file_name):
        name, ext = os.path.splitext(file_name)

        mapped_name = self._task.files._get_item_mapped_name(name, ext[1:] if ext else None)

        return self._task.files[mapped_name].get_head_revision()


class CreateTaskDefaultFilesPage2(flow.Action):
    
    """
    Display a confirmation message if a
    default file with a base file already exists
    """

    file_names = flow.Param([]).ui(hidden=True)

    _task = flow.Parent()

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return context

    def get_buttons(self):
        self.message.set(f'<font color=#EFDD5B><h3>WARNING: {", ".join(self.file_names.get())} already exists.</h3></font>\nAre you sure to create a new base revision?')
        return ['Yes', 'No']

    def run(self, button):
        # Unchecked create option on files and back to main page
        if button == 'No':
            for name in self.file_names.get():
                obj_name = name.replace('.', '_')
                df = self._task.create_dft_files.files[obj_name].create.set(False)
            
            self.file_names.set([])
            return self.get_result(next_action=self._task.create_dft_files.oid())
        
        # Create files
        for df in self._task.create_dft_files.files.mapped_items():
            if df.create.get():
                self._task.create_dft_files._create_file(df)


class CreateTaskDefaultFiles(flow.Action):

    files = flow.Child(TaskDefaultFileView).ui(expanded=True)

    _task = flow.Parent()
    _tasks = flow.Parent(2)

    def needs_dialog(self):
        self.message.set(f'<h2>Create {self._task.name()} default files</h2>')
        self.files.update()
        return True

    def allow_context(self, context):
        return context

    def get_buttons(self):
        return ['Create', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        # Check for already existing files
        existing_files = [
            df.file_name.get()
            for df in self.files.mapped_items()
            if df.create.get() is True and df.exists.get() is True
        ]
        if existing_files:
            self._task.create_dft_files_page2.file_names.set(existing_files)
            return self.get_result(next_action=self._task.create_dft_files_page2.oid())

        # Create files
        for df in self.files.mapped_items():
            if df.create.get():
                self._create_file(df)
    
    def _create_file(self, default_file):
        session = self.root().session()

        file_name = default_file.file_name.get()
        name, ext = os.path.splitext(file_name)
        target_file = None

        # Create default file
        if not default_file.exists.get():
            if ext:
                session.log_info(f'[Create Task Default Files] Creating File {file_name}')
                target_file = self._task.files.add_file(
                    name, ext[1:],
                    display_name=file_name,
                    tracked=True,
                    default_path_format=default_file.path_format.get()
                )
            else:
                session.log_info(f'[Create Task Default Files] Creating Folder {file_name}')
                target_file = self._task.files.add_folder(
                    name,
                    display_name=file_name,
                    tracked=True,
                    default_path_format=default_file.path_format.get()
                )
            
            target_file.file_type.set(default_file.file_type.get())
            target_file.is_primary_file.set(default_file.is_primary_file.get())
        else:
            session.log_info(f'[Create Task Default Files] File {file_name} exists')
            target_file = self._task.files[default_file.name()]
        
        source_revision = None
        comment = None
        
        # Increment file from base/template file
        if default_file.use_base_file.get():
            from_task = default_file.from_task.get()
            base_file_name = default_file.base_file_name.get()
            base_name, base_ext = os.path.splitext(base_file_name)

            if self._tasks.has_mapped_name(from_task):
                source_task = self._tasks[from_task]
                exists = (
                    base_ext and source_task.files.has_file(base_name, base_ext[1:])
                    or source_task.files.has_folder(base_name))

                if exists:
                    source_file = source_task.files[base_file_name.replace('.', '_')]
                    source_revision = source_file.get_head_revision()
                    
                    if source_revision is not None :
                        if source_revision.get_sync_status() == 'Available':
                            comment = f'from base file {base_file_name} {source_revision.name()}'
                            session.log_info(f'[Create Task Default Files] Use Base File {source_file.display_name.get()} - {source_revision.name()}')
                        elif source_revision.get_sync_status(exchange = True) == 'Available':
                            source_revision.download.run("Confirm")
                            while source_revision.get_sync_status() != "Available":
                                time.sleep(1)
                        else :
                            session.log_error(f'[Create Task Default Files] Revision {source_file.display_name.get()} - {source_revision.name()} is not available, the resulting file will be empty')
        else:
            template_file = default_file.template_file.get()
            if template_file is not None:
                template_file_revision = default_file.template_file_revision.get()
                if template_file_revision == 'Latest':
                    source_revision = template_file.get_head_revision(sync_status='Available')
                else:
                    source_revision = template_file.get_revision(template_file_revision)
                
                if source_revision is not None:
                    comment = f'from template {source_revision.name()}'
                    session.log_info(f'[Create Task Default Files] Use template file {template_file.oid()} - {source_revision.name()}')

        if source_revision is not None and os.path.exists(source_revision.get_path()):
            r = target_file.add_revision(comment=comment)
            session.log_info(f'[Create Task Default Files] Creating Revision {file_name} {r.name()}')

            target_path = r.get_path()
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            session.log_info('[Create Task Default Files] Copying Source Revision')

            if ext:
                shutil.copy2(source_revision.get_path(), target_path)
            else:
                shutil.copytree(source_revision.get_path(), target_path)


# Default file presets
# -------------------------


class FileTypeValue(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return ['Inputs', 'Outputs', 'Works']


class PathFormatValue(flow.values.SessionValue):

    _task = flow.Parent(3)

    def revert_to_default(self):
        # Get path format from default task or template
        path_format = self._task.get_path_format()
        
        # Use contextual dict instead if none
        if path_format is None:
            settings = get_contextual_dict(self, 'settings')
            path_format = settings.get('path_format')
        
        # Fallback to DEFAULT_PATH_FORMAT attribute if still nothing
        if path_format is None:
            super(PathFormatValue, self).revert_to_default()
        else:
            self.set(path_format)


class CreateDefaultFileAction(flow.Action):
    """
    Allows to create a default file in the parent map.
    """

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    file_name   = flow.SessionParam('').ui(
        placeholder='layout.blend'
    )
    file_type   = flow.SessionParam('Works', FileTypeValue)
    path_format = flow.SessionParam(DEFAULT_PATH_FORMAT, PathFormatValue).ui(
        placeholder='{film}/{shot}/{file}/{revision}'
    )
    enabled     = flow.SessionParam(True).ui(editor='bool')
    optional    = flow.SessionParam(False).ui(editor='bool')
    is_primary_file = flow.SessionParam(False).ui(editor='bool')
    use_base_file = flow.SessionParam(False).ui(editor='bool')
    auto_open = flow.SessionParam(False).ui(editor='bool')
    with flow.group('Base file settings'):
        from_task = flow.SessionParam('')
        base_file_name = flow.SessionParam('')

    action_display_order = flow.SessionParam(dict).watched()
    visible_action_count = flow.SessionParam(0).watched()

    _map = flow.Parent()

    def get_buttons(self):
        self.message.set('<h2>Create a default file</h2>')
        self.path_format.revert_to_default()
        return ['Add', 'Cancel']
    
    def child_value_changed(self, child_value):
        if child_value is self.action_display_order:
            self.visible_action_count.touch()
        elif child_value is self.visible_action_count:
            self.visible_action_count.set_watched(False)
            self.visible_action_count.set(min(len(self.action_display_order.get()), self.visible_action_count.get()))
            self.visible_action_count.set_watched(True)
   
    def run(self, button):
        if button == 'Cancel':
            return
        elif not self._filename_is_valid():
            return self.get_result(close=False)
        
        mapped_name = self.file_name.get().replace('.', '_')
        path_format = self.path_format.get() or None # Consider empty path format as undefined

        df = self._map.add(mapped_name)
        df.file_name.set(self.file_name.get())
        df.file_type.set(self.file_type.get())
        df.enabled.set(self.enabled.get())
        df.optional.set(self.optional.get())
        df.is_primary_file.set(self.is_primary_file.get())
        df.auto_open.set(self.auto_open.get())
        df.use_base_file.set(self.use_base_file.get())
        df.from_task.set(self.from_task.get())
        df.base_file_name.set(self.base_file_name.get())
        df.action_display_order.set(self.action_display_order.get())
        df.visible_action_count.set(self.visible_action_count.get())
        df.path_format.set(path_format)

        self._map.touch()
    
    def _filename_is_valid(self):
        title = '<h2>Create a default file</h2>'

        if self.file_name.get() == '':
            self.message.set((
                f'{title}<font color=#D66700>'
                'File name must not be empty.</font>'
            ))
            return False
        
        for df in self._map.mapped_items():
            if self.file_name.get() == df.file_name.get():
                self.message.set((
                    f'{title}<font color=#D66700>A default file '
                    f'named <b>{self.file_name.get()}</b> already '
                    'exists. Please choose another name.</font>'
                ))
                return False
        
        return True


class RemoveDefaultFileAction(flow.Action):

    ICON = ('icons.gui', 'remove-symbol')

    _dft_file   = flow.Parent()
    _map        = flow.Parent(2)
    _template       = flow.Parent(3)
    _mgr        = flow.Parent(5)

    def get_buttons(self):
        self.message.set(
            f'Remove <b>{self._dft_file.file_name.get()}</b> '
            f'from task template <b>{self._template.name()}</b> files ?'
        )
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return

        _map = self._map
        _mgr = self._mgr

        _map.remove(self._dft_file.name())
        _map.touch()
        _mgr.default_files.touch()


# class TemplateFileRevision(PropertyChoiceValue):
class TemplateFileRevision(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    STRICT_CHOICES = False
    _action = flow.Parent()

    def choices(self):
        template_file = self._action.template_file.get()
        if not template_file:
            return []
        names = template_file.get_revision_names(sync_status='Available', published_only=True)
        names.append('Latest')
        return names
    
    def revert_to_default(self):
        self.set('Latest')


class DefaultFile(Entity):
    """
    Defines a preset used to create a file in the project.
    """

    file_name            = Property()
    file_type            = Property()
    path_format          = Property()
    enabled              = Property().ui(editor='bool')
    optional             = Property().ui(editor='bool')
    is_primary_file      = Property().ui(editor='bool')
    use_base_file        = Property().ui(editor='bool')
    auto_open            = Property().ui(editor='bool')
    with flow.group('Template file settings'):
        template_file          = flow.Connection(related_type=TrackedFile)
        # template_file_revision = Property(TemplateFileRevision)
        template_file_revision = Property()
    with flow.group('Base file settings'):
        from_task = Property()
        base_file_name = Property()
    with flow.group('Kitsu settings'):
        target_kitsu_task_type = Property().ui(label='Target Task Type').watched()

    action_display_order = Property()
    visible_action_count = Property()

    remove = flow.Child(RemoveDefaultFileAction)

    def child_value_changed(self, child_value):
        super(DefaultFile, self).child_value_changed(child_value)
        if child_value is self.target_kitsu_task_type:
            # Update task type files dict on kitsu bindings
            if child_value.get() is not None and child_value.get() not in ['', []]:
                self.root().project().kitsu_bindings().set_task_type(
                    self.name(), child_value.get()
                )
            
            # Remove in task type files dict on kitsu bindings
            else:
                task_type_files = self.root().project().kitsu_bindings().task_type_files
                
                existing = [
                    t for t in task_type_files.mapped_items()
                    if self.name() in t.oid_patterns.get()
                ]

                if len(existing) > 0:
                    task_type_files.remove(existing[0].name())
                    task_type_files.touch()


class DefaultFiles(CustomEntityCollection):

    add_dft_file = flow.Child(CreateDefaultFileAction).ui(
        label='Add default file',
        dialog_size=(825, 585)
    )

    @classmethod
    def mapped_type(cls):
        return DefaultFile
    
    def columns(self):
        return ['Enabled', 'Name', 'Type']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.file_name.get()
        row['Enabled'] = ''
        row['Type'] = item.file_type.get()
    
    def _fill_row_style(self, style, item, row):
        style['Name_icon'] = get_icon(item.file_name.get())
        style['Enabled_icon'] = (
            'icons.gui',
            'check' if item.enabled.get() else 'check-box-empty'
        )


# Task UI types
# -------------------------


class TaskColor(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    STRICT_CHOICES = False

    def choices(self):
        mgr = self.root().project().get_task_manager()
        return mgr.template_colors.get() or []
    
    def update_default_value(self):
        choices = self.choices()
        if choices:
            self._value = choices[0]
        self.touch()


class EditTaskColorAction(flow.Action):

    color = flow.SessionParam(None, TaskColor)

    _task_color = flow.Parent()

    def get_buttons(self):
        self.color.update_default_value()
        return ['Save', 'Cancel']
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._task_color.set(self.color.get())


class EditableTaskColor(PropertyValue):

    edit = flow.Child(EditTaskColorAction)


# Default tasks
# -------------------------


class KitsuTaskName(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return sorted(self.root().project().kitsu_api().get_task_types())
    
    def update_default_value(self):
        choices = self.choices()
        if choices:
            self._value = choices[0]
        self.touch()


class AddKitsuTaskNameAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    kitsu_task = flow.SessionParam(None, KitsuTaskName)

    _value = flow.Parent()

    def get_buttons(self):
        self.kitsu_task.update_default_value()
        return ['Add', 'Cancel']
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        task_names = self._value.get() or []
        task_names.append(self.kitsu_task.get().split(' - ')[1])
        self._value.set(task_names)


class ExistingKitsuTaskNames(flow.values.SessionValue):

    DEFAULT_EDITOR = 'multichoice'
    STRICT_CHOICES = False

    _task_names = flow.Parent(2)

    def choices(self):
        return self._task_names.get()


class RemoveKitsuTaskNameAction(flow.Action):

    ICON = ('icons.gui', 'minus-button')

    kitsu_tasks = flow.SessionParam(list, ExistingKitsuTaskNames)

    _value = flow.Parent()

    def get_buttons(self):
        self.kitsu_tasks.revert_to_default()
        return ['Confirm', 'Cancel']
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        result = list(set(self._value.get()).difference(set(self.kitsu_tasks.get())))
        self._value.set(result)


class EditableKitsuTaskNames(PropertyValue):

    add_action = flow.Child(AddKitsuTaskNameAction).ui(label='Add')
    remove_action = flow.Child(RemoveKitsuTaskNameAction).ui(label='Remove')


class KitsuTargetTaskType(flow.values.SessionValue):
  
    _action = flow.Parent()
    _dft_task = flow.Parent(3)

    add_action = flow.Child(AddKitsuTaskNameAction).ui(label='Add')
    remove_action = flow.Child(RemoveKitsuTaskNameAction).ui(label='Remove')

    def update_default_value(self):
        # Reset value with Kitsu task names defined on default task.
        return self.set(self._dft_task.kitsu_tasks.get())
    
    def _fill_ui(self, ui):
        super(KitsuTargetTaskType, self)._fill_ui(ui)

        # Use condition only if hidden param is not defined or set to False
        if ui['hidden'] is False:
            _, ext = os.path.splitext(self._action._dft_file.file_name.get())
            # Hide param if file has no extension or cannot be uploaded to Kitsu
            ui['hidden'] = bool(
                not ext or self.root().project().kitsu_config().is_uploadable(
                    self._action._dft_file.file_name.get()) is False
            )


class EditDefaultTaskFile(flow.Action):
    """
    Allows to edit a default task's file.
    """

    ICON = ('icons.libreflow', 'edit-blank')

    path_format = flow.SessionParam(DEFAULT_PATH_FORMAT, PathFormatValue).ui(
        placeholder='{film}/{shot}/{file}/{revision}'
    )
    file_type   = flow.SessionParam(None, FileTypeValue)
    enabled     = flow.SessionParam().ui(editor='bool')
    optional    = flow.SessionParam().ui(editor='bool')
    is_primary_file = flow.SessionParam().ui(editor='bool')
    use_base_file = flow.SessionParam().ui(editor='bool')
    auto_open = flow.SessionParam().ui(editor='bool')
    with flow.group('Template file settings'):
        template_file          = flow.Connection(related_type=TrackedFile).watched()
        # template_file_revision = flow.SessionParam(TemplateFileRevision)
        template_file_revision = flow.SessionParam('Latest', value_type=TemplateFileRevision)
    with flow.group('Base file settings'):
        from_task = flow.SessionParam()
        base_file_name = flow.SessionParam()
    with flow.group('Kitsu settings'):
        target_kitsu_task_type = flow.SessionParam(None, KitsuTargetTaskType).ui(label='Target Task Type')
    
    action_display_order = flow.SessionParam(dict)
    visible_action_count = flow.SessionParam(0)

    _dft_file   = flow.Parent()
    _map        = flow.Parent(2)
    _dft_task   = flow.Parent(3)

    def get_buttons(self):
        self.message.set(f'<h2>Edit default file {self._dft_file.file_name.get()}</h2>')
        self.file_type.set(self._dft_file.file_type.get())
        self.path_format.set(self._dft_file.path_format.get())
        self.enabled.set(self._dft_file.enabled.get())
        self.optional.set(self._dft_file.optional.get())
        self.is_primary_file.set(self._dft_file.is_primary_file.get())
        self.use_base_file.set(self._dft_file.use_base_file.get())
        self.auto_open.set(self._dft_file.auto_open.get())
        oid = self._dft_file.template_file.get()
        if oid is not None:
            try:
                o = self.root().get_object(oid)
            except:
                pass
            else:
                self.template_file.set_watched(False)
                self.template_file.set(o)
                self.template_file.set_watched(True)
        else:
            self.template_file.set(None)

        self.template_file_revision.set(self._dft_file.template_file_revision.get())
        self.from_task.set(self._dft_file.from_task.get())
        self.base_file_name.set(self._dft_file.base_file_name.get())
        self.target_kitsu_task_type.set(self._dft_file.target_kitsu_task_type.get())
        self.action_display_order.set(self._dft_file.action_display_order.get())
        self.visible_action_count.set(self._dft_file.visible_action_count.get())

        buttons = ['Save']
        mgr = self.root().project().get_task_manager()
        task_template = mgr.task_templates[self._dft_task.template.get()]

        if task_template.files.has_mapped_name(self._dft_file.name()):
            buttons.append('Restore default')
        
        return buttons + ['Cancel']
    
    def child_value_changed(self, child_value):
        if child_value is self.template_file:
            self.template_file_revision.revert_to_default()
    
    def run(self, button):
        if button == 'Cancel':
            return

        if button == 'Restore default':
            self._map.edits.remove(self._dft_file.name())
        else:
            if self._map.edits.has_mapped_name(self._dft_file.name()):
                dft_file = self._map.edits[self._dft_file.name()]
            else:
                mgr = self.root().project().get_task_manager()
                task_template = mgr.task_templates[self._dft_task.template.get()]
                file_name = task_template.files[self._dft_file.name()].file_name.get()
                dft_file = self._map.edits.add(self._dft_file.name())
                dft_file.file_name.set(file_name)
            
            dft_file.file_type.set(self.file_type.get())
            dft_file.path_format.set(self.path_format.get())
            dft_file.enabled.set(self.enabled.get())
            dft_file.optional.set(self.optional.get())
            dft_file.is_primary_file.set(self.is_primary_file.get())
            dft_file.use_base_file.set(self.use_base_file.get())
            dft_file.auto_open.set(self.auto_open.get())
            dft_file.template_file.set(self.template_file.get())
            dft_file.template_file_revision.set(self.template_file_revision.get())
            dft_file.from_task.set(self.from_task.get())
            dft_file.base_file_name.set(self.base_file_name.get())
            dft_file.target_kitsu_task_type.set(self.target_kitsu_task_type.get())
            dft_file.action_display_order.set(self.action_display_order.get())
            dft_file.visible_action_count.set(self.visible_action_count.get())

        self._map.touch()


class RemoveDefaultTaskFile(flow.Action):
    """
    Allows to remove a default task's file.
    """

    ICON = ('icons.gui', 'remove-symbol')

    _dft_file   = flow.Parent()
    _map        = flow.Parent(2)
    _task       = flow.Parent(3)
    _mgr        = flow.Parent(5)

    def allow_context(self, context):
        return context and self._dft_file.is_edit.get()

    def get_buttons(self):
        self.message.set(
            f'Remove <b>{self._dft_file.file_name.get()}</b> '
            f'from task <b>{self._task.name()}</b> files ?'
        )
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        # Remove in task type files dict on kitsu bindings
        task_type_files = self.root().project().kitsu_bindings().task_type_files
        
        existing = [
            t for t in task_type_files.mapped_items()
            if self._dft_file.name() in t.oid_patterns.get()
        ]

        if len(existing) > 0:
            task_type_files.remove(existing[0].name())
            task_type_files.touch()
        
        self._map.edits.remove(self._dft_file.name())
        self._map.touch()
        self._mgr.default_files.touch()


class AddDefaultTaskFileEdit(flow.Action):
    """
    Allows to add a file in the files of a default task.
    """

    file_name   = flow.SessionParam('').ui(label='Name').watched()
    file_type   = flow.SessionParam('Works', FileTypeValue)
    path_format = flow.SessionParam(DEFAULT_PATH_FORMAT, PathFormatValue)
    enabled     = flow.SessionParam(True).ui(editor='bool')
    optional    = flow.SessionParam(False).ui(editor='bool')
    is_primary_file = flow.SessionParam(False).ui(editor='bool')
    use_base_file = flow.SessionParam(False).ui(editor='bool')
    auto_open = flow.SessionParam(False).ui(editor='bool',
        tooltip="Automatically open last revision at double-click")
    with flow.group('Template file settings'):
        template_file          = flow.Connection(related_type=TrackedFile).watched()
        template_file_revision = flow.SessionParam('Latest', value_type=TemplateFileRevision)
    with flow.group('Base file settings'):
        from_task = flow.SessionParam('')
        base_file_name = flow.SessionParam('')
    with flow.group('Kitsu settings'):
        target_kitsu_task_type = flow.SessionParam(None, KitsuTargetTaskType).ui(
            label='Target Task Type',
            hidden=True
        )

    _map = flow.Parent()
    _task = flow.Parent(2)
    _mgr = flow.Parent(4)

    def get_buttons(self):
        self.message.set('<h2>Add default task file</h2>')
        self.path_format.revert_to_default()
        self.file_type.revert_to_default()
        self.template_file.set(None)
        return ['Add', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif not self._filename_is_valid():
            self.message.set((
                f'<font color=#D66700>A default file '
                f'named <b>{self.file_name.get()}</b> already '
                'exists. Please choose another name.</font>'
            ))
            return self.get_result(close=False)
        
        file_name = self.file_name.get()
        df = self._map.edits.add(file_name.replace('.', '_'))
        df.file_name.set(self.file_name.get())
        df.file_type.set(self.file_type.get())
        df.path_format.set(self.path_format.get())
        df.enabled.set(self.enabled.get())
        df.optional.set(self.optional.get())
        df.is_primary_file.set(self.is_primary_file.get())
        df.use_base_file.set(self.use_base_file.get())
        df.auto_open.set(self.auto_open.get())
        df.template_file.set(self.template_file.get())
        df.template_file_revision.set(self.template_file_revision.get())
        df.from_task.set(self.from_task.get())
        df.base_file_name.set(self.base_file_name.get())
        df.target_kitsu_task_type.set(self.target_kitsu_task_type.get())

        self._map.touch()
        self._mgr.default_files.touch()
    
    def child_value_changed(self, child_value):
        if child_value is self.template_file:
            self.template_file_revision.revert_to_default()
        # If file is uploadable to Kitsu, target Kitsu task type is set.
        elif child_value is self.file_name:
            _, ext = os.path.splitext(self.file_name.get())

            if ext and self.root().project().kitsu_config().is_uploadable(self.file_name.get()):
                self.target_kitsu_task_type.update_default_value()
            else:
                self.target_kitsu_task_type.set(None)
    
    def _filename_is_valid(self):
        title = '<h2>Add default task file</h2>'

        if self.file_name.get() == '':
            self.message.set((
                f'{title}<font color=#D66700>'
                'File name must not be empty.</font>'
            ))
            return False
        
        for df in self._map.mapped_items():
            if self.file_name.get() == df.file_name.get():
                self.message.set((
                    f'{title}<font color=#D66700>A default file '
                    f'named <b>{self.file_name.get()}</b> already '
                    'exists. Please choose another name.</font>'
                ))
                return False
        
        return True


class DefaultTaskFile(flow.SessionObject):

    file_name   = flow.Computed().ui(editable=False)
    path_format = flow.Computed().ui(editable=False)
    file_type   = flow.Computed().ui(editable=False)
    enabled     = flow.Computed().ui(editable=False, editor='bool')
    optional    = flow.Computed().ui(editable=False, editor='bool')
    is_primary_file = flow.Computed().ui(editable=False, editor='bool')
    use_base_file = flow.Computed().ui(editable=False, editor='bool')
    auto_open = flow.Computed().ui(editable=False, editor='bool')
    with flow.group('Template file settings'):
        template_file          = flow.Computed().ui(editable=False)
        template_file_revision = flow.Computed().ui(editable=False)
    with flow.group('Base file settings'):
        from_task = flow.Computed().ui(editable=False)
        base_file_name = flow.Computed().ui(editable=False)
    with flow.group('Kitsu settings'):
        target_kitsu_task_type = flow.Computed().ui(editable=False, label='Target Task Type')

    action_display_order = flow.Computed().ui(editable=False)
    visible_action_count = flow.Computed().ui(editable=False)
    is_edit     = flow.Computed().ui(editable=False, editor='bool')

    edit        = flow.Child(EditDefaultTaskFile)
    remove      = flow.Child(RemoveDefaultTaskFile)

    _map = flow.Parent()
    
    def compute_child_value(self, child_value):
        # If value is empty, we check if there is one in the task type files dict on kitsu bindings.
        if child_value is self.target_kitsu_task_type:
            cache_child_value = self._map.get_child_value(self.name(), child_value.name())
            
            task_type_files = self.root().project().kitsu_bindings().task_type_files
            
            existing = [
                t for t in task_type_files.mapped_items()
                if self.name() in t.oid_patterns.get()
            ]

            if (cache_child_value is None or cache_child_value in ['', []]) and len(existing) > 0:
                self._map.edits[self.name()].target_kitsu_task_type.set(existing[0].task_patterns.get())
                return child_value.set(existing[0].task_patterns.get())

        child_value.set(self._map.get_child_value(self.name(), child_value.name()))


class DefaultTaskFiles(flow.DynamicMap):

    edits = flow.Child(DefaultFiles).ui(hidden=True)

    add_dft_file = flow.Child(AddDefaultTaskFileEdit).ui(label='Add default file', dialog_size=(825, 545))

    _default_task = flow.Parent()

    def __init__(self, parent, name):
        super(DefaultTaskFiles, self).__init__(parent, name)
        self._cache = None

    def mapped_names(self, page_num=0, page_size=None):
        if self._cache is None:
            mgr = self.root().project().get_task_manager()
            task_template = mgr.task_templates[self._default_task.template.get()]
            default_names = task_template.files.mapped_names()
            edit_names = set(self.edits.mapped_names())

            self._cache = {}

            # Collect default files (potentially edited)
            for name in default_names:
                data = {}
                if name in edit_names:
                    default_file = self.edits[name]
                    # Path format evaluation order: edit > default task > template file > template
                    path_format = (
                        default_file.path_format.get()
                        or self._default_task.path_format.get()
                        or task_template.files[name].path_format.get()
                        or task_template.path_format.get()
                    )
                    action_display_order = (
                        default_file.action_display_order.get()
                        or task_template.files[name].action_display_order.get()
                    )
                    visible_action_count = (
                        default_file.visible_action_count.get()
                        or task_template.files[name].visible_action_count.get()
                    )
                    data['is_edit'] = True
                    edit_names.remove(name)
                else:
                    default_file = task_template.files[name]
                    path_format = default_file.path_format.get() or task_template.path_format.get()
                    action_display_order = default_file.action_display_order.get()
                    visible_action_count = default_file.visible_action_count.get()
                    data['is_edit'] = False
                
                template_file = default_file.template_file.get()
                data.update(dict(
                    file_name=default_file.file_name.get(),
                    file_type=default_file.file_type.get(),
                    path_format=path_format,
                    enabled=default_file.enabled.get(),
                    optional=default_file.optional.get(),
                    is_primary_file=default_file.is_primary_file.get(),
                    auto_open=bool(default_file.auto_open.get()),
                    use_base_file=default_file.use_base_file.get(),
                    template_file=template_file.oid() if template_file else None,
                    template_file_revision=default_file.template_file_revision.get(),
                    from_task=default_file.from_task.get(),
                    base_file_name=default_file.base_file_name.get(),
                    target_kitsu_task_type=default_file.target_kitsu_task_type.get(),
                    action_display_order=action_display_order,
                    visible_action_count=visible_action_count
                ))
                self._cache[name] = data
            
            # Collect remaining edits
            for name in edit_names:
                default_file = self.edits[name]
                # Path format evaluation order: edit > default task > template
                path_format = (
                    default_file.path_format.get()
                    or self._default_task.path_format.get()
                    or task_template.path_format.get()
                )
                template_file = default_file.template_file.get()
                data = dict(
                    file_name=default_file.file_name.get(),
                    file_type=default_file.file_type.get(),
                    path_format=path_format,
                    enabled=default_file.enabled.get(),
                    optional=default_file.optional.get(),
                    is_primary_file=default_file.is_primary_file.get(),
                    auto_open=bool(default_file.auto_open.get()),
                    use_base_file=default_file.use_base_file.get(),
                    template_file=template_file.oid() if template_file else None,
                    template_file_revision=default_file.template_file_revision.get(),
                    from_task=default_file.from_task.get(),
                    base_file_name=default_file.base_file_name.get(),
                    target_kitsu_task_type=default_file.target_kitsu_task_type.get(),
                    action_display_order=default_file.action_display_order.get(),
                    visible_action_count=default_file.visible_action_count.get(),
                    is_edit=True
                )
                self._cache[name] = data
        
        return self._cache.keys()
    
    @classmethod
    def mapped_type(cls):
        return DefaultTaskFile
    
    def get_child_value(self, mapped_name, value_name):
        self.mapped_names()
        return self._cache[mapped_name][value_name]
    
    def columns(self):
        return ['Enabled', 'Name', 'Type']
    
    def touch(self):
        self._cache = None
        self._mng.children.clear()
        super(DefaultTaskFiles, self).touch()
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.file_name.get()
        row['Enabled'] = ''
        row['Type'] = item.file_type.get()
    
    def _fill_row_style(self, style, item, row):
        style['Name_icon'] = get_icon(item.file_name.get())
        style['Enabled_icon'] = (
            'icons.gui',
            'check' if item.enabled.get() else 'check-box-empty'
        )
        style['activate_oid'] = item.edit.oid()


class TaskTemplateName(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        mgr = self.root().project().get_task_manager()
        return mgr.task_templates.mapped_names()
    
    def update_default_value(self):
        choices = self.choices()
        if choices:
            self._value = choices[0]
        self.touch()


class EditTaskTemplateNameAction(flow.Action):

    template = flow.SessionParam(None, TaskTemplateName)

    _task_template = flow.Parent()

    def get_buttons(self):
        self.template.update_default_value()
        return ['Save', 'Cancel']
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._task_template.set(self.template.get())


class EditableTaskTemplateName(PropertyValue):

    edit = flow.Child(EditTaskTemplateNameAction)


class CreateDefaultTaskAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    task_name    = flow.SessionParam('')
    display_name = flow.SessionParam('')
    code         = flow.SessionParam('')
    prefix       = flow.SessionParam('')
    icon         = flow.SessionParam(('icons.gui', 'cog-wheel-silhouette'))
    template     = flow.SessionParam(None, TaskTemplateName)
    position     = flow.SessionParam(0).ui(editor='int')
    path_format  = flow.SessionParam('')
    entity_filter = flow.SessionParam('')
    enabled      = flow.SessionParam(True).ui(
        editor='bool',
        tooltip='Dictates if the task must appear in the UI by default')
    optional     = flow.SessionParam(False).ui(
        editor='bool',
        tooltip='Dictates if the task must be created automatically')

    _map      = flow.Parent()
    _mgr      = flow.Parent(2)

    def get_buttons(self):
        self.template.update_default_value()

        if len(self.template.choices()) == 0:
            self.message.set((
                '<h2>Add default task</h2>'
                '<font color=#D5000D>Please add a template '
                'before creating a default task.</font>'
            ))
            return ['Cancel']
        
        self.message.set('<h2>Add default task</h2>')
        return ['Add', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return
        
        dt = self._map.add_default_task(
            self.task_name.get(),
            self.display_name.get(),
            self.template.get(),
            self.position.get(),
            self.code.get(),
            self.prefix.get(),
            self.path_format.get() or None,
            self.entity_filter.get() or None,
            self.enabled.get(),
            self.optional.get()
        )
        icon = tuple(self.icon.get() or ('icons.gui', 'cog-wheel-silhouette'))
        dt.icon.set(icon)

        self._map.touch()
        self._mgr.default_files.touch()


class KitsuTasksMultiChoiceValue(flow.values.SessionValue):

    DEFAULT_EDITOR = 'multichoice'

    _action = flow.Parent()

    def choices(self):       
        return self._action.tasksData.get()


class CreateKitsuTasksPage1(flow.Action):

    ICON = ('icons.libreflow', 'kitsu')

    tasksData = flow.Computed(cached=True, store_value=False).ui(hidden=True)
    tasksChoice = flow.Param([], KitsuTasksMultiChoiceValue).ui(label='Tasks')

    _map = flow.Parent()
    _mgr = flow.Parent(2)

    def get_buttons(self):
        self.tasksData.touch()
        self.message.set('<h2>Select tasks to create</h2>')
        return ['Select', 'Cancel']

    def compute_child_value(self, child_value):
        if child_value is self.tasksData:
            task_types = sorted(self.root().project().kitsu_api().get_task_types())
            task_types = [t for t in task_types
            if t.split(' - ')[1] != "FDT"
            if t.split(' - ')[0].lower() in (name.lower() for name in self._mgr.task_templates.mapped_names()) # Case insensitive
            if self._mgr.default_tasks.has_mapped_name(t.split(' - ')[1]) == False]

            for t in task_types:
                task_type, task_name = t.split(' - ')
                for dft_task in self._mgr.default_tasks.mapped_items():
                    if task_name in dft_task.kitsu_tasks.get():
                        task_types.remove(t)
                        break
            
            self.tasksData.set(task_types)
   
    def run(self, button):
        if button == 'Cancel':
            return
        
        return self.get_result(next_action=self._map.add_kitsu_tasks_page2.oid())


class KitsuTaskData(flow.Object):

    task_type = flow.Param().ui(editable=False)
    task_name = flow.Param()


class KitsuTasksChoices(flow.DynamicMap):

    _map = flow.Parent(2)
    _mgr = flow.Parent(3)

    def __init__(self, parent, name):
        super(KitsuTasksChoices, self).__init__(parent, name)
        self.tasks = None

    @classmethod
    def mapped_type(cls):
        return KitsuTaskData
    
    def mapped_names(self, page_num=0, page_size=None):
        choices = self._map.add_kitsu_tasks.tasksChoice.get()

        self.tasks = {}
        for i, task in enumerate(choices):
            data = {}
            data.update(dict(
                task_type=next(
                    # Case insensitive
                    name for name in self._mgr.task_templates.mapped_names()
                    if name.lower() == task.split(' - ')[0].lower()
                ),
                task_name=task.split(' - ')[1]
            ))
            self.tasks['task'+str(i)] = data
        
        return self.tasks.keys()

    def columns(self):
        return ['Type', 'Name']

    def _configure_child(self, child):
        child.task_type.set(self.tasks[child.name()]['task_type'])
        child.task_name.set(self.tasks[child.name()]['task_name'])

    def _fill_row_cells(self, row, item):
        row['Type'] = item.task_type.get()
        row['Name'] = item.task_name.get()


class CreateKitsuTasksPage2(flow.Action):

    tasks = flow.Child(KitsuTasksChoices).ui(expanded=True)

    _map = flow.Parent()
    _mgr = flow.Parent(2)

    def allow_context(self, context):
        return context and context.endswith('.details')

    def get_buttons(self):
        self.message.set('<h2>Rename tasks if needed</h2>')
        return ['Create tasks', 'Back']

    def run(self, button):
        if button == 'Back':
            return self.get_result(next_action=self._map.add_kitsu_tasks.oid())
        
        for item in self.tasks.mapped_items():
            if not self._mgr.default_tasks.has_mapped_name(item.task_name.get()):
                self.root().session().log_info(f'[Create Kitsu Tasks] Creating Default Task {item.task_name.get()}')
                
                t = self._mgr.default_tasks.add_default_task(
                    item.task_name.get(),
                    item.task_name.get(),
                    item.task_type.get(),
                    0
                )

                kitsu_task_names = t.kitsu_tasks.get() or []
                kitsu_task_names.append(item.task_name.get())
                t.kitsu_tasks.set(kitsu_task_names)
            else:
                continue
        
        self._mgr.default_tasks.touch()


class DefaultTask(Entity):
    """
    Defines a set of presets used to create a task in the project.

    These presets include UI elements (display name and position),
    dictate if the associated tasks are enabled in the project and
    optional at creation time.
    In addition, each default task has a task template, and holds
    a set of parameters and a list of default files used to
    override the template's defaults.
    """

    display_name = Property()
    code         = Property()
    prefix       = Property()
    position     = Property()
    enabled      = Property().ui(editor='bool')
    optional     = Property().ui(editor='bool')
    entity_filter = Property().ui(tooltip='Regular expression used to filter entities in which this default task can be created.')
    icon         = Property()
    color        = Property(EditableTaskColor)
    template     = Property(EditableTaskTemplateName).ui(editable=False).watched()
    files        = flow.Child(DefaultTaskFiles).ui(expanded=True)
    path_format  = Property()
    kitsu_tasks   = Property(EditableKitsuTaskNames).ui(editable=False)
    priority_actions  = Property()

    subtasks     = flow.OrderedStringSetParam()

    assignation_enabled = flow.BoolParam(True)

    def get_display_name(self):
        return self.display_name.get()
    
    def get_position(self):
        return self.position.get() or 0
    
    def get_code(self):
        code = self.code.get()
        if not code:
            code = self.get_template().code.get()
        
        return code
    
    def get_prefix(self):
        prefix = self.prefix.get()
        if not prefix:
            prefix = self.get_template().prefix.get()
        
        return prefix

    def get_icon(self):
        icon = self.icon.get()
        if not icon:
            icon = self.get_template().icon.get()
        
        return tuple(icon)
    
    def get_color(self):
        color = self.color.get()
        if not color:
            color = self.get_template().color.get()
        
        return color
    
    def get_primary_file_names(self):
        names = [
            f.file_name.get()
            for f in self.files.mapped_items()
            if f.is_primary_file.get()
        ]
        if not names:
            names = self.get_template().primary_files.get()
        
        return names or None
    
    def get_path_format(self):
        '''
        Returns the path format of this default task if defined,
        or the path format of its template otherwise.
        '''
        path_format = self.path_format.get()
        
        if not path_format:
            path_format = self.get_template().path_format.get()
        
        return path_format
    
    def get_template(self):
        return self.root().project().get_task_manager().task_templates[
            self.template.get()
        ]
    
    def child_value_changed(self, child_value):
        if child_value is self.template:
            self.root().project().get_task_manager().default_files.touch()


class DefaultTasks(CustomEntityCollection):

    add_dft_task = flow.Child(CreateDefaultTaskAction).ui(
        label='Add default task'
    )
    add_kitsu_tasks = flow.Child(CreateKitsuTasksPage1).ui(dialog_size=(500, 560))
    add_kitsu_tasks_page2 = flow.Child(CreateKitsuTasksPage2).ui(hidden=True)

    @classmethod
    def mapped_type(cls):
        return DefaultTask

    def mapped_names(self, page_num=0, page_size=None):
        '''
        Returns task names sorted by task positions.
        '''
        names = super(DefaultTasks, self).mapped_names(page_num, page_size)
        return sorted(names, key=self.get_task_position)

    def get_task_position(self, task_name):
        '''
        Returns the position of the task `task_name` in this
        collection. If not defined (i.e. not `None` neither `""`),
        returns `0`.
        '''
        super(DefaultTasks, self).mapped_names() # ensure cache exists
        pos = self._document_cache[task_name].get('position')
        if pos is None or pos == "":
            pos = 0
        return pos

    def add_default_task(self, name, display_name, template_name, position=-1, code=None, prefix=None, path_format=None, entity_filter=None, enabled=True, optional=False, icon=None):
        if position < 0:
            position = len(self)
        
        dt = self.add(name)
        dt.display_name.set(display_name)
        dt.code.set(code)
        dt.prefix.set(prefix)
        dt.position.set(position)
        dt.template.set(template_name)
        dt.path_format.set(path_format)
        dt.entity_filter.set(entity_filter)
        dt.enabled.set(enabled)
        dt.optional.set(optional)
        if icon:
            dt.icon.set(icon)
        
        self.touch()
        return dt
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.display_name.get()
    
    def _fill_row_style(self, style, item, row):
        style['icon'] = item.get_icon()
        style['background-color'] = item.get_color()


# Task templates
# -------------------------


class CreateTaskTemplateAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    template_name = flow.SessionParam('').ui(label='Name')
    color         = flow.SessionParam(None, TaskColor)
    icon          = flow.SessionParam(('icons.gui', 'cog-wheel-silhouette'))
    path_format   = flow.SessionParam('')

    _map = flow.Parent()

    def get_buttons(self):
        self.color.update_default_value()
        self.message.set('<h2>Add task template</h2>')
        return ['Add', 'Cancel']

    def run(self, button):
        if button == 'Cancel':
            return
        
        tt = self._map.add_task_template(
            self.template_name.get(),
            self.color.get(),
            self.path_format.get() or None
        )
        icon = tuple(self.icon.get() or ('icons.gui', 'cog-wheel-silhouette'))
        tt.icon.set(icon)
        self._map.touch()


class TaskTemplate(Entity):
    """
    A task template defines a generic task configuration,
    which can be overriden by default tasks.
    """
    
    code  = Property()
    prefix = Property()
    color = Property(EditableTaskColor)
    icon  = Property()
    files = flow.Child(DefaultFiles).ui(expanded=True)
    path_format = Property()
    primary_files = flow.Computed(None).ui(editable=False)

    def get_path_format(self):
        '''
        Returns the path format of this task template.
        '''
        return self.path_format.get()

    def compute_child_value(self, child_value):
        if child_value is self.primary_files:
            files = []
            for dft_file in self.files.mapped_items():
                if dft_file.enabled.get() and dft_file.is_primary_file.get():
                    files.append(dft_file.file_name.get())
            
            self.primary_files.set(files)


class TaskTemplates(CustomEntityCollection):

    add_template = flow.Child(CreateTaskTemplateAction)

    @classmethod
    def mapped_type(cls):
        return TaskTemplate

    def add_task_template(self, template_name, color, path_format=None):
        template = self.add(template_name)
        template.color.set(color)
        template.path_format.set(path_format)
        
        self.touch()
        return template
    
    def _fill_row_style(self, style, item, row):
        style['icon'] = tuple(item.icon.get())
        style['background-color'] = item.color.get()


# Task creation
# -------------------------


class SelectDefaultFileAction(flow.Action):

    _default_file = flow.Parent()
    _map          = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        if self._default_file.exists.get():
            return
        
        self._default_file.create.set(
            not self._default_file.create.get()
        )
        self._map.touch()


class DefaultTaskViewItem(flow.SessionObject):
    """
    Describes a default task to be created in the list of
    files of a task.
    """
    task_name    = flow.Param()
    display_name = flow.Param()
    create       = flow.BoolParam()
    exists       = flow.Computed(cached=True)
    icon         = flow.Param()

    select       = flow.Child(SelectDefaultFileAction)

    _tasks       = flow.Parent(3)

    def compute_child_value(self, child_value):
        if child_value is self.exists:
            exists = self._tasks.has_mapped_name(self.task_name.get())
            self.exists.set(exists)


class DefaultTaskView(flow.DynamicMap):
    '''
    Lists the default tasks defined in the task manager that
    can be added to a task collection.
    
    Tasks defined as not optional in the manager's default
    tasks are preselected; tasks which already exist in the
    collection appear greyed out.
    '''

    _action = flow.Parent()
    _tasks = flow.Parent(2)

    def __init__(self, parent, name):
        super(DefaultTaskView, self).__init__(parent, name)
        self._cache = None
        self._cache_names = None
        self._cache_key = None

    @classmethod
    def mapped_type(cls):
        return DefaultTaskViewItem

    def mapped_names(self, page_num=0, page_size=None):
        cache_key = (page_num, page_size)
        if (
            self._cache is None
            or self._cache_key != cache_key
        ):
            mgr = self.root().project().get_task_manager()
            default_tasks = self._tasks.get_default_tasks()

            self._cache = {}
            self._cache_names = []
            positions = {}

            for dt in default_tasks:
                task_name = dt.name()
                self._cache[task_name] = dict(
                    task_name=task_name,
                    display_name=mgr.get_task_display_name(task_name),
                    create=not dt.optional.get(),
                    icon=mgr.get_task_icon(task_name),
                )
                self._cache_names.append(task_name)
                positions[task_name] = dt.position.get()
            
            self._cache_names.sort(key=lambda n: positions[n])
            self._cache_key = cache_key
        
        return self._cache_names
    
    def columns(self):
        return ['Do create', 'Task']

    def refresh(self):
        self._cache = None
        for t in self.mapped_items():
            t.exists.touch()
        self.touch()
    
    def _configure_child(self, child):
        self.mapped_names()
        child.task_name.set(self._cache[child.name()]['task_name'])
        child.display_name.set(self._cache[child.name()]['display_name'])
        child.create.set(self._cache[child.name()]['create'])
        child.icon.set(self._cache[child.name()]['icon'])
    
    def _fill_row_cells(self, row, item):
        row['Do create'] = ''
        row['Task'] = item.display_name.get()
    
    def _fill_row_style(self, style, item, row):
        style['Do create_activate_oid'] = item.select.oid()

        if item.exists.get():
            style['Task_icon'] = item.icon.get()
            style['Do create_icon'] = ('icons.gui', 'check-box-empty-dark')
            for col in self.columns():
                style['%s_foreground-color' % col] = '#4e5255'
        else:
            style['Task_icon'] = item.icon.get()
            if item.create.get():
                style['Do create_icon'] = ('icons.gui', 'check')
            else:
                style['Do create_icon'] = ('icons.gui', 'check-box-empty')


class ManageTasksAction(flow.Action):
    """
    Allows to create tasks among the default tasks defined
    in the project's task manager.
    """

    tasks = flow.Child(DefaultTaskView)

    _map = flow.Parent()

    def get_buttons(self):
        self.tasks.refresh()
        if self.all_tasks_exist():
            return ['Close']
        
        return ['Create', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel' or button == 'Close':
            return
        
        mgr = self.root().project().get_task_manager()
        
        for dt in self.tasks.mapped_items():
            if dt.create.get() and not dt.exists.get():
                t = self._map.add(dt.name())
                t.display_name.set(dt.display_name.get())
        
        self._map.touch()
    
    def child_value_changed(self, child_value):
        if child_value is self.select_all:
            b = self.select_all.get()

            for dt in self.tasks.mapped_items():
                if not dt.exists.get():
                    dt.create.set(b)
            
            self.tasks.touch()
    
    def all_tasks_exist(self):
        return all([
            t.exists.get()
            for t in self.tasks.mapped_items()
        ])


# Task manager
# -------------------------


class TaskDefaultConfig(flow.Object):

    code = flow.Param('')
    prefix = flow.Param('')
    color = flow.Param()
    icon = flow.Param(('icons.gui', 'cog-wheel-silhouette'))
    position = flow.IntParam(0)
    path_format = flow.Param()
    primary_files = flow.Param(list)


class TaskManager(flow.Object):
    """
    The task manager embeds an ordered list of default task
    names and a list of task templates
    """

    default_config = flow.Child(TaskDefaultConfig).ui(
        tooltip='Task configuration used when a task has no corresponding default task')
    default_files = flow.Computed(cached=True).ui(hidden=True)
    enabled_only = flow.BoolParam(False).ui(hidden=True).watched()
    default_tasks  = flow.Child(DefaultTasks).ui(expanded=True)
    task_templates = flow.Child(TaskTemplates).ui(expanded=True)
    template_colors = flow.OrderedStringSetParam().ui(hidden=True)

    def get_task_color(self, task_name):
        if not self.has_default_task(task_name):
            return self.default_config.color.get()
        
        return self.default_tasks[task_name].get_color()
    
    def get_task_icon(self, task_name):
        if not self.has_default_task(task_name):
            return tuple(self.default_config.icon.get())
        
        return self.default_tasks[task_name].get_icon()
    
    def get_task_display_name(self, task_name):
        if not self.has_default_task(task_name):
            return task_name
        
        return self.default_tasks[task_name].get_display_name()
    
    def get_task_code(self, task_name):
        if not self.has_default_task(task_name):
            return self.default_config.code.get()
        
        return self.default_tasks[task_name].get_code()
    
    def get_task_prefix(self, task_name):
        if not self.has_default_task(task_name):
            return self.default_config.prefix.get()
        
        return self.default_tasks[task_name].get_prefix()
    
    def get_task_position(self, task_name):
        if not self.has_default_task(task_name):
            return self.default_config.position.get()
        
        return self.default_tasks[task_name].get_position()

    def get_task_path_format(self, task_name):
        '''
        If a default task exists with the given name, returns
        its path format. Otherwise, returns the task manager's
        default path format.
        '''
        if not self.has_default_task(task_name):
            return self.default_config.path_format.get()
        
        return self.default_tasks[task_name].get_path_format()
    
    def get_task_primary_file_names(self, task_name):
        if not self.has_default_task(task_name):
            return self.default_config.primary_files.get()
        
        return self.default_tasks[task_name].get_primary_file_names()
    
    def get_template_default_tasks(self, template_name):
        return [
            dt for dt in self.default_tasks.mapped_items()
            if re.fullmatch(template_name, dt.template.get(), re.IGNORECASE)
        ]
    
    def get_default_tasks(self, template_name=None, exclude_optional=False, entity_oid=None):
        '''
        Returns a list of default tasks.

        If `template_name` is provided, this method returns only default
        tasks of the corresponding template. The template search is
        case-insensitive, i.e. providing either `default` or `DEFAULT`
        will produce the same result.
        The `exclude_optional` parameter indicates if only default
        tasks whose `optional` property is false must be returned.
        If `entity_oid` is provided, only default tasks for which this
        oid matches the `entity_filter` will be returned.

        If neither of the parameters is used, the method returns all
        default tasks defined in the task manager.
        '''
        default_tasks = self.default_tasks.mapped_items()
        
        if template_name is not None:
            default_tasks = [
                dt for dt in default_tasks
                if re.fullmatch(template_name, dt.template.get(), re.IGNORECASE)
            ]
        if exclude_optional:
            default_tasks = [
                dt for dt in default_tasks
                if not dt.optional.get()
            ]
        if entity_oid:
            default_tasks = [
                dt for dt in default_tasks
                if (not dt.entity_filter.get()
                    or re.fullmatch(dt.entity_filter.get(), entity_oid) is not None)
            ]
        
        return default_tasks
    
    def get_file_priority_actions(self, task_name, file_oid):
        '''
        Returns a tuple containing the two lists of primary and
        secondary actions (as returned by the `get_object_actions()`
        command) of the file with the given oid and belonging to the
        task `task_name`.
        '''
        if not self.has_default_task(task_name):
            return ([], [])
        
        _file = self.root().get_object(file_oid)

        display_order = _file.action_display_order.get() or None
        visible_count = _file.visible_action_count.get() or None
        
        if display_order is None or visible_count is None:
            presets = self.default_tasks[task_name].files
            file_mapped_name = file_oid.split('/')[-1]

            if presets.has_mapped_name(file_mapped_name):
                preset = presets[file_mapped_name]
                display_order = preset.action_display_order.get() or {}
                visible_count = preset.visible_action_count.get() or 0
            
            display_order = display_order or {}
            visible_count = visible_count or 0

        actions = sorted(
            self.root().session().cmds.Flow.get_object_actions(file_oid),
            key=lambda a: display_order.get(a[2][0], sys.maxsize)
        )
        
        return (actions[:visible_count], actions[visible_count:])
    
    def get_subtasks(self, task_name):
        if not self.has_default_task(task_name):
            return []
        
        return self.default_tasks[task_name].subtasks.get()
    
    def is_assignation_enabled(self, task_name):
        if not self.has_default_task(task_name):
            return False
        
        return self.default_tasks[task_name].assignation_enabled.get()

    def get_task_files(self, task_name, enabled_only=False):
        """
        Returns a dict describing the default files
        of a task with the given name.
        
        Each pair of the returned dict has the following layout:
            <mapped_name>: (<display_name>, <path_format>, <optional>)
        """
        files = {}
        if self.default_tasks.has_mapped_name(task_name):
            dt = self.default_tasks[task_name]
            for df in dt.files.mapped_items():
                template_file = None
                if not enabled_only or df.enabled.get():
                    oid = df.template_file.get()
                    if oid is not None:
                        try:
                            template_file = self.root().get_object(oid)
                        except:
                            pass

                    files[df.name()] = (
                            df.file_name.get(),
                            df.path_format.get(),
                            df.file_type.get(),
                            df.optional.get(),
                            df.is_primary_file.get(),
                            df.use_base_file.get(),
                            template_file,
                            df.template_file_revision.get(),
                            df.from_task.get(),
                            df.base_file_name.get(),
                            df.target_kitsu_task_type.get(),
                            df.auto_open.get(),
                        )
        
        return files
    
    def has_default_task(self, task_name):
        return self.default_tasks.has_mapped_name(task_name)
    
    def child_value_changed(self, child_value):
        if child_value is self.enabled_only:
            self.default_files.touch()
    
    def compute_child_value(self, child_value):
        if child_value is self.default_files:
            default_files = defaultdict(list)
            enabled_only = self.enabled_only.get()
            
            for t in self.default_tasks.mapped_items():
                t.files.touch() # Needed to get up-to-date file presets
                for f in t.files.mapped_items():
                    if not enabled_only or f.enabled.get():
                        default_files[f.file_name.get()].append(t.name())
            
            self.default_files.set(dict(default_files))
