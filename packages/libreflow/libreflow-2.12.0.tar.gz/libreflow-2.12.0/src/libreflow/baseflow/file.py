import os
import sys
import getpass
import time
import datetime
import shutil
import glob
import string
import re
import hashlib
import timeago
import zipfile
import fnmatch
import subprocess
import pathlib
import mimetypes
import traceback
import psutil
import copy
import json
import pprint

import kabaret.app.resources as resources
from kabaret import flow
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.flow_entities.entities import Entity, EntityCollection, Property
from kabaret.subprocess_manager.flow import RunAction

from ..resources.mark_sequence import fields
from ..resources.icons import gui
from ..resources.scripts import blender as _
from ..utils.b3d import wrap_python_expr
from ..utils.kabaret.jobs import jobs_flow
from ..utils.kabaret.flow_entities.entities import CustomEntity, EntityView, GlobalEntityCollection
from ..utils.os import zip_folder, remove_folder_content, hash_folder
from ..utils.flow import keywords_from_format, EntityRef, EntityRefMap

from .maputils import SimpleCreateAction, ClearMapAction
from .site import SyncMap, Request, RequestAs, UploadRevision, DownloadRevision, SiteJobsPoolNames, ActiveSiteChoiceValue
from .runners import LaunchSessionWorker, FILE_EXTENSIONS, FILE_EXTENSION_ICONS
from .kitsu import KitsuTaskStatus
from .dependency import DependencyView

pyversion = sys.version_info


def list_digits(s, _nsre=re.compile('([0-9]+)')):
    '''
    List all digits contained in a string
    '''
    return [int(text) for text in _nsre.split(s) if text.isdigit()]


class FileType(flow.values.ChoiceValue):

    CHOICES = ['INPUT', 'OUTPUT', 'WORK']


class CreateWorkingCopyBaseAction(flow.Action):

    _file = flow.Parent()

    def allow_context(self, context):
        return context and self._file.editable()


class RevisionsChoiceValue(flow.values.ChoiceValue):

    STRICT_CHOICES = False

    _file = flow.Parent(2)

    def choices(self):
        return self._file.get_revision_names(sync_status='Available', published_only=True)

    def revert_to_default(self):
        if self._file.is_empty():
            self.set('')
            return

        revision = self._file.get_head_revision(sync_status='Available')
        revision_name = ''
        
        if revision is None:
            choices = self.choices()
            if choices:
                revision_name = choices[0]
        else:
            revision_name = revision.name()
        
        self.set(revision_name)
    
    def _fill_ui(self, ui):
        super(RevisionsChoiceValue, self)._fill_ui(ui)
        ui['hidden'] = self._file.is_empty(on_current_site=True)
        if hasattr(self._file.open, "is_running") :
            ui['hidden'] = self._file.open.is_running()


class RevisionsWorkingCopiesChoiceValue(RevisionsChoiceValue):

    def choices(self):
        user = self.root().project().get_user()
        if user.preferences.create_working_copies.get() == True:
            revisions = self._file.get_revision_names(sync_status='Available')
            for revision in revisions:
                if revision == self.root().project().get_user_name():
                    revisions.remove(revision)
            return revisions
        else:
            return super(RevisionsWorkingCopiesChoiceValue, self).choices()


class CreateWorkingCopyFromRevision(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    _revision = flow.Parent()
    _file = flow.Parent(4)

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#FFA34D>WARNING: You already have "
                "a working copy to your name. Choosing to create "
                "a new one will overwrite your changes.</font>"
            )
        self.message.set(msg)

        return ["Create", "Cancel"]

    def needs_dialog(self):
        return self._file.has_working_copy(from_current_user=True)

    def allow_context(self, context):
        user = self.root().project().get_user()
        create_working_copies = user.preferences.create_working_copies.get()
        
        return (
            context
            and self._file.editable()
            and not self._revision.is_working_copy(from_current_user=create_working_copies)
            and self._revision.get_sync_status() == 'Available'
        )

    def run(self, button):
        if button == "Cancel":
            return

        working_copy = self._file.create_working_copy(from_revision=self._revision.name())
        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


class MakeCurrentRevisionAction(flow.Action):

    _revision = flow.Parent()

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False

    def run(self, button):
        file = self._revision._file
        file.make_current(self._revision)
        file.get_revisions().touch()
        file.touch()


class GenericRunAction(RunAction):

    _file = flow.Parent()
    _buttons = flow.SessionParam()

    def get_default_app(self, extension):
        extension = self.target_file_extension()
        default_applications = self.root().project().admin.default_applications
        app = None
        if default_applications.has_mapped_name(extension):
            app = default_applications[extension]
        
        return app

    def runner_name_and_tags(self):
        runner_name = None
        app = self.get_default_app(self.target_file_extension())

        if app is not None:
            runner_name = app.runner_name.get()
        
        return runner_name, []
    
    def _check_env_priority(self, var_name):
        sys_env = os.environ
        usr_env = self.root().project().admin.user_environment
        name_site = self.root().project().admin.multisites.current_site_name.get()
        site_env = self.root().project().admin.multisites.working_sites[name_site].site_environment

        if (var_name in sys_env) and (len(sys_env[var_name]) > 0):
            # Highest priority: Already defined, we don't do anything
            pass

        elif (usr_env.has_mapped_name(var_name)) and (len(usr_env[var_name].get()) > 0):
            # Mid priority: We fill the environment
            sys_env[var_name] = usr_env[var_name].get()

        elif (site_env.has_mapped_name(var_name)) and (len(site_env[var_name].value.get()) > 0):
            # Lowest priority
            sys_env[var_name] = site_env[var_name].value.get()
        else:
            return False
        
        return True


    def check_runner_env_priority(self, runner_name, runner_version=None):
        session = self.root().session()

        if runner_version is not None:
            target_var = '%s_%s_EXEC_PATH' % (
                runner_name.upper(),
                runner_version.upper().replace('.', '_')
            )
        
            var_defined = self._check_env_priority(target_var)
        
            if var_defined:
                session.log_debug('%s defined: %s' % (target_var, os.environ[target_var]))
                return var_defined
            
            session.log_debug('%s undefined' % target_var)
        
        target_var = '%s_EXEC_PATH' % runner_name.upper()
        var_defined = self._check_env_priority(target_var)

        if var_defined:
            session.log_debug('%s defined: %s' % (target_var, os.environ[target_var]))
        else:
            session.log_warning('No executable path defined for %s %s in environment' % (runner_name, runner_version))
        
        return var_defined
    
    def target_file_extension(self):
        return self._file.format.get()

    def extra_env(self):
        env = {}
        env["USER_NAME"] = self.root().project().get_user_name()
        root_path = self.root().project().get_root()
        
        if root_path:
            env["ROOT_PATH"] = root_path

        return env
    
    def extra_handlers(self):
        # Return extras and overrides handlers from project settings map
        runner_handlers = self.root().project().admin.runner_handlers.mapped_items()
        runner_name, _ = self.runner_name_and_tags()

        handlers = []
        for handler in runner_handlers:
            # Append handler if for current runner and not a base handler
            if handler.runner.get() == runner_name and handler.status.get() != 'default':
                handlers.append(dict(
                    handler_type=handler.handler_type.get(),
                    description=handler.description.get(),
                    pattern=handler.pattern.get(),
                    whence=handler.whence.get(),
                    enabled=handler.enabled.get()
                ))

        return handlers

    def get_version(self, button):
        session = self.root().session()

        default_applications = self.root().project().admin.default_applications
        app = default_applications[self.target_file_extension()]
        runner_name = app.runner_name.get()

        env = get_contextual_dict(self, 'environment')
        version_var_name = '%s_VERSION' % app.runner_name.get().upper()

        if env and version_var_name in env:
            runner_version = str(env[version_var_name])
            session.log_debug('%s selected version: %s (contextual override)' % (runner_name, runner_version))
        else:
            runner_version = app.runner_version.get()
            session.log_debug('%s selected version: %s (default applications)' % (
                runner_name,
                runner_version
            ))

            if runner_version == 'default':
                runner_version = None

        return runner_version

    def get_buttons(self):
        return self._buttons.get()
    
    def runner_configured(self):
        '''
        Returns None if the runner run by this action if properly configured,
        or a message which describes what remains to be configured, and sets
        the available buttons in the `_buttons` parameter accordingly.
        
        This function checks in the following order:
            1. if a default application exists according to the target file extension
            2. if the runner type is defined
            3. if the runner's executable path is defined (unless it's the DefaultEditor)
        '''
        name, tags = self.runner_name_and_tags()
        ext = self.target_file_extension()
        msg = None

        if self.get_default_app(ext) is None: # no default app defined for the target file extension
            msg = ('A default application must be defined for '
                f'file extension \'{ext}\'.\n\n')
            self._buttons.set(['Cancel'])
        elif not self.root().session().cmds.SubprocessManager.get_runner_versions(name, tags) is not None:
            msg = (f'Runner \'{name}\' not found: make sure it is '
                'registered in the project runner factory.\n\n')
            self._buttons.set(['Cancel'])
        elif name != 'DefaultEditor' and not self.check_runner_env_priority(name, self.get_version(None)):
            msg = ('An executable path must be defined for runner '
                f'\'{name}\'.\n\n')
            self._buttons.set(['Cancel'])

        return msg

    def needs_dialog(self):
        msg = self.runner_configured()
        if msg is not None:
            name, _ = self.runner_name_and_tags()
            error_txt = '<div style="color: red">Error:</div>'
            self.root().session().log_error(msg)
            self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                f'Application {name} not configured (see terminal).'))
        return msg is not None
    
    def run(self, button):
        '''
        Sets the environment variable which contains the runner executable path
        before launching the runner.
        '''
        name, tags = self.runner_name_and_tags()
        version = self.get_version(button)

        self.check_runner_env_priority(name, version)
        
        rid = self.root().session().cmds.SubprocessManager.run(
            runner_name=name,
            tags=tags,
            version=version,
            label=self.get_run_label(),
            extra_argv=self.extra_argv(),
            extra_env=self.extra_env(),
            extra_handlers=self.extra_handlers()
        )
        return self.get_result(runner_id=rid)


class OpenRevision(GenericRunAction):

    ICON = ('icons.gui', 'open-folder')
    
    _file = flow.Parent(4)
    _revision = flow.Parent()
    
    def extra_argv(self):
        args = [self._revision.get_path()]

        # Use blender read-only script if it's not a working copy
        project_settings = self.root().project().settings()

        if project_settings.enable_publish_read_only.get() is True:
            if self._file.format.get() == 'blend':
                if not self._revision.is_working_copy():
                    args.extend(['--python', resources.get("scripts.blender", "disable_save_keymap.py")])
                elif self._file.file_user_status.get() == 'old':
                    args.extend(['--python', resources.get("scripts.blender", "disable_save_keymap.py"), '--', 'working_copy'])

        return args
    
    def allow_context(self, context):
        return context and self._revision.get_sync_status() == 'Available'
    
    def needs_dialog(self):
        ret = GenericRunAction.needs_dialog(self)

        if not ret:
            available = self._revision.get_sync_status() == 'Available'
            exists = self._revision.exists()

            if not available:
                self.message.set((
                    '<h2>Unavailable revision</h2>'
                    'This revision is not available on the current site.'
                ))
            elif not exists:
                self.message.set((
                    '<h2>Missing revision</h2>'
                    'This revision does not exist on the current site.'
                ))
            ret = (not available or not exists)
        
        return ret
    
    def get_buttons(self):
        return ['Close']
    
    def run(self, button):
        if button == 'Close':
            return
        
        super(OpenRevision, self).run(button)


class RevealInExplorer(RunAction):
    """
    Reveals a location in the explorer.

    This location must be specified in `get_target_path()`.
    """

    ICON = ('icons.flow', 'explorer')

    _file = flow.Parent()
    _buttons = flow.SessionParam(list)

    def runner_name_and_tags(self):
        return "DefaultEditor", []

    def extra_argv(self):
        return [self.get_target_path()]
    
    def get_buttons(self):
        return self._buttons.get()

    def needs_dialog(self):
        msg = self.runner_configured()
        if msg is not None:
            name, _ = self.runner_name_and_tags()
            error_txt = '<div style="color: red">Error:</div>'
            self.root().session().log_error(msg)
            self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                f'Application {name} not configured (see terminal).'))
            self._buttons.set(['Cancel'])
        return msg is not None
    
    def runner_configured(self):
        '''
        Returns None if the type of the runner run by this action is registered in the
        project's runner factory, or a message as a string describing the error.
        '''
        msg = None
        name, tags = self.runner_name_and_tags()
        versions = self.root().session().cmds.SubprocessManager.get_runner_versions(name, tags)
        if versions is None:
            msg = (f'Runner \'{name}\' not found: make sure it is '
                'registered in the project runner factory.\n\n')
        return msg
    
    def get_target_path(self):
        raise NotImplementedError()
    
    def run(self, button):
        if button == 'Cancel':
            return
        return super(RevealInExplorer, self).run(button)


class RevealRevisionInExplorer(RevealInExplorer):
    """
    Reveals a tracked file revision in the explorer.
    """

    _revision = flow.Parent()

    def allow_context(self, context):
        return (
            context
            and self._revision.exists()
            and self._revision.get_sync_status() == 'Available'
        )
    
    def get_target_path(self):
        return os.path.dirname(self._revision.get_path())


class ComputeRevisionHash(LaunchSessionWorker):
    _revision = flow.Parent()

    def get_run_label(self):
        return 'Compute revision hash'

    def allow_context(self, context):
        return False

    def launcher_oid(self):
        return self._revision.oid()

    def launcher_exec_func_name(self):
        return "update_hash"


class CheckRevisionHash(flow.Action):
    _revision = flow.Parent()

    def get_buttons(self):
        self.message.revert_to_default()
        return ["Check", "Close"]
    
    def run(self, button):
        if button == "Close":
            return

        if self._revision.hash_is_valid():
            color = "029600"
            msg = "Hash is valid !"
        else:
            color = "D5000D"
            msg = "Invalid hash"

        self.message.set((
            f"<h3><font color=#{color}>"
            f"{msg}</font></h3>"
        ))

        return self.get_result(close=False)


class KeepEditingValue(flow.values.SessionValue):

    _action = flow.Parent()

    def check_default_value(self):
        user = self.root().project().get_user()

        if user.preferences.keep_editing.enabled.get():
            # Check if default value is defined in user preferences
            default = user.preferences.keep_editing.value.get()
            self.set(default)
        else:
            # No default value: do nothing
            pass

from .users import PresetValue, PresetSessionValue, PresetChoiceValue

class UploadAfterPublishValue(flow.values.SessionValue):

    _action = flow.Parent()

    def check_default_value(self):
        if self._action._file.to_upload_after_publish():
            # Option enabled for this file in the project settings
            self.set(True)
        else:
            # No default value: do nothing
            pass

    def _fill_ui(self, ui):
        settings = self.root().project().admin.project_settings
        f = self._action._file

        for pattern in settings.get_hidden_upload_files():
            if fnmatch.fnmatch(f.display_name.get(), pattern):
                ui['hidden'] = True
                break


class PublishFileAction(LaunchSessionWorker):

    ICON = ("icons.libreflow", "publish")

    _file = flow.Parent()
    _map = flow.Parent(2)

    comment = flow.SessionParam("", PresetSessionValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(
        editor='bool',
        tooltip='If disabled, delete your working copy after publication'
    )
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def get_run_label(self):
        return 'Upload revision'
    
    def check_default_values(self):
        self.comment.apply_preset()
        self.keep_editing.apply_preset()
        self.upload_after_publish.check_default_value()
    
    def update_presets(self):
        self.comment.update_preset()
        self.keep_editing.update_preset()

    def get_buttons(self):
        self.check_default_values()
        
        msg = "<h2>Publish</h2>"

        working_copies = self._file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "This file is currently being edited by one or more users (%s)."
                "</font></h3>"
                % ', '.join(user_names)
            )

        self.message.set(msg)
        
        return ['Publish', 'Cancel']

    def allow_context(self, context):
        return context and self._file.editable() and self._file.has_working_copy(True)
    
    def launcher_oid(self):
        return self.oid()

    def launcher_exec_func_name(self):
        return "_process_revision"

    def launcher_exec_func_kwargs(self):
        return dict(
            upload_after_publish=self.upload_after_publish.get()
        )

    def _target_file(self):
        return self._file
    
    def _revision_to_process(self):
        return self._target_file().get_head_revision()
    
    def _process_revision(self, upload_after_publish):
        file = self._target_file()
        rev = self._revision_to_process()
        
        if upload_after_publish:
            self._upload(rev)
            self._map.touch()
    
    def _upload(self, revision):
        current_site = self.root().project().get_current_site()

        upload_job = current_site.get_queue().submit_job(
            emitter_oid=revision.oid(),
            user=self.root().project().get_user_name(),
            studio=current_site.name(),
            job_type='Upload',
            init_status='WAITING'
        )
        sync_manager = self.root().project().get_sync_manager()
        sync_manager.process(upload_job)
    
    def _save_blend_dependencies(self, revision):
        '''deprecated and not used anymore'''
        from blender_asset_tracer import trace, bpathlib
        from pathlib import Path
        import collections

        path = Path(revision.get_path())
        report = collections.defaultdict(list)

        for usage in trace.deps(path):
            filepath = usage.block.bfile.filepath.absolute()
            asset_path = str(usage.asset_path).replace('//', '')
            report[str(filepath)].append(asset_path)
        
        revision.dependencies.set(dict(report))
    
    def publish_file(self, file, comment, keep_editing, upload_after_publish=None):
        file.lock()
        published_revision = file.publish(comment=comment, keep_editing=keep_editing)

        if not keep_editing:
            file.set_current_user_on_revision(published_revision.name())
            file.unlock()

        published_revision.make_current.run(None)
        file.touch()

        if upload_after_publish is not None:
            self.upload_after_publish.set(upload_after_publish)

        super(PublishFileAction, self).run(None)

    def allow_context(self, context):
        return (
            context and (
                self._file.has_working_copy(from_current_user=True)
                and (
                    not self._file.is_locked()
                    or self._file.is_locked(by_current_user=True)
                )
            )
        )

    def run(self, button):
        if button == "Cancel":
            return
        
        project_settings = self.root().project().settings()
        if self.comment.get() == "" and not project_settings.optional_publish_comment.get():
            self.message.set(
                "<h2>Publish</h2>"
                "Please enter a comment to describe your changes.")
            return self.get_result(close=False)
        
        self.update_presets()
        
        target_file = self._target_file()
        self.publish_file(
            target_file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get()
        )


class PublishFileFromWorkingCopy(flow.Action):

    ICON = ('icons.libreflow', 'publish')

    _revision = flow.Parent()
    _file = flow.Parent(4)
    
    comment = flow.SessionParam('', PresetSessionValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(
        editor='bool',
        tooltip='If disabled, delete your working copy after publication'
    )
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def allow_context(self, context):
        return (
            context
            and self._revision.is_working_copy(from_current_user=True)
            and (
                not self._file.is_locked()
                or self._file.is_locked(by_current_user=True)
            )
        )
    
    def get_buttons(self):
        self.check_default_values()
        
        msg = "<h2>Publish</h2>"

        working_copies = self._file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "This file is currently being edited by one or more users (%s)."
                "</font></h3>"
                % ', '.join(user_names)
            )

        self.message.set(msg)
        
        return ['Publish', 'Cancel']

    def check_default_values(self):
        self.comment.apply_preset()
        self.keep_editing.apply_preset()
        self.upload_after_publish.check_default_value()
    
    def update_presets(self):
        self.comment.update_preset()
        self.keep_editing.update_preset()

    def run(self, button):
        if button == 'Cancel':
            return
        
        self.update_presets()

        publish_action = self._file.publish_action
        publish_action.publish_file(
            self._file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get(),
            upload_after_publish=self.upload_after_publish.get()
        )


class RevisionStatus(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    STRICT_CHOICES = False

    def choices(self):
        return ['init'] + self.root().project().admin.project_settings.revision_statutes.get()
    
    def revert_to_default(self):
        self.set(self.choices()[0])


class ChangeRevisionStatus(flow.Action):

    status = flow.SessionParam(None, RevisionStatus)

    _revision = flow.Parent()

    def allow_context(self, context):
        return context and not self._revision.working_copy.get()
    
    def get_buttons(self):
        return ['Confirm', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._revision.set_status(self.status.get())
        self._revision.touch()


class SiteName(flow.values.ChoiceValue):
    
    def choices(self):
        sites = self.root().project().get_working_sites()
        return sites.mapped_names()
    
    def revert_to_default(self):
        site = self.root().project().get_current_site()
        self.set(site.name())


class RevisionActionDependencyView(DependencyView):
    
    _parent = flow.Parent(5)
    
    def get_site_name(self):
        return self._action.target_site.get()
    
    def get_revision_name(self):
        return self._action.revision.name()


class RequestRevisionDependencies(flow.Action):

    ICON = ('icons.libreflow', 'dependencies')
    
    revision = flow.Parent().ui(hidden=True)
    target_site = flow.Param(None, ActiveSiteChoiceValue).watched()
    dependencies = flow.Child(RevisionActionDependencyView)
    predictive_only = flow.SessionParam(False).ui(editor='bool').watched()
    
    def child_value_changed(self, child_value):
        if child_value in [self.target_site, self.predictive_only]:
            self.update_dependencies()
    
    def update_dependencies(self):
        self.dependencies.update_dependencies_data()
        self.dependencies.touch()
    
    def get_buttons(self):
        choices = self.target_site.choices()
        
        if not choices:
            return ['Cancel']
        
        self.target_site.set(choices[0])
        
        return ['Proceed', 'Cancel']
    
    def allow_context(self, context):
        return context and not self.revision.is_working_copy()
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        target_site = self.target_site.get()
        
        for d in self.dependencies.mapped_items():
            revision_oid = d.revision_oid.get()
            if revision_oid is not None and d.in_breakdown.get():
                rev = self.root().get_object(revision_oid)
                status = rev.get_sync_status(site_name=target_site)
                
                if status == 'NotAvailable':
                    rev.request_as.sites.target_site.set(target_site)
                    rev.request_as.sites.source_site.set(d.source_site.get())
                    rev.request_as.run(None)
        
        return self.get_result(close=False)


class SyncStatus(Entity):

    status = Property().ui(editable=False)

    def get_default_value(self):
        return 'NotAvailable'


class SyncStatutes(EntityView):
    '''
    This class manages the synchronization statutes of a tracked file revision.
    '''

    _revision = flow.Parent()
    _history = flow.Parent(3)

    @classmethod
    def mapped_type(cls):
        return SyncStatus
    
    def set_status(self, site_name, status):
        if site_name not in self.mapped_names():
            s = self.add(site_name)
        else:
            s = self.get_mapped(site_name)
        
        s.status.set(status)
        
        self._document_cache = None # Reset map cache
        self._history.sync_statutes.touch() # Reset history status map cache

    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_sync_status_collection().collection_name()


class Revision(CustomEntity):

    _revisions = flow.Parent()
    _history = flow.Parent(2)
    _file = flow.Parent(3)

    user = Property().ui(editable=False)
    date = Property().ui(editable=False, editor='datetime')
    comment = Property().ui(editable=False)
    site = Property().ui(editable=False)
    hash = Property().ui(editable=False)
    ready_for_sync = Property().ui(editable=False, editor='bool')
    working_copy = Property().ui(editable=False, editor='bool')
    path = Property().ui(editable=False)
    file_size = Property().ui(editable=False)
    source = Property().ui(editable=False)
    status = Property().ui(editable=False)

    sync_statutes = flow.Child(SyncStatutes).injectable()

    settings = flow.Child(ContextualView).ui(hidden=True)

    open = flow.Child(OpenRevision)
    publish = flow.Child(PublishFileFromWorkingCopy)
    create_working_copy = flow.Child(CreateWorkingCopyFromRevision).injectable()
    upload = flow.Child(UploadRevision)
    download = flow.Child(DownloadRevision)
    reveal = flow.Child(RevealRevisionInExplorer).ui(label='Reveal in explorer')
    change_status = flow.Child(ChangeRevisionStatus)
    request = flow.Child(Request)
    request_as = flow.Child(RequestAs)
    request_dependencies = flow.Child(RequestRevisionDependencies)
    compute_hash_action = flow.Child(ComputeRevisionHash)
    check_hash = flow.Child(CheckRevisionHash)
    make_current = flow.Child(MakeCurrentRevisionAction)
    dependencies = flow.Param("").ui(editor='textarea', editable=False)

    @classmethod
    def get_property_names_and_labels(cls):
        return [
            ('name', 'Revision'), ('user', 'Creator'),
            ('date', 'Created on'), ('comment', 'Comment')
        ]

    @classmethod
    def get_source_display(cls, oid):
        split = oid.split('/')
        indices = list(range(len(split) - 4, 2, -2))
        indices[:0] = [len(split)-1]
        return ' – '.join([split[i] for i in reversed(indices)])
    
    def configure(self, creator_name, is_working_copy, site_name, status, comment, ready_for_sync, from_revision, init_status):
        self.date.set(time.time())
        self.user.set(creator_name)
        self.working_copy.set(is_working_copy)
        self.site.set(site_name)
        self.set_sync_status(status)
        self.comment.set(comment)
        self.ready_for_sync.set(ready_for_sync)
        self.source.set(from_revision)
        self.status.set(init_status)

    def get_path(self, relative=False):
        '''
        If relative is True, returns the path of this
        revision without the project root. Otherwise,
        returns the complete path of the revision on the
        current site.
        In case the `path` of this revision is undefined,
        it is computed according to the path format of its
        parent file. If this file's path format is undefined,
        the function raises an exception.
        '''
        path = self.path.get()

        if path == '' or path is None:
            path_format = self._file.path_format.get()
            if path_format == '' or path_format is None:
                raise Exception((f"Revision.get_path(): Cannot "\
                    f"compute the path of {self.oid()}: " \
                     "its parent file must have a valid path format"))

            self.root().session().log_warning(
                f"Revision.get_path(): {self.oid()} path "\
                 "undefined -> compute it from file path format")
            self.update_path(self._file.path_format.get())
            path = self.path.get()

        if not relative:
            path = os.path.normpath(os.path.join(
                self.root().project().get_root(), path
            ))
        
        return path
    
    def update_path(self, path_format=None):
        '''
        Updates the relative path of this revision.

        If provided, `path_format` must be a format string
        from which the path will be computed. Otherwise,
        the path will defaults to the value returned by
        `get_default_path()`.
        '''
        if path_format is None:
            path = self.get_default_path()
        else:
            path = self._compute_path(path_format)
        
        self.path.set(path.replace('\\', '/'))
    
    def _get_default_suffix(self):
        '''
        Returns the default path suffix of this revision.

        The suffix should contain the revision underlying
        file name, possibly under one or more folders.
        Default is to return the revision's file complete
        name under a folder with the name of the revision
        (e.g., <revision_name>/<file_complete_name>.<file_extension>)
        '''
        file_name = '{file_name}.{extension}'.format(
            file_name=self._file.complete_name.get(),
            extension=self._file.format.get()
        )
        return os.path.join(self.name(), file_name)
    
    def get_default_path(self):
        '''
        Returns the default relative path of this revision.
        '''
        return os.path.join(
            self._file.get_default_path(), self._get_default_suffix()
        )
    
    def _compute_path(self, path_format):
        '''
        Computes a path given the format string `path_format`.
        
        By default, keywords in `path_format` are replaced
        with the values of the entries with the same names
        in the contextual settings of this revision.
        In case there is no match, a keyword is replaced by
        an empty string.
        '''
        kwords = keywords_from_format(path_format)
        settings = get_contextual_dict(self, 'settings')
        values = {}
        for kword in kwords:
            values[kword] = settings.get(kword, '')
        
        path = pathlib.Path(path_format.format(**values))
        
        return f'{path}.{self._file.format.get()}'

    def is_current(self):
        return self.name() == self._file.current_revision.get()

    def is_working_copy(self, from_current_user=False):
        return (
            self.working_copy.get()
            and (
                not from_current_user
                or self.name() == self.root().project().get_user_name()
            )
        )

    def get_sync_status(self, site_name=None, exchange=False):
        """
        Returns revision's status on the site identified
        by the given name, or the project's exchange site
        if `exchange` is True.

        If site_name is None, this method returns its status
        on the current site.
        """
        if exchange:
            site_name = self.root().project().admin.multisites.exchange_site_name.get()
        elif not site_name:
            site_name = self.root().project().admin.multisites.current_site_name.get()
        
        return self._history.sync_statutes.get_status(self.name(), site_name)

    def set_sync_status(self, status, site_name=None, exchange=False):
        """
        Sets revision's status on the site identified
        by the given name, or the project's exchange site
        if `exchange` is True, to the given status.

        If site_name is None, this method sets its status
        on the current site.
        """
        if exchange:
            site_name = self.root().project().admin.multisites.exchange_site_name.get()
        elif not site_name:
            site_name = self.root().project().admin.multisites.current_site_name.get()

        self.sync_statutes.set_status(site_name, status)
    
    def set_status(self, status):
        if self.working_copy.get():
            self.root().session().log_warning(
                'You cannot modify the status of a working copy.'
            )
            return
        
        self.status.set(status)
    
    def update_status(self, forced=False):
        status = self.status.get() or None

        if status is None or forced:
            if self.working_copy.get():
                if self.root().project().get_user_name() == self.name():
                    self.status.set('working_copy_mine')
                else:
                    self.status.set('working_copy')
            else:
                self.status.set('init')

    def get_last_edit_time(self):
        if self.exists():
            return os.path.getmtime(self.get_path())
        
        return 0
    
    def exists(self):
        return os.path.exists(self.get_path())
    
    def compute_hash(self):
        path = self.get_path()
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()

            return hashlib.md5(content).hexdigest()
    
    def update_hash(self):
        self.hash.set(self.compute_hash())
        self.hash.touch()
    
    def hash_is_valid(self):
        return self.hash.get() == self.compute_hash()
    
    def activate_oid(self):
        return self.open.oid()
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            nums = list_digits(self.name())
            dt = datetime.datetime.fromtimestamp(self.date.get())
            return dict(
                revision=self.name(),
                revision_number=nums[0] if nums else -1,
                revision_date=dt.strftime('%y%m%d'),
                revision_working_copy=self.is_working_copy()
            )


class ToggleSyncStatuses(flow.Action):
    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._revisions.show_sync_statuses.set(
            not self._revisions.show_sync_statuses.get()
        )
        self._revisions.touch()


class ToggleShortNames(flow.Action):
    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._revisions.enable_short_names.set(
            not self._revisions.enable_short_names.get()
        )
        self._revisions.touch()


class TogglePublicationDateFormat(flow.Action):
    
    ICON = ('icons.libreflow', 'time_format')
    
    _revisions = flow.Parent()
    
    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def run(self, button):
        enabled = self._revisions.time_ago_enabled.get()
        self._revisions.time_ago_enabled.set(not enabled)
        self._revisions.touch()


class ToggleActiveSites(flow.Action):

    ICON = ('icons.libreflow', 'active_site')

    _revisions = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        active_sites_only = self._revisions.active_sites_only
        active_sites_only.set(not active_sites_only.get())


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    '''
    Sort a string in a natural way
    https://stackoverflow.com/a/16090640
    '''
    return [int(text) if text.isdigit() else text.lower()
            for text in _nsre.split(s)]


class Revisions(EntityView):

    STYLE_BY_STATUS = {
        "Available":    ("#45cc3d", ("icons.libreflow", "checked-symbol-colored")),
        "Requested":    ("#cc3b3c", ("icons.libreflow", "exclamation-sign-colored")),
        "NotAvailable": ("#cc3b3c", ("icons.libreflow", "blank"))
    }

    _history = flow.Parent()
    _file = flow.Parent(2)
    _needs_update = flow.SessionParam(True).ui(editor='bool')

    show_sync_statuses = flow.SessionParam(True).ui(hidden=True, editor='bool')
    enable_short_names = flow.SessionParam(True).ui(hidden=True, editor='bool').watched()
    time_ago_enabled = flow.SessionParam(False).ui(hidden=True, editor='bool')
    active_sites_only = flow.SessionParam(True).ui(hidden=True, editor='bool').watched()

    toggle_sync_statuses = flow.Child(ToggleSyncStatuses)
    toggle_short_names = flow.Child(ToggleShortNames)
    toggle_date_format = flow.Child(TogglePublicationDateFormat)
    toggle_active_sites = flow.Child(ToggleActiveSites)

    def __init__(self, parent, name):
        super(Revisions, self).__init__(parent, name)
        self._site_names_cache = None
        self._file_cache = None
        self._file_cache_ttl = 5

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(Revision)
    
    def mapped_names(self, page_num=0, page_size=None):
        names = super(Revisions, self).mapped_names(page_num, page_size)
        return sorted(names, key=natural_sort_key)

    def columns(self):
        columns = ['Revision', 'Creator', 'Created on']
        
        if self.show_sync_statuses.get():
            _, display_names = self._ensure_site_names()
            columns += display_names
        
        columns.append('Comment')

        return columns

    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_revision_collection().collection_name()

    def add(self, name=None, is_working_copy=False, comment="", ready_for_sync=True, path_format=None, from_revision=None, init_status=None):
        if not name:
            publication_count = len([r for r in self.mapped_items() if not r.is_working_copy()])
            name = 'v%03i' % (publication_count + 1)
        
        if not is_working_copy:
            init_status = init_status or 'init'

        r = super(Revisions, self).add(name)
        r.configure(
            creator_name=self.root().project().get_user_name(),
            is_working_copy=is_working_copy,
            site_name=self.root().project().admin.multisites.current_site_name.get(),
            status='Available',
            comment=comment,
            ready_for_sync=ready_for_sync,
            from_revision=from_revision,
            init_status=init_status
        )
        r.update_status()
        r.update_path(path_format)

        self._document_cache = None # Reset map cache
        
        return r
    
    def remove(self, name):
        r = self.get_mapped(name)
        r.sync_statutes.clear()
        super(Revisions, self).remove(name)
    
    def clear(self):
        for r in self.mapped_items():
            r.sync_statutes.clear()
        
        super(Revisions, self).clear()
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                file=self._file.name(),
                file_base_name=self._file.complete_name.get(),
                file_display_name=self._file.display_name.get(),
                file_extension=self._file.format.get()
            )

    def _fill_row_cells(self, row, item):
        self.mapped_names()

        name = item.name()
        if self._document_cache[item.oid()]['working_copy']:
            name += " ("
            if item.name() == self.root().project().get_user_name():
                name += "your "
            name += "working copy)"
        
        if item.get_sync_status() == "Requested":
            name += " ⏳"
        
        row['Revision'] = name
        row['Creator'] = self._document_cache[item.oid()]['user']
        row['Comment'] = self._document_cache[item.oid()]['comment']
        create_datetime = datetime.datetime.fromtimestamp(self._document_cache[item.oid()]['date'])

        if self.time_ago_enabled.get():
            row['Created on'] = timeago.format(create_datetime, datetime.datetime.now())
        else:
            row['Created on'] = create_datetime.strftime('%Y-%m-%d %H:%M:%S')

        if self.show_sync_statuses.get():
            _, display_names = self._ensure_site_names()
            d = dict.fromkeys(display_names, '')
            row.update(d)

    def _fill_row_style(self, style, item, row):
        file_data = self._ensure_file_data()
        seen_name = file_data['active']
        
        if item.name() == file_data['current']:
            if item.name() == seen_name or seen_name == "current":
                style["icon"] = ('icons.libreflow', 'circular-shape-right-eye-silhouette')
            else:
                style["icon"] = ('icons.libreflow', 'circular-shape-silhouette')
        else:
            if item.name() == seen_name:
                style["icon"] = ('icons.libreflow', 'circle-shape-right-eye-outline')
            else:
                style["icon"] = ('icons.libreflow', 'circle-shape-outline')

        style['Revision_foreground-color'] = self.STYLE_BY_STATUS[item.get_sync_status()][0]

        if self.show_sync_statuses.get():
            names, display_names = self._ensure_site_names()
            
            for i in range(len(names)):
                style[display_names[i] + '_icon'] = self.STYLE_BY_STATUS[item.get_sync_status(names[i])][1]
        
        style["Revision_activate_oid"] = item.open.oid()
    
    def _get_site_names(self):
        sites_data = self.root().project().admin.multisites.sites_data.get()
        ordered_names = self.root().project().get_current_site().ordered_site_names.get()
        names = []
        display_names = []

        for name in ordered_names:
            if self.active_sites_only.get() and not sites_data[name]['is_active']:
                continue
            
            names.append(name)
        
        exchange_site = self.root().project().get_exchange_site()

        if self.enable_short_names.get():
            display_names = [exchange_site.short_name.get()]
            display_names += [sites_data[name]['short_name'] for name in names]
            names.insert(0, exchange_site.name())
        else:
            names.insert(0, exchange_site.name())
            display_names = names
        
        return names, display_names
    
    def _ensure_site_names(self):
        if self._site_names_cache is None or self._needs_update.get():
            self._site_names_cache = self._get_site_names()
            self._needs_update.set(False)
        
        return self._site_names_cache
    
    def _ensure_file_data(self):
        if (
            self._file_cache is None
            or self._file_cache_birth < time.time() - self._file_cache_ttl
        ):
            self._file_cache = {
                'active': self._file.current_user_sees.get(),
                'current': self._file.current_revision.get()
            }
            self._file_cache_birth = time.time()
        
        return self._file_cache

    def touch(self):
        self._file_cache = None
        super(Revisions, self).touch()

    def child_value_changed(self, child_value):
        if child_value in [self.enable_short_names, self.active_sites_only] and self.show_sync_statuses.get():
            self._needs_update.set(True)
            self.touch()


class HistorySyncStatutes(EntityCollection):
    '''
    This class caches all revisions statutes recorded
    in the revision store which belong to a given history.
    '''

    _history = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return SyncStatus
    
    def mapped_names(self, page_num=0, page_size=None):
        cache_key = (page_num, page_size)
        if (
            self._document_cache is None
            or self._document_cache_key != cache_key
            or self._document_cache_birth < time.time() - self._document_cache_ttl
        ):
            cursor = (
                self.get_entity_store()
                .get_collection(self.collection_name())
                .find(self.query_filter())
            )
            if page_num is not None and page_size is not None:
                cursor.skip((page_num - 1) * page_size)
                cursor.limit(page_size)
            
            name_and_doc = []
            for i in cursor:
                _, revision, _, site = i['name'].rsplit('/', maxsplit=3)
                name_and_doc.append((f'{revision}_{site}', i))
            
            self._document_names_cache = [n for n, d in name_and_doc]
            self._document_cache = dict(name_and_doc)
            self._document_cache_birth = time.time()
            self._document_cache_key = cache_key
            self.ensure_indexes()
        
        return self._document_names_cache

    def set_property(self, entity_name, property_name, value):
        self.mapped_names()
        self.get_entity_store().get_collection(self.collection_name()).update_one(
            {"name": self._document_cache[entity_name]['name']},
            {"$set": {property_name: value}},
        )

    def get_property(self, entity_name, property_name):
        self.root().session().log_debug(f'===========> {self._history.revisions.oid()}/{entity_name} {property_name}')
        self.mapped_names()

        value = (
            self.get_entity_store()
            .get_collection(self.collection_name())
            .find_one(
                {"name": self._document_cache[entity_name]['name']},
                {property_name: 1},
            )
        )
        try:
            return value[property_name]
        except KeyError:
            default = getattr(self.mapped_type(), property_name).get_default_value()
            return default
    
    def get_status(self, revision_name, site_name):
        self.mapped_names()
        st = self._document_cache.get(
            f'{revision_name}_{site_name}',
            {'status': 'NotAvailable'}
        )
        return st['status']

    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_sync_status_collection().collection_name()
    
    def query_filter(self):
        return {'name': {'$regex': f'^{self._history.revisions.oid()}/[^/]*'}}


class History(flow.Object):

    revisions = flow.Child(Revisions).injectable().ui(expanded=True)
    sync_statutes = flow.Child(HistorySyncStatutes).injectable().ui(hidden=True)
    department = flow.Parent(3)


class CreateWorkingCopyAction(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    _file = flow.Parent()
    _task = flow.Parent(3)
    _tasks = flow.Parent(4)

    from_revision = flow.Param(None, RevisionsWorkingCopiesChoiceValue).ui(label="Reference")

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        # Buttons for Use Base File mode
        if self.use_base_file:
            msg += f"<font color=#FFA34D>WARNING: You should start working on this file \
                    from the latest version of {self.base_file_name} in {self.from_task} task.</font>"
            self.message.set(msg)
            return ["Create from base file", "Create from scratch", "Cancel"]

        if self._file.has_working_copy(from_current_user=True):
            msg += "<font color=#FFA34D>WARNING: You already have a working copy to your name. \
                    Choosing to create a new one will overwrite your changes.</font>"
        self.message.set(msg)

        self.from_revision.revert_to_default()

        return ["Create", "Create from scratch", "Cancel"]

    def needs_dialog(self):
        # Alert user if use base file is enabled and source revision has not been created
        default_file = self.root().project().get_task_manager().get_task_files(self._task.name()).get(
            self._file.name()
        )

        self.use_base_file = False
        if default_file is not None and default_file[5]:
            if self._file.is_empty():
                self.use_base_file = True
                self.from_task = default_file[8]
                self.base_file_name = default_file[9]
                return True

        # Default use case
        return not self._file.is_empty() or self._file.has_working_copy(
            from_current_user=True
        )

    def allow_context(self, context):
        return context and self._file.editable()

    def run(self, button):
        if button == "Cancel":
            return
        
        if button == "Create from base file":
            # Check if source revision exists
            base_name, base_ext = os.path.splitext(self.base_file_name)
            source_revision = None

            if self._tasks.has_mapped_name(self.from_task):
                source_task = self._tasks[self.from_task]
                exists = (
                    base_ext and source_task.files.has_file(base_name, base_ext[1:])
                    or source_task.files.has_folder(base_name))

                if exists:
                    source_file = source_task.files[self.base_file_name.replace('.', '_')]
                    source_revision = source_file.get_head_revision(sync_status="Available")
                    
                    if source_revision is not None:
                        comment = f'from base file {self.base_file_name} {source_revision.name()}'

            # Create base revision
            if source_revision is not None and os.path.exists(source_revision.get_path()):
                r = self._file.add_revision(comment=comment)
                target_path = r.get_path()
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                if self._file.format.get():
                    shutil.copy2(source_revision.get_path(), target_path)
                else:
                    shutil.copytree(source_revision.get_path(), target_path)
            else:
                # Show error if source revision doesn't exist
                msg = self.message.get()
                if 'no revision' not in msg:
                    msg += f"<br><br><font color=#FF584D>There is no revision from {self.base_file_name}</font>"
                    self.message.set(msg)

                return self.get_result(close=False)
            
            # Create working copy from base revision
            working_copy = self._file.create_working_copy(from_revision=r.name())

        elif button == "Create from scratch":
            working_copy = self._file.create_working_copy()
        else:
            ref_name = self.from_revision.get()

            if ref_name == "" or self._file.is_empty():
                ref_name = None
            elif not self._file.has_revision(ref_name):
                msg = self.message.get()
                msg += (
                    "<br><br><font color=#FF584D>There is no revision %s for this file.</font>"
                    % ref_name
                )
                self.message.set(msg)

                return self.get_result(close=False)

            working_copy = self._file.create_working_copy(from_revision=ref_name)

        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


class SeeRevisionAction(flow.Action):

    ICON = ("icons.libreflow", "watch")

    _file = flow.Parent()
    revision_name = flow.Param(None, RevisionsChoiceValue).ui(label="Revision")

    def allow_context(self, context):
        return False

    def get_buttons(self):
        self.message.set("<h3>Choose a revision to open</h3>")

        if self._file.is_empty():
            self.message.set("<h3>This file has no revision</h3>")
            return ["Cancel"]

        seen_name = self._file.current_user_sees.get()
        if seen_name != "current" or self._file.has_current_revision():
            if seen_name == "current":
                seen_name = self._file.current_revision.get()
            self.revision_name.set(seen_name)
        else:
            self.revision_name.set(self._file.get_revisions().mapped_names[0])

        return ["See", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        name = self.revision_name.get()

        if self._file.get_revision(name).is_current():
            name = "current"

        self._file.set_current_user_on_revision(name)
        self._file.touch()


class OpenFileAction(GenericRunAction):

    ICON = ('icons.gui', 'open-folder')

    def extra_argv(self):
        return [self._file.get_path()]


class OpenTrackedFileAction(GenericRunAction):

    ICON = ('icons.gui', 'open-folder')

    _to_open = flow.SessionParam()
    _task = flow.Parent(3)
    revision_name = flow.Param(None, RevisionsChoiceValue).ui(label="Revision")

    def get_run_label(self):
        return 'Open file'

    def needs_dialog(self):
        msg = self.runner_configured()
        needs_dialog = (msg is not None)
        self._to_open.revert_to_default()

        if needs_dialog:
            name, _ = self.runner_name_and_tags()
            error_txt = '<div style="color: red">Error:</div>'
            self.root().session().log_error(msg)
            self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                f'Application {name} not configured (see terminal).'))
            self._buttons.set(['Cancel'])
        else:
            self.revision_name.revert_to_default()
            buttons = []
            default_file = self.root().project().get_task_manager().get_task_files(self._task.name()).get(
                self._file.name()
            )
            auto_open = False

            if default_file is not None and default_file[10]: # open last revision at double-clic
                last_rev = self._file.get_head_revision()
                if last_rev is not None:
                    self._to_open.set(last_rev.name())
                    auto_open = True
            
            if not auto_open: # fall back to default behavior
                if self._file.editable():
                    if not self._file.has_working_copy(from_current_user=True, sync_status='Available'):
                        if not self._file.get_revision_names(sync_status='Available', published_only=True):
                            msg = ("<h3>Empty file</h3>Start to edit this file "
                            "by creating a working copy.")
                        else:
                            msg = ("<h3>Open/edit file</h3>Select a published "
                            "revision to open, or create a working copy from it.")
                            buttons.append('Open revision')
                        
                        buttons.append('Create a working copy')
                        needs_dialog = True
                    else:
                        self._to_open.set(self._file.get_working_copy().name())
                else:
                    needs_dialog = True
                    msg = "<h3>Read-only file</h3>"

                    if self._file.get_revision_names(sync_status='Available', published_only=True):
                        msg += "Select a revision to open."
                        buttons.append('Open revision')
                    else:
                        msg += "This file is empty."

            if self.is_running(): # show a warning if working copy is already open
                msg = ("<font color = red>Working copy is already open</font>")
                needs_dialog = True

            if needs_dialog:
                buttons.append('Cancel')
                self.message.set(msg)
                self._buttons.set(buttons)
        
        return needs_dialog

    def allow_context(self, context):
        return context

    def is_running(self):
        runner_infos = self.root().session().cmds.SubprocessManager.list_runner_infos()
        if self._to_open.get() is None:
            return False
        
        revision_path = self._file.get_revision(self._to_open.get()).get_path()

        rid = next(
            (runner['id']
            for runner in runner_infos
            if revision_path in runner['command'] and runner['is_running'] is True), None
        )

        return True if rid else False

    def extra_argv(self):
        revision = self._file.get_revision(self._to_open.get())
        args = [revision.get_path()]
        
        # Conditions for use blender read-only script
        project_settings = self.root().project().settings()
        
        if project_settings.enable_publish_read_only.get() is True:
            if self._file.format.get() == 'blend':
                # Published revisions
                if not revision.is_working_copy():
                    args.extend(['--python', resources.get("scripts.blender", "disable_save_keymap.py")])
                # Working copy is outdated
                elif self._file.file_user_status.get() == 'old':
                    args.extend(['--python', resources.get("scripts.blender", "disable_save_keymap.py"), '--', 'working_copy'])

        return args

    def run(self, button):
        if button == 'Cancel':
            return

        if button == 'Create a working copy':
            # Create and open new working copy
            if self._file.editable() and not self._file.has_working_copy(from_current_user=True, sync_status='Available'):
                working_copy = self._file.create_working_copy(
                    from_revision=self.revision_name.get() if self.revision_name.get() else None)
                self._to_open.set(working_copy.name())
            else:
                self.root().session().log_error("\n\nCould not create a working "
                f"copy for user '{self.root().project().get_user_name()}': this "
                "file is not editable, or a working copy already exists.\n\n")
                return
        elif button == 'Open revision':
            # Open selected revision
            if self._file.get_revision_names(sync_status='Available', published_only=True):
                revision_name = self.revision_name.get()# = self._file.get_revision(self.revision_name.get())

                if revision_name not in self.revision_name.choices() or not self._file.has_revision(revision_name):
                    self.root().session().log_error("\n\nCould not open published "
                    f"revision '{revision_name}': this revision does not exist.\n\n")
                    return
                
                self._to_open.set(revision_name)
            else:
                self.root().session().log_error("\n\nCould not open a revision: "
                "this file is empty.\n\n")
                return
        elif self._to_open.get() is None: # no button pressed
            # Two possible cases:
            # - automatic opening is enabled but file is empty
            # - action is run programmatically but file is read-only or has no working copy
            self.root().session().log_error("\n\nCould not run open action: "
            "this file is either empty or not editable.\n\n")
            return

        result = super(OpenTrackedFileAction, self).run(button)
        self._file.touch()

        return result


class OpenWithDefaultApp(RunAction):

    def runner_name_and_tags(self):
        return "DefaultEditor", []

    def extra_env(self):
        env = {}
        env["USER_NAME"] = self.root().project().get_user_name()
        root_path = self.root().project().get_root()

        if root_path:
            env["ROOT_PATH"] = root_path

        return env


class OpenWithAction(OpenTrackedFileAction):
    
    def runner_name_and_tags(self):
        raise NotImplementedError()

    def allow_context(self, context):
        return context and self._file.format.get() in self.supported_extensions()

    @classmethod
    def supported_extensions(cls):
        raise NotImplementedError()


class OpenWithBlenderAction(OpenWithAction):

    ICON = ("icons.libreflow", "blender")

    def runner_name_and_tags(self):
        return "Blender", []

    @classmethod
    def supported_extensions(cls):
        return ["blend"]


class OpenWithKritaAction(OpenWithAction):

    ICON = ("icons.libreflow", "krita")

    def runner_name_and_tags(self):
        return "Krita", []

    @classmethod
    def supported_extensions(cls):
        return ["kra", "png", "jpg"]


class OpenWithVSCodiumAction(OpenWithAction):

    ICON = ("icons.libreflow", "vscodium")

    def runner_name_and_tags(self):
        return "VSCodium", []

    @classmethod
    def supported_extensions(cls):
        return ["txt"]


class OpenWithNotepadPPAction(OpenWithAction):

    ICON = ("icons.flow", "notepad")

    def runner_name_and_tags(self):
        return "NotepadPP", []

    @classmethod
    def supported_extensions(cls):
        return ["txt"]


class MakeFileCurrentAction(flow.Action):

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        head_revision = self._file.get_head_revision()
        return (
            context and head_revision is not None and not head_revision.is_current()
        )  # And user is admin ?

    def run(self, button):
        self.root().session().log_debug(
            "Make latest revision of file %s current" % self._file.name()
        )

        self._file.make_current(self._file.get_head_revision())
        self._file.touch()


class GotoHistory(flow.Action):

    ICON = ("icons.libreflow", "history")

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        return context

    def run(self, button):
        return self.get_result(goto=self._file.history.oid())


class LockAction(flow.Action):

    ICON = ("icons.gui", "padlock")

    _file = flow.Parent()

    def allow_context(self, context):
        return context and not self._file.is_locked()
    
    def needs_dialog(self):
        return False

    def run(self, button):
        self._file.lock()
        self._file._map.touch()


class UnlockAction(flow.Action):

    ICON = ("icons.gui", "open-padlock-silhouette")

    _file = flow.Parent()

    def allow_context(self, context):
        return self._file.is_locked(by_current_user=True)
    
    def needs_dialog(self):
        return False

    def run(self, button):
        self._file.unlock()
        self._file._map.touch()


class UserSees(flow.values.Value):
    pass


class ActiveUsers(flow.Map):
    @classmethod
    def mapped_type(cls):
        return UserSees

    def columns(self):
        return ["User", "Revision"]

    def _fill_row_cells(self, row, item):
        row["User"] = item.name()
        row["Revision"] = item.get()


class RevealFileInExplorer(RevealInExplorer):
    """
    Reveals a tracked file in the explorer.

    By default, the action opens the folder two levels
    above the file's first available revision.
    """

    _file = flow.Parent()

    def allow_context(self, context):
        return context and not self._file.is_empty()

    def get_target_path(self):
        available_revisions = self._file.get_revision_names(
            sync_status='Available'
        )
        r = self._file.get_revision(available_revisions[-1])

        return os.path.dirname(os.path.dirname(r.get_path()))


class FileSystemItem(Entity):

    _map = flow.Parent()
    _parent = flow.Parent(2)

    format        = Property().ui(editable=False)
    complete_name = Property().ui(editable=False)
    display_name  = Property().ui(editable=False)
    path_format   = Property().ui(editable=False)
    file_type     = Property().ui(editable=False)
    is_primary_file = Property().ui(editable=False)

    settings = flow.Child(ContextualView).ui(hidden=True)
    path = flow.Computed(cached=True)

    def get_name(self):
        return self.name()

    def get_path(self):
        return os.path.normpath(os.path.join(
            self.root().project().get_root(),
            self.path.get()
        ))

    def get_last_edit_time(self):
        path = self.get_path()
        if os.path.exists(path):
            return os.path.getmtime(path)
        
        return 0
    
    def compute_child_value(self, child_value):
        if child_value is self.path:
            self.path.set(os.path.join(
                self._map.get_parent_path(),
                self.get_name()
            ))
    
    def configure(self, format, complete_name, display_name, path_format):
        self.format.set(format)
        self.complete_name.set(complete_name)
        self.display_name.set(display_name)
        self.path_format.set(path_format)

    def create(self):
        raise NotImplementedError

    def remove(self):
        raise NotImplementedError
    
    def get_icon(self, extension=None):
        return ('icons.gui', 'text-file-1')
    
    def get_default_contextual_edits(self, context_name):
        if context_name == 'settings':
            return dict(
                file=self.name(),
                file_base_name=self.complete_name.get(),
                file_display_name=self.display_name.get(),
                file_extension=self.format.get()
            )


class File(FileSystemItem):

    open = flow.Child(OpenFileAction)
    reveal = flow.Child(RevealFileInExplorer).ui(label="Reveal in explorer")

    def get_name(self):
        return "%s.%s" % (self.complete_name.get(), self.format.get())

    def get_template_path(self):
        try:
            return resources.get("file_templates", "template.%s" % self.format.get())
        except resources.NotFoundError:
            raise resources.NotFoundError(
                "No template file for '%s' format." % self.format.get()
            )

    def editable(self):
        settings = self.root().project().admin.project_settings
        patterns = settings.non_editable_files.get().split(",")

        for pattern in patterns:
            pattern = pattern.encode('unicode-escape').decode().replace(" ", "")
            if fnmatch.fnmatch(self.display_name.get(), pattern):
                return False
        
        return True

    def create(self):
        shutil.copyfile(self.get_template_path(), self.get_path())

    def remove(self):
        os.remove(self.get_path())
    
    def get_icon(self, extension=None):
        return FILE_EXTENSION_ICONS.get(extension, ('icons.gui', 'text-file-1'))


class SearchExistingRevisions(flow.Action):

    _file = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        folders = [
            f for f in os.listdir(self._file.get_path()) if re.search(r"^v\d\d\d$", f)
        ]
        revisions = self._file.get_revisions()

        for name in folders:
            try:
                revisions.add(name)
            except ValueError:
                pass

        revisions.touch()


class LinkedJob(jobs_flow.Job):
    '''
    This class represents a flow job whose execution can be
    chained with that of other flow jobs. For this purpose,
    a `LinkedJob` manages two lists, recording:

      - the ids of all the jobs this flow job must wait for
      before it can be processed (i.e., unpaused)
      - the oids of all the flow jobs which this job will
      notify when it finishes
    
    To link two flow jobs together, the user may call
    `link_jobs()`. The method assumes the corresponding jobs
    in the database are paused.
    '''

    _waited_jobs = flow.OrderedStringSetParam() # jids
    _children    = flow.OrderedStringSetParam() # flow job oids

    @staticmethod
    def link_jobs(parent, child):
        '''
        Links two LinkedJob, in such a way that the `child`
        job will be unpaused when all its parents (including
        `parent`) notify it, and the `parent` job will notify
        all its children as soon as it is done.
        '''
        parent._children.add(child.oid(), parent._children.len())
        child._waited_jobs.add(parent.oid(), child._waited_jobs.len())
    
    def notify_children(self):
        for oid in self._children.get():
            child = self.root().get_object(oid)
            child.notify_done(self.oid())

    def notify_done(self, oid):
        if not self._waited_jobs.has(oid):
            return
        
        self._waited_jobs.remove(oid)

        if self._waited_jobs.len() == 0:
            # All waited jobs done: make this one ready to be processed
            self.root().session().cmds.Jobs.set_job_paused(self.job_id.get(), False)

    def execute(self):
        print('----------------EXECUTING JOB', self.oid())
        self.touch()
        self.root().session().cmds.Jobs.set_job_in_progress(self.job_id.get())
        try:
            self._do_job()
        except Exception as err:
            self.on_error(traceback.format_exc())
        else:
            self.root().session().cmds.Jobs.set_job_done(self.job_id.get())
            self.status.touch()
            self.touch()
            self.notify_children()
        finally:
            self.touch()


class FileJob(LinkedJob):

    _file = flow.Parent(2)
    
    def get_log_filename(self):
        root = str(pathlib.Path.home()) + "/.libreflow/log/"
        dt = datetime.datetime.fromtimestamp(self.get_created_on())
        dt = dt.astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")
        
        path = os.path.join(root, '%s_%s.log' % (self.__class__.__name__, dt))
        return path

    def is_running(self, runner_id):
        info = self.root().session().cmds.SubprocessManager.get_runner_info(runner_id)
        return info['is_running']

    def show_runner_info(self, runner_info, description=None):
        if description is not None:
            description = "- " + description
        else:
            description = ""
        self.root().session().log_info(f"[JOB INFO] Runner {runner_info['id']} started...")
        self.root().session().log_info(f"[JOB INFO] Description: {runner_info['label']} {description}")
        self.root().session().log_info(f"[JOB INFO] Command: {runner_info['command']}")
        self.root().session().log_info(f"[JOB INFO] Log path: {runner_info['log_path']}")

    def get_time(self):
        return str(datetime.datetime.now().strftime("%Y-%M-%D %H:%M:%S"))

    def on_error(self, error_message):
        self.root().session().log_error('{}'.format(error_message))
        self.root().session().cmds.Jobs.set_job_error(self.job_id.get(), error_message)
        self.status.touch()
        self.touch()

        raise Exception(error_message)

    def wait_runner(self, runner_ids):
        if runner_ids is None:
            raise Exception("Runner(s) undefined")

        for rid in runner_ids:
            info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
            self.show_runner_info(info)

        while len(runner_ids) > 0:
            time.sleep(1)

            for rid in runner_ids:
                if not self.is_running(rid):
                    runner_ids.pop(runner_ids.index(rid))
                    self.root().session().log_info(f"[JOB INFO] Runner {rid} finished")


class PlayblastJob(FileJob):

    revision = flow.Param().ui(editable=False)
    resolution_percentage = flow.Param('100').ui(editable=False)
    use_simplify = flow.BoolParam().ui(editable=False)
    reduce_textures = flow.BoolParam(False).ui(editable=False)
    target_texture_width = flow.IntParam(4096).ui(editable=False)

    def _do_job(self):
        # Job is to wait until the playblast is ended
        render_blender_playblast = self._file.render_blender_playblast
        render_blender_playblast.revision_name.set(self.revision.get())
        render_blender_playblast.resolution_percentage.set(self.resolution_percentage.get())
        render_blender_playblast.use_simplify.set(self.use_simplify.get())
        render_blender_playblast.reduce_textures.set(self.reduce_textures.get())
        render_blender_playblast.target_texture_width.set(self.target_texture_width.get())
        
        result = render_blender_playblast.run('Render')
        rid = result['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)

        while runner_info['is_running']:
            self.show_message("Waiting for runner %s to finish" % rid)
            time.sleep(1)
            
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message("Runner %s finished !" % rid)


class FileJobs(jobs_flow.Jobs):

    @classmethod
    def job_type(cls):
        return FileJob

    def create_job(self, job_type=None):
        name = '{}{:>05}'.format(self._get_job_prefix(), self._get_next_job_id())
        job = self.add(name, object_type=job_type)
        return job


class ResolutionChoiceValue(PresetChoiceValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return ['25', '50', '100']


class PlayblastQuality(flow.values.ChoiceValue):

    CHOICES = ['Preview', 'Final']


class RenderBlenderPlayblast(OpenWithBlenderAction):

    revision_name = flow.Param("", RevisionsChoiceValue).watched()
    quality = flow.Param('Final', PlayblastQuality)
    auto_play_playblast = flow.SessionParam(True, PresetSessionValue).ui(
        tooltip="Play playblast when render is finished",
        editor='bool',
        )
    with flow.group('Advanced'):
        resolution_percentage = flow.SessionParam(100)
    #     use_simplify = flow.SessionParam(False, PresetSessionValue).ui(
    #         tooltip="Use low-definition rigs",
    #         editor='bool',
    #         )

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    _shot       = flow.Parent(5)
    _sequence   = flow.Parent(7)

    def get_run_label(self):
        return 'Render playblast'

    def _sequence_number_from_name(self, sequence_name):
        tmp = re.findall(r"\d+", sequence_name)
        numbers = list(map(int, tmp))
        return numbers[0] if numbers else -999
    
    def check_default_values(self):
        self.revision_name.revert_to_default()
        # self.use_simplify.apply_preset()
        self.auto_play_playblast.apply_preset()
    
    def update_presets(self):
        # self.use_simplify.update_preset()
        self.auto_play_playblast.update_preset()

    def needs_dialog(self):
        msg = self.runner_configured()
        if msg is not None:
            name, _ = self.runner_name_and_tags()
            error_txt = '<div style="color: red">Error:</div>'
            self.root().session().log_error(msg)
            self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                f'Application {name} not configured (see terminal).'))
            self._buttons.set(['Cancel'])
        else:
            self.check_default_values()
            buttons = ['Render', 'Cancel']
            
            if self.root().project().get_current_site().site_type.get() == 'Studio' and self.root().project().get_current_site().pool_names.get():
                buttons.insert(1, 'Submit job')
            self._buttons.set(buttons)
            
        return True

    def allow_context(self, context):
        return (
            super(RenderBlenderPlayblast, self).allow_context(context)
            and not self._file.is_empty()
        )
    
    def playblast_infos_from_revision(self, revision_name):
        filepath = self._file.path.get()
        filename = "_".join(self._file.name().split("_")[:-1])

        # Check if there is a AE compositing file
        if self._files.has_file('compositing', "aep"):
            playblast_filename = filename + "_movie_blend"
            playblast_revision_filename = self._file.complete_name.get() + "_movie_blend.mov"
        else:
            playblast_filename = filename + "_movie"
            playblast_revision_filename = self._file.complete_name.get() + "_movie.mov"
        
        playblast_filepath = os.path.join(
            self.root().project().get_root(),
            os.path.dirname(filepath),
            playblast_filename + "_mov",
            revision_name,
            playblast_revision_filename
        )

        return playblast_filepath, playblast_filename, self._file.path_format.get()

    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            msg = "<h2>Render playblast</h2>"
            playblast_path, _, _ = self.playblast_infos_from_revision(child_value.get())

            # Check if revision playblast exists
            if os.path.exists(playblast_path):
                msg += (
                    "<font color=#D50000>"
                    "Choosing to render a revision's playblast "
                    "will override the existing one."
                    "</font>"
                )

            self.message.set(msg)
    
    def get_shot_frame_count(self):
        kitsu_api = self.root().project().kitsu_api()
        if not kitsu_api.host_is_valid():
            return 0
        
        # Don't check frame count if entity is a asset
        if 'shots' not in self._shot.oid():
            return 0

        sequence_data = kitsu_api.get_sequence_data(self._sequence.name())
        shot_data = kitsu_api.get_shot_data(self._shot.name(),sequence_data)
        if shot_data['nb_frames'] is not None:
            return shot_data['nb_frames']
        else:
            return 0

    def extra_argv(self):
        file_settings = get_contextual_dict(
            self._file, "settings", ["sequence", "shot"]
        )
        project_name = self.root().project().name()
        revision = self._file.get_revision(self.revision_name.get())
        do_render = self.quality.get() == 'Final'
        python_expr = """import bpy
bpy.ops.lfs.playblast(do_render=%s, filepath='%s', studio='%s', project='%s', sequence='%s', scene='%s', quality='%s', version='%s', template_path='%s', do_autoplay=%s, frame_count=%s, resolution_percentage=%s)""" % (
            str(do_render),
            self.output_path,
            self.root().project().get_current_site().name(),
            project_name,
            file_settings.get("sequence", "undefined") if 'shots' in self._shot.oid() else file_settings.get("asset_type", "undefined"),
            file_settings.get("shot", "undefined") if 'shots' in self._shot.oid() else file_settings.get("asset", "undefined"),
            'PREVIEW' if self.quality.get() == 'Preview' else 'FINAL',
            self.revision_name.get(),
            resources.get('mark_sequence.fields', 'default.json').replace('\\', '/'),
            self.auto_play_playblast.get(), 
            self.get_shot_frame_count(),
            self.resolution_percentage.get(),
        )
        if not do_render:
            python_expr += "\nbpy.ops.wm.quit_blender()"
        
        args = [
            revision.get_path(),
            "--addons",
            "mark_sequence",
            "--python-expr",
            wrap_python_expr(python_expr),
        ]

        if do_render:
            args.insert(0, '-b')
        
        return args

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Submit job":
            self.update_presets()

            submit_action = self._file.submit_blender_playblast_job
            submit_action.revision_name.set(self.revision_name.get())
            submit_action.resolution_percentage.set(self.resolution_percentage.get())
            submit_action.use_simplify.set(self.use_simplify.get())
            submit_action.reduce_textures.set(self.reduce_textures.get())
            submit_action.target_texture_width.set(self.target_texture_width.get())
            
            return self.get_result(
                next_action=submit_action.oid()
            )
        
        self.update_presets()

        revision_name = self.revision_name.get()
        playblast_path, playblast_name, path_format = self.playblast_infos_from_revision(
            revision_name
        )

        # Get or create playblast file
        if not self._files.has_file(playblast_name, "mov"):
            tm = self.root().project().get_task_manager()
            df = next((
                file_data for file_name, file_data in tm.get_task_files(self._task.name()).items()
                if file_data[0] == f'{playblast_name}.mov'), None
            )
            playblast_file = self._files.add_file(
                name=playblast_name,
                extension="mov",
                base_name=self._file.complete_name.get() + "_movie",
                tracked=True,
                default_path_format=path_format if df is None else df[1]
            )
            playblast_file.file_type.set('Outputs')
        else:
            playblast_file = self._files[playblast_name + "_mov"]
        
        playblast_file.source_file.set(self._file.oid())
        
        # Get or add playblast revision
        if playblast_file.has_revision(revision_name):
            playblast_revision = playblast_file.get_revision(
                revision_name
            )
        else:
            source_revision = self._file.get_revision(revision_name)
            playblast_revision = playblast_file.add_revision(
                name=revision_name,
                comment=source_revision.comment.get()
            )
        
        # Configure playblast revision
        playblast_revision.set_sync_status("Available")

        # Store revision path as playblast output path
        self.output_path = playblast_revision.get_path().replace("\\", "/")
        
        # Ensure playblast revision folder exists and is empty
        if not os.path.exists(self.output_path):
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        else:
            os.remove(self.output_path)

        result = GenericRunAction.run(self, button)
        self._files.touch()
        return result


class SubmitBlenderPlayblastJob(flow.Action):
    
    _file = flow.Parent()
    
    pool = flow.Param('default', SiteJobsPoolNames)
    priority = flow.SessionParam(10).ui(editor='int')
    
    revision_name = flow.Param().ui(hidden=True)
    resolution_percentage = flow.Param().ui(hidden=True)
    use_simplify = flow.Param().ui(hidden=True)
    reduce_textures = flow.Param().ui(hidden=True)
    target_texture_width = flow.Param().ui(hidden=True)
    
    def get_buttons(self):
        self.message.set('<h2>Submit playblast to pool</h2>')
        self.pool.apply_preset()
        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _get_job_label(self):
        label = f'Render playblast - {self._file.oid()}'
        return label
    
    def run(self, button):
        if button == 'Cancel':
            return

        # Update pool preset
        self.pool.update_preset()

        job = self._file.jobs.create_job(job_type=PlayblastJob)
        job.revision.set(self.revision_name.get())
        job.resolution_percentage.set(self.resolution_percentage.get())
        job.use_simplify.set(self.use_simplify.get())
        job.reduce_textures.set(self.reduce_textures.get())
        job.target_texture_width.set(self.target_texture_width.get())
        site_name = self.root().project().get_current_site().name()        

        job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=self.priority.get(),
            label=self._get_job_label(),
            creator=self.root().project().get_user_name(),
            owner=self.root().project().get_user_name(),
            paused=False,
            show_console=False,
        )


class PublishAndRenderPlayblast(flow.Action):

    _file = flow.Parent()

    comment = flow.SessionParam('', PresetSessionValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(
        tooltip='Delete your working copy after publication if disabled',
        editor='bool'
    )
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def needs_dialog(self):
        self.check_default_values()
        self.message.set("<h2>Publish</h2>")
        return True

    def allow_context(self, context):
        return context and self._file.publish_action.allow_context(context)
    
    def check_default_values(self):
        self.comment.apply_preset()
        self.keep_editing.apply_preset()
        self.upload_after_publish.check_default_value()
    
    def update_presets(self):
        self.comment.update_preset()
        self.keep_editing.update_preset()
    
    def get_buttons(self):
        return ['Publish and render playblast', 'Cancel']
    
    def _configure_and_render(self, revision_name):
        '''
        May be overriden by subclasses to configure and launch playblast rendering
        of the revision `revision_name` of the selected file.
        '''
        pass

    def run(self, button):
        if button == 'Cancel':
            return
        
        project_settings = self.root().project().settings()
        if self.comment.get() == "" and not project_settings.optional_publish_comment.get():
            self.message.set(
                "<h2>Publish</h2>"
                "Please enter a comment to describe your changes.")
            return self.get_result(close=False)
        
        # Update parameter presets
        self.update_presets()
        
        # Publish
        publish_action = self._file.publish_action
        publish_action.publish_file(
            self._file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get(),
            upload_after_publish=self.upload_after_publish.get()
        )
        
        # Playblast
        ret = self._configure_and_render(self._file.get_head_revision().name())

        return ret


class PublishAndRenderBlenderPlayblast(PublishAndRenderPlayblast):

    ICON = ('icons.libreflow', 'publish-blender')

    render_blender_playblast = flow.Label('<h2>Playblast</h2>')
    quality = flow.Param('Final', PlayblastQuality)
    render_in_pool = flow.SessionParam(False, PresetSessionValue).ui(
        tooltip='Submit playblast rendering in a job pool',
        editor='bool'
    )

    with flow.group('Advanced'):
        use_simplify = flow.SessionParam(False, PresetSessionValue).ui(
            tooltip='Use low-definition rigs',
            editor='bool'
        )

    def allow_context(self, context):
        allow_context = super(PublishAndRenderBlenderPlayblast, self).allow_context(context)
        return allow_context and self._file.render_blender_playblast.allow_context(context)

    def check_default_values(self):
        super(PublishAndRenderBlenderPlayblast, self).check_default_values()
        self.use_simplify.apply_preset()
        self.render_in_pool.apply_preset()
    
    def update_presets(self):
        super(PublishAndRenderBlenderPlayblast, self).update_presets()
        self.use_simplify.update_preset()
        self.render_in_pool.update_preset()

    def _configure_and_render(self, revision_name):
        self._file.render_blender_playblast.revision_name.set(revision_name)
        self._file.render_blender_playblast.quality.set(self.quality.get())
        self._file.render_blender_playblast.use_simplify.set(self.use_simplify.get())
        render_button = 'Submit job' if self.render_in_pool.get() else 'Render'
        
        return self._file.render_blender_playblast.run(render_button)


class AERenderSettings(flow.values.SessionValue):
    DEFAULT_EDITOR = 'choice'

    _action = flow.Parent()

    def choices(self):
        rs = self.root().project().get_current_site().ae_render_settings_templates.get() or {}
        return list(rs)
    
    def revert_to_default(self):
        rs = self.choices()
        self.set(rs[0] if rs else None)


class AEOutputModule(flow.values.SessionValue):
    DEFAULT_EDITOR = 'choice'

    _action = flow.Parent()

    def choices(self):
        om = self.root().project().get_current_site().ae_output_module_templates.get() or {}
        return list(om)
    
    def revert_to_default(self):
        om = self.choices()
        self.set(om[0] if om else None)


class PlayblastOutputModuleChoiceValue(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    _action = flow.Parent()

    def choices(self):
        om = self.root().project().get_current_site().ae_output_module_templates.get() or {}
        return list(om)
    
    def revert_to_default(self):
        values = self.root().project().get_action_value_store().get_action_values(
            self._action.name(), {self.name(): self.get()}
        )
        value = values[self.name()]

        # Reset to value set in project action value store
        if value in self.choices():
            self.set(value)
        else:
            om = self.root().project().get_current_site().ae_output_module_templates.get() or {}
            if om:
                self.set(om.keys[0])


class PublishAndRenderAEPlayblast(PublishAndRenderPlayblast):

    ICON = ('icons.libreflow', 'publish-ae')
    
    with flow.group('Playblast advanced settings'):
        render_settings = flow.SessionParam(None, AERenderSettings)
        output_module = flow.SessionParam(None, AEOutputModule)
        start_frame = flow.IntParam()
        end_frame = flow.IntParam()
        render_in_pool = flow.SessionParam(False, PresetSessionValue).ui(
            tooltip='Submit playblast rendering in a job pool',
            editor='bool'
        )

    def needs_dialog(self):
        self.render_settings.revert_to_default()
        self.output_module.revert_to_default()
        self.start_frame.revert_to_default()
        self.end_frame.revert_to_default()
        return super(PublishAndRenderAEPlayblast, self).needs_dialog()

    def allow_context(self, context):
        allow_context = super(PublishAndRenderAEPlayblast, self).allow_context(context)
        return allow_context and self._file.select_ae_playblast_render_mode.allow_context(context)
    
    def check_default_values(self):
        super(PublishAndRenderAEPlayblast, self).check_default_values()
        self.render_in_pool.apply_preset()
    
    def update_presets(self):
        super(PublishAndRenderAEPlayblast, self).update_presets()
        self.render_in_pool.update_preset()

    def _configure_and_render(self, revision_name):
        render_select_mode = self._file.select_ae_playblast_render_mode
        render_select_mode.revision.set(revision_name)
        render_select_mode.render_settings.set(self.render_settings.get())
        render_select_mode.output_module.set(self.output_module.get())
        render_select_mode.start_frame.set(self.start_frame.get())
        render_select_mode.end_frame.set(self.end_frame.get()) 
        if self.render_in_pool.get():
            render_button = 'Submit job'
        else:
            render_button = 'Render'
        
        return render_select_mode.run(render_button)


class FileRevisionNameChoiceValue(flow.values.ChoiceValue):

    STRICT_CHOICES = False
    action = flow.Parent()

    def get_file(self):
        return self.action._file

    def choices(self):
        if self.get_file() is None:
            return []
        
        return self.get_file().get_revision_names(
            sync_status='Available',
            published_only=True
        )
    
    def revert_to_default(self):
        source_file = self.get_file()
        
        if not source_file:
            self.set(None)
            return
        
        revision = source_file.get_head_revision(sync_status="Available")
        self.set(revision.name() if revision else None)


class FileRevisionWorkingCopyNameChoiceValue(FileRevisionNameChoiceValue):

    def choices(self):
        user = self.root().project().get_user()

        if user.preferences.create_working_copies.get() == True:
            if self.get_file() is None:
                return []
            
            revisions = self.get_file().get_revision_names(
                sync_status='Available',
            )

            for revision in revisions:
                if revision == self.root().project().get_user_name():
                    revisions.remove(revision)
            
            return revisions
        else:
            return super(FileRevisionWorkingCopyNameChoiceValue, self).choices()


class KitsuShotTaskType(PresetChoiceValue):

    DEFAULT_EDITOR = 'choice'
    _file = flow.Parent(2)
    
    def choices(self):
        site = self.root().project().get_current_site()

        if site.is_kitsu_admin.get():
            # Return shot types if current site is 
            kitsu_api = self.root().project().kitsu_api()
            return kitsu_api.get_task_types('Shot')
        else:
            kitsu_bindings = self.root().project().kitsu_bindings()
            return kitsu_bindings.get_task_types(self._file.oid())

    def revert_to_default(self):
        kitsu_bindings = self.root().project().kitsu_bindings()
        choices = kitsu_bindings.get_task_types(self._file.oid())
        
        if choices:
            default_value = choices[0]
        else:
            default_value = ''
        
        self.set(default_value)


class UploadPlayblastToKitsu(flow.Action):
    
    ICON = ('icons.libreflow', 'kitsu')
    
    _file = flow.Parent()
    _shot       = flow.Parent(5)
    _sequence   = flow.Parent(7)
    
    revision_name = flow.Param(None, FileRevisionNameChoiceValue)
    kitsu_settings = flow.Label('<h3>Kitsu settings</h3>').ui(icon=('icons.libreflow', 'kitsu'))
    current_task_status = flow.Computed().ui(hidden=True)
    target_task_type = flow.Param(None, KitsuShotTaskType).watched().ui(label="Task Type")
    target_task_status = flow.Param('Work In Progress', KitsuTaskStatus).ui(label="Task Status")
    comment = flow.SessionParam('', PresetSessionValue).ui(editor='textarea')
    
    def __init__(self, parent, name):
        super(UploadPlayblastToKitsu, self).__init__(parent, name)
        self._kitsu_entity = None
    
    def _ensure_kitsu_entity(self):
        if self._kitsu_entity is None:
            kitsu_bindings = self.root().project().kitsu_bindings()
            kitsu_config = self.root().project().kitsu_config()
            file_settings = get_contextual_dict(self._file, 'settings')

            # Handle Kitsu Episodes (tvshow project) if necessary
            if kitsu_config.project_type.get() == 'tvshow':
                if file_settings.get('shot', None) is not None:
                    file_settings['entity_type'] = 'shot'
                    file_settings['episode'] = file_settings.get('film')
                elif file_settings.get('asset', None) is not None:
                    file_settings['entity_type'] = 'asset'
            
            entity_data = kitsu_bindings.get_entity_data(file_settings)
            self._kitsu_entity = kitsu_bindings.get_kitsu_entity(entity_data)
        
        return self._kitsu_entity
    
    def allow_context(self, context):
        kitsu_config = self.root().project().kitsu_config()
        return (
            context
            and not self._file.is_empty(on_current_site=True, published_only=True)
            and kitsu_config.configured.get()
            and kitsu_config.is_uploadable(self._file.display_name.get())
        )
    
    def check_default_values(self):
        self.revision_name.revert_to_default()
        self.target_task_type.apply_preset()
        self.target_task_status.apply_preset()
        self.comment.apply_preset()
    
    def update_presets(self):
        self.target_task_type.update_preset()
        self.target_task_status.update_preset()
        self.comment.update_preset()
    
    def get_buttons(self):
        return ['Upload', 'Cancel']
    
    def needs_dialog(self):
        self.check_default_values()
        return True
    
    def _check_kitsu_params(self):
        # Check if the file is linked to a Kitsu entity
        task_type = self.target_task_type.get()
        kitsu_entity = self._ensure_kitsu_entity()
        
        msg = "<h2>Upload playblast to Kitsu</h2>"
        
        if kitsu_entity is None or task_type is None:
            msg += (
                "<h3><font color=#FF584D>The Kitsu entity %s belongs to "
                "couldn't be detected. Please contact the "
                "support on the chat.</font></h3>" % self._file.display_name.get()
            )
            self.message.set(msg)
            return False
        
        # Check if current user is assigned to a Kitsu task this file is made for
        kitsu_api = self.root().project().kitsu_api()
        user = kitsu_api.get_user()
        task = kitsu_api.get_task(kitsu_entity, task_type)
        
        if user is None:
            msg += (
                "<h3><font color=#FF584D>It seems you (%s) have no "
                "user profile on Kitsu. Please contact the "
                "support on the chat.</font></h3>" % self.root().project().get_user_name()
            )
            self.message.set(msg)
            return False
        
        if task is None:
            msg += (
                "<h3><font color=#FF584D>This file is not linked to any "
                "task on Kitsu.</font></h3>"
            )
            self.message.set(msg)
            return False
        
        # Check if user is assigned to the task or have sufficient rights
        is_assigned = kitsu_api.user_is_assigned(user, task)
        user_role = user.get('role', None)
        
        if not is_assigned:
            if not user_role in ['admin', 'manager']:
                msg += (
                    "<h3><font color=#FF584D>You (%s) are not assigned to "
                    "the task this file has been created for.</font></h3>"
                    % self.root().project().get_user_name()
                )
                self.message.set(msg)
                return False
            else:
                user_roles = {
                    'admin': 'studio manager',
                    'manager': 'supervisor'
                }
                msg += (
                    "<h3>As %s, you can upload a preview for this file.</h3>"
                    % user_roles[user_role]
                )

        #Check is the number of frames in the file is the same as the shot was set on Kitsu
        site_env = self.root().project().get_current_site().site_environment
        if site_env.has_mapped_name('FFPROBE_EXEC_PATH'):
            exec_path = site_env['FFPROBE_EXEC_PATH'].value.get()

            check_frames = subprocess.check_output(
                f'{exec_path} -v quiet -show_streams -select_streams v:0 -of json "{self._file.get_revision(self.revision_name.get()).get_path()}"',
                shell=True).decode()

            fields = json.loads(check_frames)['streams'][0]
            frames = int(fields['nb_frames'])

            sequence_data = kitsu_api.get_sequence_data(self._sequence.name())
            shot_data = kitsu_api.get_shot_data(self._shot.name(),sequence_data)

            if shot_data['nb_frames'] is not None :

                if frames < shot_data['nb_frames']:

                    msg = f'<font color=red><b>Revision has {shot_data["nb_frames"]-frames} missing frames (expected : {shot_data["nb_frames"]})</font></b>'
                    self.message.set(msg)
                    return False

        self.message.set(msg)
        
        return True

    def child_value_changed(self, child_value):
        if child_value is self.target_task_type:
            self._check_kitsu_params()
            self.current_task_status.touch()
    
    def compute_child_value(self, child_value):
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            child_value.set(None)
            return
        
        kitsu_api = self.root().project().kitsu_api()
        
        if child_value is self.current_task_status:
            task_status = kitsu_api.get_task_current_status(
                kitsu_entity,
                self.target_task_type.get()
            )
            self.current_task_status.set(task_status)
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self.update_presets()

        if not self._check_kitsu_params():
            return self.get_result(close=False)
        
        kitsu_api = self.root().project().kitsu_api()
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            self.root().session().log_error('No Kitsu entity for file ' + self._file.oid())
            return self.get_result(close=False)
        
        revision = self._file.get_revision(self.revision_name.get())
        if self._file.source_file.get() is not None :
            source_file = self.root().get_object(self._file.source_file.get())
            source_file_revision = source_file.get_revision(self.revision_name.get())

        task_status_data = kitsu_api.get_task_status(short_name=self.target_task_status.names_dict[self.target_task_status.get()])

        success = kitsu_api.upload_preview(
            kitsu_entity=kitsu_entity,
            task_type_name=self.target_task_type.get(),
            task_status_name=task_status_data['name'],
            file_path=revision.get_path(),
            comment=self.comment.get(),
        )
        
        if not success:
            self.message.set((
                "<h2>Upload playblast to Kitsu</h2>"
                "<font color=#FF584D>An error occured "
                "while uploading the preview.</font>"
            ))
            return self.get_result(close=False)
        
        revision.set_status('on_kitsu')
        if self._file.source_file.get() is not None :
            source_file_revision.set_status('on_kitsu')

        if self.root().project().get_current_site().auto_upload_kitsu_playblasts.get():
            revision.upload.run('Confirm')

class UploadPNGToKitsu(UploadPlayblastToKitsu):
    '''
    Export a PNG file from a Photoshop scene and upload it to Kitsu.
    '''

    ICON = ('icons.libreflow', 'kitsu')
    
    _file = flow.Parent()
    _shot       = flow.Parent(5)
    _sequence   = flow.Parent(7)
    
    revision_name = flow.Param(None, FileRevisionNameChoiceValue)
    kitsu_settings = flow.Label('<h3>Kitsu settings</h3>').ui(icon=('icons.libreflow', 'kitsu'))
    current_task_status = flow.Computed().ui(hidden=True)
    target_task_type = flow.Param(None, KitsuShotTaskType).watched().ui(label="Task Type")
    target_task_status = flow.Param('Work In Progress', KitsuTaskStatus).ui(label="Task Status")
    comment = flow.SessionParam('', PresetSessionValue).ui(editor='textarea')

    def __init__(self, parent, name):
        super(UploadPNGToKitsu, self).__init__(parent, name)
        self._kitsu_entity = None

    def allow_context(self, context):
        kitsu_config = self.root().project().kitsu_config()
        return (
            context
            and not self._file.is_empty(on_current_site=True, published_only=True)
            and kitsu_config.configured.get()
            # and kitsu_config.is_uploadable(self._file.display_name.get())
            and self._file.format.get() in ['psd','psb','png','jpg']
        )
    
    def _check_kitsu_params(self):
        # Check if the file is linked to a Kitsu entity
        task_type = self.target_task_type.get()
        kitsu_entity = self._ensure_kitsu_entity()
        
        msg = "<h2>Upload Image to Kitsu<</h2>"
        
        if kitsu_entity is None or task_type is None:
            msg += (
                "<h3><font color=#FF584D>The Kitsu entity %s belongs to "
                "couldn't be detected. Please contact the "
                "support on the chat.</font></h3>" % self._file.display_name.get()
            )
            self.message.set(msg)
            return False
        
        # Check if current user is assigned to a Kitsu task this file is made for
        kitsu_api = self.root().project().kitsu_api()
        user = kitsu_api.get_user()
        task = kitsu_api.get_task(kitsu_entity, task_type)
        
        if user is None:
            msg += (
                "<h3><font color=#FF584D>It seems you (%s) have no "
                "user profile on Kitsu. Please contact the "
                "support on the chat.</font></h3>" % self.root().project().get_user_name()
            )
            self.message.set(msg)
            return False
        
        if task is None:
            msg += (
                "<h3><font color=#FF584D>This file is not linked to any "
                "task on Kitsu.</font></h3>"
            )
            self.message.set(msg)
            return False
        
        # Check if user is assigned to the task or have sufficient rights
        is_assigned = kitsu_api.user_is_assigned(user, task)
        user_role = user.get('role', None)
        
        if not is_assigned:
            if not user_role in ['admin', 'manager']:
                msg += (
                    "<h3><font color=#FF584D>You (%s) are not assigned to "
                    "the task this file has been created for.</font></h3>"
                    % self.root().project().get_user_name()
                )
                self.message.set(msg)
                return False
            else:
                user_roles = {
                    'admin': 'studio manager',
                    'manager': 'supervisor'
                }
                msg += (
                    "<h3>As %s, you can upload a preview for this file.</h3>"
                    % user_roles[user_role]
                )
        self.message.set(msg)
        return True

    def run(self, button):
        if button == 'Cancel':
            return

        # Convert to png

        rev = self._file.get_revision(self.revision_name.get())
        path = rev.get_path()

        input_path = path + '[0]'

        print('INPUT_PATH = ' + input_path)
        
        output_path = os.path.splitext(path)[0] + '.png'

        print('OUPUT PATH = ' + output_path)

        convert_args = ['magick']
        convert_args += ['%s' %input_path]
        convert_args += ['%s' %output_path]

        process = subprocess.run(convert_args, check=False, shell=True)

        print(f"COMMAND:\n{' '.join(process.args)}")
        print(f"STDERR: {repr(process.stderr)}")
        print(f'STDOUT: {process.stdout}')
        print(f'RETURN CODE: {process.returncode}')

        if process.returncode != 0:

            self.root().session().log_warning('Conversion failed with "magick", fallback to "convert".')

            convert_args = ['convert']
            convert_args += ['%s' %input_path]
            convert_args += ['%s' %output_path]

            process = subprocess.run(convert_args, check=True, shell=True)
        
        if not os.path.exists(output_path):
            self.message.set((
                "<h2>Upload playblast to Kitsu</h2>"
                "<font color=#FF584D>File conversion failed</font>"
            ))
            return self.get_result(close=False)


        # Upload to Kitsu
        
        self.update_presets()

        if not self._check_kitsu_params():
            self.root().session().log_error('KITSU PARAM ERROR')
            return self.get_result(close=False)
        
        kitsu_api = self.root().project().kitsu_api()
        kitsu_entity = self._ensure_kitsu_entity()
        
        if kitsu_entity is None:
            self.root().session().log_error('No Kitsu entity for file ' + self._file.oid())
            return self.get_result(close=False)

        if self._file.source_file.get() is not None :
            source_file = self.root().get_object(self._file.source_file.get())
            source_file_revision = source_file.get_revision(self.revision_name.get())

        task_status_data = kitsu_api.get_task_status(short_name=self.target_task_status.names_dict[self.target_task_status.get()])

        success = kitsu_api.upload_preview(
            kitsu_entity=kitsu_entity,
            task_type_name=self.target_task_type.get(),
            task_status_name=task_status_data['name'],
            file_path=output_path,
            comment=self.comment.get(),
        )
        
        if not success:
            self.message.set((
                "<h2>Upload playblast to Kitsu</h2>"
                "<font color=#FF584D>An error occured "
                "while uploading the preview.</font>"
            ))
            return self.get_result(close=False)
        
        rev.set_status('on_kitsu')
        

        






class RenderWithAfterEffect(GenericRunAction):
    
    ICON = ('icons.libreflow', 'afterfx')

    def get_buttons(self):
        return ["Render", "Cancel"]

    def runner_name_and_tags(self):
        return "AfterEffectsRender", []

    @classmethod
    def supported_extensions(cls):
        return ["aep"]
    
    def allow_context(self, context):
        return (
            context
            and self._file.format.get() in self.supported_extensions()
        )


class WaitProcess(LaunchSessionWorker):
    '''
    Launch a `SessionWorker` which waits for the processes identified
    by the ID `pids` to end. It is up to the user of this action to set
    the latter param using `add_wait_pid()` before the action runs.
    
    Since a `SessionWorker` runs in its own session, params of this class
    and its subclasses must be stored in the DB in order to remain
    accessible to the underlying subprocess.
    '''
    pids = flow.OrderedStringSetParam()
    
    def allow_context(self, context):
        return False
    
    def launcher_oid(self):
        return self.oid()
    
    def launcher_exec_func_name(self):
        return 'wait'
    
    def wait_pid(self, pid):
        self.pids.add(pid, self.pids.len())
    
    def wait(self, *args, **kwargs):
        while self.pids.len() > 0:
            time.sleep(1.0)

            for pid in self.pids.get():
                if not psutil.pid_exists(int(pid)):
                    self.pids.remove(pid)
        
        self._do_after_process_ends(*args, **kwargs)
    
    def _do_after_process_ends(self, *args, **kwargs):
        '''
        Subclasses may redefine this method to perform a particular
        processing after the subprocess ending.
        '''
        pass


class ZipFolder(WaitProcess):
    
    folder_path = flow.Param()
    output_path = flow.Param()
    
    def allow_context(self, context):
        return False
    
    def get_run_label(self):
        return 'Zip rendered images'
    
    def _do_after_process_ends(self, *args, **kwargs):
        folder_path = self.folder_path.get()
        output_path = self.output_path.get()
        
        if os.path.exists(folder_path):
            zip_folder(self.folder_path.get(), self.output_path.get())


class RenderImageSequence(RenderWithAfterEffect):

    revision        = flow.SessionParam()
    render_settings = flow.SessionParam()
    output_module   = flow.SessionParam()
    output_name     = flow.SessionParam()
    output_path     = flow.SessionParam()
    start_frame     = flow.IntParam()
    end_frame     = flow.IntParam()
    overwrite_folder = flow.BoolParam().ui(hidden=True)

    _files = flow.Parent(2)

    def needs_dialog(self):
        return True

    def allow_context(self, context):
        return False
    
    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Cancel']
    
    def get_run_label(self):
        return 'Render image sequence'
    
    def get_comp_name(self, default_pattern=None):

        def _get_name(pattern, settings):
            comp_name = None
            kwords = keywords_from_format(pattern)
            values = {kw: settings.get(kw, None) for kw in kwords}

            if all([v is not None for v in values.values()]):
                comp_name = pattern.format(**values)
            
            return comp_name
        
        settings = get_contextual_dict(self, 'settings')
        comp_name = None

        if default_pattern is not None:
            comp_name = _get_name(default_pattern, settings)
        else:
            for pattern in self.root().project().get_current_site().ae_comp_name_patterns.get():
                comp_name = _get_name(pattern, settings)

                if comp_name is not None:
                    break
        
        return comp_name

    def extra_argv(self):
        settings = get_contextual_dict(self._file, 'settings')
        revision = self._file.get_revision(self.revision.get())
        project_path = revision.get_path()


        asset_name = settings.get('asset')
        sequence_name = settings.get('sequence')
        shot_name = settings.get('shot')
        comp_name = self.get_comp_name()

        if asset_name is not None:
            output_name = asset_name
        elif sequence_name is not None and shot_name is not None:
            output_name = sequence_name + '_' + shot_name
        else:
            output_name = 'render'
        
        if self.output_name.get() is not None:
            output_name = self.output_name.get().format(
                comp_name=comp_name, sequence=sequence_name, shot=shot_name, asset=asset_name, revision=revision.name())
        else:
            output_name = comp_name + '.[####].exr'
        
        output_path = os.path.join(self._output_path, output_name)
        site = self.root().project().get_current_site()
        
        argv = [
            '-project', project_path,
            '-comp', comp_name,
            '-RStemplate', self.render_settings.get(),
            '-OMtemplate', self.output_module.get(),
            '-output', output_path
        ]

        if self.start_frame.get() is not None :
            argv += '-s',self.start_frame.get()

        if self.end_frame.get() is not None :
            argv += '-e',self.end_frame.get()
        
        return argv
    
    def ensure_render_folder(self):
        folder_name = self._file.display_name.get().split('.')[0]
        folder_name += '_render'

        if not self._files.has_folder(folder_name):
            self._files.create_folder_action.folder_name.set(folder_name)
            self._files.create_folder_action.tracked.set(True)
            self._files.create_folder_action.run(None)
        
        return self._files[folder_name]
    
    def ensure_render_folder_revision(self):
        folder = self.ensure_render_folder()
        revision_name = self.revision.get()
        revisions = folder.get_revisions()
        source_revision = self._file.get_revision(self.revision.get())
        
        if not folder.has_revision(revision_name):
            revision = folder.add_revision(revision_name)
            folder.set_current_user_on_revision(revision_name)
        else:
            revision = folder.get_revision(revision_name)
        
        revision.comment.set(source_revision.comment.get())
        
        folder.ensure_last_revision_oid()
        
        self._files.touch()
        
        return revision
    
    def run(self, button):
        if button == 'Cancel':
            return

        if self.output_path.get() is not None:
            settings = get_contextual_dict(self._file, 'settings')
            sequence_name = settings['sequence']
            shot_name = settings.get('shot', None)
            revision = self._file.get_revision(self.revision.get())
            self._output_path = self.output_path.get().format(sequence=sequence_name, shot=shot_name, revision=revision.name())

            # Ensure playblast revision folder exists and is empty
            if not os.path.exists(self._output_path):
                os.makedirs(self._output_path)
            elif self.overwrite_folder.get() is True :
                remove_folder_content(self._output_path)
        else:
            revision = self.ensure_render_folder_revision()
            self._output_path = revision.get_path()
            
            # Ensure playblast revision folder exists and is empty
            if not os.path.exists(self._output_path):
                os.makedirs(self._output_path)
            elif self.overwrite_folder.get() is True :
                remove_folder_content(self._output_path)

        return super(RenderImageSequence, self).run(button)


class ExportAEAudio(RenderWithAfterEffect):

    _files = flow.Parent(2)
    revision = flow.Param(None, FileRevisionNameChoiceValue)
    output_module = flow.SessionParam()
    audio_path = flow.Param(None)

    def get_run_label(self):
        return 'Export audio'
    
    def allow_context(self, context):
        return False

    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Export', 'Cancel']

    def extra_argv(self):
        project_path = self._file.get_revision(self.revision.get()).get_path()
        comp_name = self.get_comp_name()
        output_path = os.path.join(
            os.path.dirname(project_path),
            f'{comp_name}.wav'
        )
        
        argv = [
            '-project', project_path,
            '-comp', comp_name,
            '-OMtemplate', self.output_module.get(),
            '-output', output_path
        ]

        self.audio_path.set(output_path)
        
        return argv
    
    def get_audio_path(self):
        return self.audio_path.get()
        
    def get_comp_name(self, default_pattern=None):

        def _get_name(pattern, settings):
            comp_name = None
            kwords = keywords_from_format(pattern)
            values = {kw: settings.get(kw, None) for kw in kwords}

            if all([v is not None for v in values]):
                comp_name = pattern.format(**values)
            
            return comp_name
        
        settings = get_contextual_dict(self, 'settings')
        comp_name = None

        if default_pattern is not None:
            comp_name = _get_name(default_pattern, settings)
        else:
            for pattern in self.root().project().get_current_site().ae_comp_name_patterns.get():
                comp_name = _get_name(pattern, settings)

                if comp_name is not None:
                    break
        
        return comp_name
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        return super(ExportAEAudio, self).run(button)


class MarkImageSequence(GenericRunAction):
    
    _folder = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    
    revision = flow.Param(None, FileRevisionNameChoiceValue)
    
    def runner_name_and_tags(self):
        return 'MarkSequenceRunner', []
    
    def get_version(self, button):
        return None
    
    def get_run_label(self):
        return 'Generate playblast'
    
    def allow_context(self, context):
        return context and len(self._folder.get_revision_names(sync_status='Available')) > 0
    
    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Cancel']
    
    def extra_argv(self):
        argv = super(MarkImageSequence, self).extra_argv()
        
        settings = get_contextual_dict(self, 'settings')
        sequence = settings.get('sequence', None)
        
        if sequence is None:
            sequence = 0
        else:
            sequence = list_digits(sequence)[0]
        
        argv += [
            '-o', self._extra_argv['video_output'],
            '-t', resources.get('mark_sequence.fields', 'default.json'),
            '--project', settings.get('film', 'undefined'),
            '--sequence', sequence,
            '--scene', settings.get('shot', 'undefined'),
            '--version', self.revision.get(),
            '--studio', self.root().project().get_current_site().name(),
            '--file-name', self._extra_argv['file_name'],
            '--frame_rate', settings.get('frame_rate', 24.0),
            self._extra_argv['image_path']
        ]
        
        audio_path = self._extra_argv['audio_file']
        
        if audio_path is not None and os.path.exists(audio_path):
            argv += ['--audio-file', audio_path]
        
        return argv

    def _ensure_file_revision(self, name, revision_name):
        mng = self.root().project().get_task_manager()
        default_files = mng.get_task_files(self._task.name())

        # Find matching default file
        match_dft_file = False
        for file_mapped_name, file_data in default_files.items():
            # Get only files
            if '.' in file_data[0]:
                base_name, extension = os.path.splitext(file_data[0])
                if name == base_name:
                    extension = extension[1:]
                    path_format = file_data[1]
                    match_dft_file = True
                    break
        
        # Fallback to default mov container
        if match_dft_file is False:
            extension = 'mov'
            path_format = mng.get_task_path_format(self._task.name()) # get from default task
        
        mapped_name = name + '_' + extension
        
        if not self._files.has_mapped_name(mapped_name):
            file = self._files.add_file(
                name, extension, tracked=True,
                default_path_format=path_format
            )
        else:
            file = self._files[mapped_name]
        
        if not file.has_revision(revision_name):
            revision = file.add_revision(revision_name)
            file.set_current_user_on_revision(revision_name)
        else:
            revision = file.get_revision(revision_name)
        
        file.file_type.set('Outputs')
        file.ensure_last_revision_oid()
        
        return revision
    
    def _get_first_image_path(self, revision_name):
        revision = self._folder.get_revision(revision_name)
        img_folder_path = revision.get_path()
        
        for f in os.listdir(img_folder_path):
            file_path = os.path.join(img_folder_path, f)
            file_type = mimetypes.guess_type(file_path)[0].split('/')[0]
            
            if file_type == 'image':
                return file_path
        
        return None
    
    def _get_audio_path(self):
        if any("_aep" in file for file in self._files.mapped_names()):
            scene_name = self._folder.name().replace('_render', '_aep')
        else : 
            scene_name = re.search(r"(.+?(?=_render))", self._folder.name()).group()
            
        if not self._files.has_mapped_name(scene_name):
            # Scene not found
            return None
            
        return self._files[scene_name].export_ae_audio.get_audio_path()

    def mark_sequence(self, revision_name):
        # Compute playblast prefix
        prefix = self._folder.name()
        prefix = prefix.replace('_render', '')
        
        source_revision = self._file.get_revision(revision_name)
        revision = self._ensure_file_revision(prefix + '_movie', revision_name)
        revision.comment.set(source_revision.comment.get())
        
        # Get the path of the first image in folder
        img_path = self._get_first_image_path(revision_name)
        
        # Get original file name to print on frames
        if self._files.has_mapped_name(prefix + '_aep'):
            scene = self._files[prefix + '_aep']
            file_name = scene.complete_name.get() + '.' + scene.format.get()
        else:
            file_name = self._folder.complete_name.get()
        
        self._extra_argv = {
            'image_path': img_path,
            'video_output': revision.get_path(),
            'file_name': file_name,
            'audio_file': self._get_audio_path()
        }
        
        return super(MarkImageSequence, self).run('Render')
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        return self.mark_sequence(self.revision.get())


class MarkImageSequenceWaiting(WaitProcess):

    _file = flow.Parent()
    _files = flow.Parent(2)
    
    folder_name = flow.Param()
    revision_name = flow.Param()

    def get_run_label(self):
        return 'Mark image sequence'

    def launcher_exec_func_kwargs(self):
        return dict(
            folder_name=self.folder_name.get(),
            revision_name=self.revision_name.get()
        )

    def _do_after_process_ends(self, *args, **kwargs):
        # Mark image sequence in provided folder
        self.root().project().ensure_runners_loaded()
        sequence_folder = self._files[kwargs['folder_name']]
        sequence_folder.mark_image_sequence.revision.set(kwargs['revision_name'])
        ret = sequence_folder.mark_image_sequence.mark_sequence(kwargs['revision_name'])
        rid = ret['runner_id']
        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)

        print('[PLAYBLAST] Marking started...')
        print('[PLAYBLAST] Command: %s' % runner_info['command'])

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        if runner_info['handlers_catch'] is None:
            print('[PLAYBLAST] Marking finished !')


class RenderImageSequenceJob(FileJob):

    _file = flow.Parent(2)
    revision_name = flow.Param()
    render_settings = flow.Param()
    output_module = flow.Param()
    output_name = flow.Param()
    output_path = flow.Param()
    start_frame = flow.IntParam()
    end_frame = flow.IntParam()
    overwrite_folder = flow.BoolParam()

    def _do_job(self):
        revision_name = self.revision_name.get()
        render_image_seq = self._file.render_image_sequence
        render_image_seq.revision.set(revision_name)
        render_image_seq.render_settings.set(self.render_settings.get())
        render_image_seq.output_module.set(self.output_module.get())
        render_image_seq.output_name.set(self.output_name.get())
        render_image_seq.output_path.set(self.output_path.get())
        render_image_seq.start_frame.set(self.start_frame.get())
        render_image_seq.end_frame.set(self.end_frame.get())
        render_image_seq.overwrite_folder.set(self.overwrite_folder.get())
        ret = render_image_seq.run('Render')
        rid = ret['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s started...' % rid)
        self.show_message('[RUNNER] Description: %s - %s %s' % (runner_info['label'], self._file.oid(), revision_name))
        self.show_message('[RUNNER] Command: %s' % runner_info['command'])

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s finished' % rid)


class ExportAudioJob(FileJob):

    revision_name = flow.Param()
    output_module = flow.Param()

    def _do_job(self):
        revision_name = self.revision_name.get()
        export_audio = self._file.export_ae_audio
        export_audio.revision.set(revision_name)
        export_audio.output_module.set(self.output_module.get())

        ret = export_audio.run('Export')
        rid = ret['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s started...' % rid)
        self.show_message('[RUNNER] Description: %s - %s %s' % (runner_info['label'], self._file.oid(), revision_name))
        self.show_message('[RUNNER] Command: %s' % runner_info['command'])

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s finished' % rid)


class MarkImageSequenceJob(FileJob):

    _folder = flow.Parent(2)
    revision_name = flow.Param()

    def _do_job(self):
        revision_name = self.revision_name.get()
        mark_image_seq = self._folder.mark_image_sequence
        mark_image_seq.revision.set(revision_name)
        ret = mark_image_seq.run('Render')
        rid = ret['runner_id']

        runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s started...' % rid)
        self.show_message('[RUNNER] Description: %s - %s %s' % (runner_info['label'], self._file.oid(), revision_name))
        self.show_message('[RUNNER] Command: %s' % runner_info['command'])

        while runner_info['is_running']:
            time.sleep(1)
            runner_info = self.root().session().cmds.SubprocessManager.get_runner_info(rid)
        
        self.show_message('[RUNNER] Runner %s finished' % rid)


class RenderAEPlayblast(flow.Action):

    ICON = ('icons.libreflow', 'afterfx')

    _file = flow.Parent()
    revision = flow.Param(None, FileRevisionNameChoiceValue)
    render_settings = flow.SessionParam()
    output_module = flow.SessionParam()
    audio_output_module = flow.SessionParam()
    start_frame = flow.IntParam()
    end_frame = flow.IntParam()

    def get_buttons(self):
        self.revision.revert_to_default()
        return ['Render', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def _render_image_sequence(self, revision_name, render_settings, output_module, start_frame, end_frame):
        render_image_seq = self._file.render_image_sequence
        render_image_seq.revision.set(revision_name)
        render_image_seq.render_settings.set(render_settings)
        render_image_seq.output_module.set(output_module)
        render_image_seq.start_frame.set(start_frame)
        render_image_seq.end_frame.set(end_frame)
        ret = render_image_seq.run('Render')

        return ret
    
    def _export_audio(self, revision_name, output_module):
        export_audio = self._file.export_ae_audio
        export_audio.revision.set(revision_name)
        export_audio.output_module.set(output_module)
        ret = export_audio.run('Export')

        return ret
    
    def _mark_image_sequence(self, folder_name, revision_name, render_pid, export_audio_pid):
        mark_sequence_wait = self._file.mark_image_sequence_wait
        mark_sequence_wait.folder_name.set(folder_name)
        mark_sequence_wait.revision_name.set(revision_name)
        mark_sequence_wait.wait_pid(render_pid)
        mark_sequence_wait.wait_pid(export_audio_pid)
        mark_sequence_wait.run(None)
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        revision_name = self.revision.get()
        
        # Render image sequence
        ret = self._render_image_sequence(
            revision_name,
            self.render_settings.get(),
            self.output_module.get(),
            self.start_frame.get(),
            self.end_frame.get(),
        )
        render_runner = self.root().session().cmds.SubprocessManager.get_runner_info(
            ret['runner_id']
        )
        # Export audio
        ret = self._export_audio(
            revision_name,
            self.audio_output_module.get()
        )
        export_audio_runner = self.root().session().cmds.SubprocessManager.get_runner_info(
            ret['runner_id']
        )
        # Configure image sequence marking
        folder_name = self._file.name()[:-len(self._file.format.get())]
        folder_name += 'render'
        self._mark_image_sequence(
            folder_name,
            revision_name,
            render_pid=render_runner['pid'],
            export_audio_pid=export_audio_runner['pid']
        )

class SelectAEPlayblastRenderModePage2(flow.Action):

    _file = flow.Parent()

    def allow_context(self,context):
        return context and context.endswith('.details')
    
    def get_buttons(self):
        self.message.set('Do you want to keep the existing frames out of frame range?')
        return ['Yes' , 'No']
    
    def run(self,button):
        render_action = self._file.render_ae_playblast
        render_img_seq = self._file.render_image_sequence

        render_img_seq.overwrite_folder.set(True if button == 'No' else False)
        render_action.run('Render')
        return

class SubmitRenderAEPlayblast(flow.Action):

    ICON = ('icons.libreflow', 'afterfx')

    pool = flow.Param('default', SiteJobsPoolNames)
    revision = flow.SessionParam().ui(hidden=True)
    render_settings = flow.SessionParam().ui(hidden=True)
    output_module = flow.SessionParam().ui(hidden=True)
    audio_output_module = flow.SessionParam().ui(hidden=True)
    start_frame = flow.IntParam().ui(hidden=True)
    end_frame = flow.IntParam().ui(hidden=True)
    overwrite_folder = flow.BoolParam().ui(hidden=True)

    _file  = flow.Parent()
    _files = flow.Parent(2)

    def get_buttons(self):
        self.pool.apply_preset()

        return ['Submit', 'Cancel']
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self.pool.update_preset()
        revision_name = self.revision.get()

        # Create render folder and movie
        aep_name = self._file.name().replace('_aep', '')
        render_folder = self._ensure_file(aep_name+'_render')
        mov_file = self._ensure_file(aep_name+'_movie.mov')
        self._ensure_revision(render_folder, revision_name)
        self._ensure_revision(mov_file, revision_name)

        # Create rendering job
        render_job = self._file.jobs.create_job(job_type=RenderImageSequenceJob)
        render_job.revision_name.set(revision_name)
        render_job.render_settings.set(self.render_settings.get())
        render_job.output_module.set(self.output_module.get())
        render_job.start_frame.set(self.start_frame.get())
        render_job.end_frame.set(self.end_frame.get())
        render_job.overwrite_folder.set(self.overwrite_folder.get())

        # Create audio export job
        export_audio_job = self._file.jobs.create_job(job_type=ExportAudioJob)
        export_audio_job.revision_name.set(revision_name)
        export_audio_job.output_module.set(self.audio_output_module.get())

        # Create marking job
        mark_job = render_folder.jobs.create_job(job_type=MarkImageSequenceJob)
        mark_job.revision_name.set(revision_name)

        site_name = self.root().project().admin.multisites.current_site_name.get()
        user_name = self.root().project().get_user_name()

        render_job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=10,
            label='Render image sequence - %s (%s)' % (self._file.oid(), revision_name),
            creator=user_name,
            owner=user_name,
            paused=True,
            show_console=False,
        )

        export_audio_job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=10,
            label='Export audio - %s (%s)' % (self._file.oid(), revision_name),
            creator=user_name,
            owner=user_name,
            paused=True,
            show_console=False,
        )

        mark_job.submit(
            pool=site_name + '_' + self.pool.get(),
            priority=10,
            label='Mark image sequence - %s (%s)' % (self._file.oid(), revision_name),
            creator=user_name,
            owner=user_name,
            paused=True,
            show_console=False,
        )

        # Configure marking job to resume when rendering and audio export jobs finish
        LinkedJob.link_jobs(render_job, mark_job)
        LinkedJob.link_jobs(export_audio_job, mark_job)

        # Resume render and audio jobs
        self.root().session().cmds.Jobs.set_job_paused(render_job.job_id.get(), False)
        self.root().session().cmds.Jobs.set_job_paused(export_audio_job.job_id.get(), False)
    
    def _ensure_file(self, file_name):
        mapped_name = file_name.replace('.', '_')
        f = None
        
        if not self._files.has_mapped_name(mapped_name):
            name, ext = os.path.splitext(file_name)
            if ext:
                f = self._files.add_file(name, ext[1:], tracked=True)
            else:
                f = self._files.add_folder(name, tracked=True)
        else:
            f = self._files[mapped_name]

        return f
    
    def _ensure_revision(self, file, revision_name):
        if not file.has_revision(revision_name):
            r = file.add_revision(revision_name)
            file.set_current_user_on_revision(revision_name)
        else:
            r = file.get_revision(revision_name)
        
        file.ensure_last_revision_oid()
        
        return r
        
class SubmitRenderAEPlayblastPage0(flow.Action):

    _file = flow.Parent()

    def allow_context(self,context):
        return context and context.endswith('.details')
    
    def get_buttons(self):
        self.message.set('Do you want to keep the existing frames out of frame range?')
        return ['Yes' , 'No']
    
    def run(self,button):
        submit_action = self._file.submit_ae_playblast

        submit_action.overwrite_folder.set(True if button == 'No' else False)
        return self.get_result(next_action=submit_action.oid())
        return

class SelectAEPlayblastRenderMode(flow.Action):
    '''
    This action needs the current site's AfterEffects
    templates to be configured as follow:
    
    - at least one render settings template
    - at least one output module template named `default`
    '''

    ICON = ('icons.libreflow', 'afterfx')

    _file = flow.Parent()
    _file_list = flow.Parent(2)
    revision = flow.Param(None, FileRevisionNameChoiceValue)

    with flow.group('Advanced settings'):
        render_settings = flow.SessionParam(None, AERenderSettings)
        output_module = flow.SessionParam(None, AEOutputModule)
        start_frame = flow.IntParam()
        end_frame = flow.IntParam()

    _buttons = flow.SessionParam()

    def get_buttons(self):
        return self._buttons.get()
    
    def needs_dialog(self):
        self.revision.revert_to_default()
        self.render_settings.revert_to_default()
        self.output_module.revert_to_default()
        self.start_frame.revert_to_default()
        self.end_frame.revert_to_default()

        actions = [
            self._file.render_image_sequence,
            self._file.export_ae_audio,
            self._file.mark_image_sequence_wait
        ]
        msg = None
        for a in actions:
            msg = a.runner_configured()
            if msg is not None:
                name, _ = a.runner_name_and_tags()
                error_txt = '<div style="color: red">Error:</div>'
                self.root().session().log_error(msg)
                self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                    f'Application {name} not configured (see terminal).'))
                self._buttons.set(['Cancel'])
                break
        if self.render_settings.get() is None or self.output_module.get() is None:
            msg = ('At least one render settings template and '
                'one output module template must be defined in '
                'the current site settings.\n\n')
            self.root().session().log_error(msg)
            error_txt = '<div style="color: red">Error:</div>'
            self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                f'Application AfterEffects not configured (see terminal).'))
            self._buttons.set(['Cancel'])
        
        if msg is None:
            self.revision.revert_to_default()
            self.render_settings.revert_to_default()
            self.output_module.revert_to_default()
            self.start_frame.revert_to_default()
            self.end_frame.revert_to_default()
            self.message.set('')
            buttons = ['Render', 'Cancel']
            if self.root().project().get_current_site().site_type.get() == 'Studio' and self.root().project().get_current_site().pool_names.get():
                buttons.insert(1, 'Submit job')
            self._buttons.set(buttons)
        
        return True
    
    def allow_context(self, context):
        site = self.root().project().get_current_site()
        return (
            context
            and self._file.format.get() == 'aep'
            and site.ae_render_settings_templates.get()
            and site.ae_output_module_templates.get()
            and site.ae_output_module_audio.get()
            and self.start_frame.get()
            and self.end_frame.get()
            and not self._file.is_empty()
        )

    def _has_render_folder(self):
        if self._file_list.has_folder(self._file.complete_name.get() + '_render'):
            folder_rev = self._file_list[self._file.complete_name.get() + '_render'].get_revision(self.revision.get())
            if folder_rev is not None :
                folder_path = folder_rev.get_path()
                if os.path.exists(folder_path):
                    return True
        return False

    def run(self, button):
        if button == 'Cancel':
            return
        else:
            # Get AfterEffects templates configured in current site
            site = self.root().project().get_current_site()
            render_settings = (site.ae_render_settings_templates.get() or {}).get(
                self.render_settings.get()
            )
            output_module = (site.ae_output_module_templates.get() or {}).get(
                self.output_module.get()
            )
            audio_output_module = site.ae_output_module_audio.get()

            if button == 'Render':
                render_action = self._file.render_ae_playblast
                render_action.revision.set(self.revision.get())
                render_action.render_settings.set(render_settings)
                render_action.output_module.set(output_module)
                render_action.audio_output_module.set(audio_output_module)
                render_action.start_frame.set(self.start_frame.get())
                render_action.end_frame.set(self.end_frame.get())

                if (self.start_frame.get() is not None or self.end_frame.get() is not None) and self._has_render_folder():
                    return self.get_result(next_action=self._file.select_ae_playblast_render_mode_page2.oid())
                    
                render_action.run('Render')
            else:
                submit_action = self._file.submit_ae_playblast
                submit_action.revision.set(self.revision.get())
                submit_action.render_settings.set(render_settings)
                submit_action.output_module.set(output_module)
                submit_action.audio_output_module.set(audio_output_module)
                submit_action.start_frame.set(self.start_frame.get())
                submit_action.end_frame.set(self.end_frame.get())

                if (self.start_frame.get() is not None or self.end_frame.get() is not None) and self._has_render_folder():
                    return self.get_result(next_action=self._file.submit_ae_playblast_page0.oid())

                return self.get_result(next_action=submit_action.oid())


class PlaySequenceAction(flow.Action):

    ICON = ('icons.gui', 'chevron-sign-to-right')

    _file = flow.Parent()
    _sequence = flow.Parent(7)

    @classmethod
    def supported_extensions(cls):
        return ["mp4","mov"]

    def allow_context(self, context):
        return (
            context 
            and self._file.format.get() in self.supported_extensions()
        )
    
    def needs_dialog(self):
        self._sequence.play_sequence.filler_type.revert_to_default()
        self._sequence.play_sequence.duration_seconds.revert_to_default()
        self._sequence.play_sequence.priority_files.revert_to_default()
        self._sequence.play_sequence.status = self._sequence.play_sequence.get_files()

        if (
            self._sequence.play_sequence.status == 'Nothing' or
            self._sequence.play_sequence.filler_type.get() == ''
        ):
            return True
        
        return False

    def get_buttons(self):
        if self._sequence.play_sequence.status == 'Nothing':
            self.message.set('<h2>No files has been found.</h2>\nCheck if parameter are correctly setted in Action Value Store.')
        elif self._sequence.play_sequence.filler_type.get() == '':
            self.message.set('<h2>Incorrect filler type.</h2>\nCheck if parameter are correctly setted in Action Value Store.')
        return ['Close']
    
    def run(self, button):
        if button == 'Close':
            return None
        
        return self.get_result(goto_target=self._sequence.play_sequence.run('Open'))


class SetPrimaryFile(flow.Action):

    ICON = ('icons.gui', 'tag-black-shape')

    _file = flow.Parent()
    _task = flow.Parent(3)

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        return context

    def run(self, button):
        task_manager = self.root().project().get_task_manager()
        default_tasks = task_manager.default_tasks

        if default_tasks.has_mapped_name(self._task.name()):
            dt = default_tasks[self._task.name()]
            if dt.files.edits.has_mapped_name(self._file.name()):
                df = dt.files.edits[self._file.name()]
                self.root().session().log_info('[Set Primary File Action] Default File found')
                
                new_state = False if df.is_primary_file.get() else True
                df.is_primary_file.set(new_state)
                self._file.is_primary_file.set(new_state)
                
                status_name = 'added' if new_state else 'removed'
                self.root().session().log_info(f'[Set Primary File Action] Status {status_name}')
                
                dt.files.edits.touch()
                dt.files.touch()
            else:
                self._file.is_primary_file.set(False if self._file.is_primary_file.get() else True)

                status_name = 'added' if self._file.is_primary_file.get() else 'removed'
                self.root().session().log_info(f'[Set Primary File Action] Status {status_name}')


class RequestTrackedFileAction(flow.Action):

    _file = flow.Parent()
    _files = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def allow_context(self, context):
        return False
    
    def run(self, button):
        head = self._file.get_head_revision()
        exchange_site_name = self.root().project().get_exchange_site().name()

        if not head or head.get_sync_status() != "NotAvailable" or head.get_sync_status(site_name=exchange_site_name) != "Available":
            return
        
        head.request.sites.target_site.set(
            self.root().project().get_current_site().name()
        )
        head.request.run(None)
        self._files.touch()


class TrackedFile(File):

    ICON = ("icons.gui", "text-file-1")

    _map = flow.Parent()
    _task = flow.Parent(2)
    
    locked_by = Property().ui(editable=False)

    history = flow.Child(History)
    source_file = flow.Param().ui(editable=False)
    current_revision = flow.Param("").ui(editable=False)
    last_revision_oid = Property().ui(editable=False)

    active_users = flow.Child(ActiveUsers)
    current_user_sees = flow.Computed()
    file_user_status = flow.Computed()

    jobs = flow.Child(FileJobs)

    show_history = flow.Child(GotoHistory)
    publish_action = flow.Child(PublishFileAction).injectable().ui(label="Publish", dialog_size=(525, 425))
    publish_and_playblast_blender = flow.Child(PublishAndRenderBlenderPlayblast).ui(label='Publish and playblast')
    publish_and_playblast_ae = flow.Child(PublishAndRenderAEPlayblast).ui(label='Publish and playblast')
    create_working_copy_action = flow.Child(CreateWorkingCopyAction).injectable().ui(
        label="Create working copy"
    )
    open = flow.Child(OpenTrackedFileAction)
    reveal = flow.Child(RevealFileInExplorer).ui(label="Reveal in explorer")
    request = flow.Child(RequestTrackedFileAction)
    upload_playblast = flow.Child(UploadPlayblastToKitsu).ui(label='Upload to Kitsu', dialog_size=(600, 510)).injectable()
    upload_image = flow.Child(UploadPNGToKitsu).ui(label='Upload to Kitsu', dialog_size=(600, 510))

    # Blender
    render_blender_playblast = flow.Child(RenderBlenderPlayblast).ui(label='Render playblast')
    submit_blender_playblast_job = flow.Child(SubmitBlenderPlayblastJob)

    # AfterEffects
    select_ae_playblast_render_mode = flow.Child(SelectAEPlayblastRenderMode).ui(label='Render playblast')
    select_ae_playblast_render_mode_page2 = flow.Child(SelectAEPlayblastRenderModePage2).ui(hidden=True)

    # with flow.group("Advanced"):
    create_working_copy_from_file = flow.Child(None).ui(label="Create working copy from another file", dialog_size=(841, 400))
    publish_into_file = flow.Child(None).ui(label="Publish to another file", dialog_size=(550, 450))
    play_sequence = flow.Child(PlaySequenceAction).ui(hidden=True)
    set_primary_file = flow.Child(SetPrimaryFile).ui(label='Set as primary file')

    # Options hidden by default
    render_ae_playblast = flow.Child(RenderAEPlayblast)
    render_image_sequence = flow.Child(RenderImageSequence).ui(label='Render image sequence')
    export_ae_audio     = flow.Child(ExportAEAudio).ui(label='Export audio')
    mark_image_sequence_wait = flow.Child(MarkImageSequenceWaiting)
    submit_ae_playblast = flow.Child(SubmitRenderAEPlayblast)
    submit_ae_playblast_page0 = flow.Child(SubmitRenderAEPlayblastPage0)

    # Order in which actions are displayed on the UI
    action_display_order = Property()
    visible_action_count = Property()

    def get_name(self):
        return "%s_%s" % (self.complete_name.get(), self.format.get())

    def get_source_display(self, oid):
        split = oid.split('/')
        split[-1] = self.display_name.get()
        indices = list(range(len(split) - 1, 2, -2))
        return ' – '.join([split[i] for i in reversed(indices)])
    
    def get_default_path(self):
        return os.path.join(
            self._map.get_parent_path(), self.name()
        )

    def ensure_file_data(self):
        task_manager = self.root().project().get_task_manager()
        default_tasks = task_manager.default_tasks

        file_type = None
        primary_file = None
        if default_tasks.has_mapped_name(self._task.name()):
            df = default_tasks[self._task.name()]
            if df.files.has_mapped_name(self.name()):
                file_type = df.files[self.name()].file_type.get()
                primary_file = df.files[self.name()].is_primary_file.get()

        self.file_type.set(file_type)
        self.is_primary_file.set(primary_file)

    def create(self):
        os.makedirs(self.get_path())

    def remove(self):
        shutil.rmtree(self.get_path())
    
    def configure(self, format, complete_name, display_name, path_format):
        super(TrackedFile, self).configure(format, complete_name, display_name, path_format)
        self.locked_by.set(None)
        self.last_revision_oid.set(None)
        self.ensure_file_data()

    def is_locked(self, by_current_user=False):
        lock_enabled = self.root().project().admin.project_settings.enable_file_lock.get()
        user_name = self.root().project().get_user_name()

        return (
            lock_enabled
            and (
                not by_current_user and self.locked_by.get() is not None
                or self.locked_by.get() == user_name
            )
        )

    def lock(self):
        self.locked_by.set(self.root().project().get_user_name())

    def unlock(self):
        self.locked_by.set(None)

    def has_working_copy(self, from_current_user=False, sync_status=None):
        if from_current_user:
            rev = self.get_revision(self.root().project().get_user_name())
            return rev is not None and (sync_status is None or rev.get_sync_status() == sync_status)

        for revision in self.get_revisions().mapped_items():
            if revision.is_working_copy() and (sync_status is None or revision.get_sync_status() == sync_status):
                return True

        return False

    def set_current_user_on_revision(self, revision_name):
        current_user = self.root().project().get_user_name()
        self.set_user_on_revision(current_user, revision_name)

    def set_user_on_revision(self, user_name, revision_name):
        if self.has_active_user(user_name):
            active_user = self.active_users[user_name]
        else:
            active_user = self.active_users.add(user_name)

        active_user.set(revision_name)
        self.get_revisions().touch()

    def remove_active_user(self, user_name):
        self.active_users.remove(user_name)

    def has_active_user(self, user_name):
        return user_name in self.active_users.mapped_names()

    def get_seen_revision(self):
        name = self.current_user_sees.get()

        if name == "current":
            if self.has_current_revision():
                return self.get_current_revision()
            else:
                return None
        else:
            return self.get_revision(name)

    def has_current_revision(self):
        return bool(self.current_revision.get())

    def get_revision(self, name):
        r = None
        if self.history.revisions.has_mapped_name(name):
            r = self.history.revisions[name]
        
        return r

    def get_revisions(self):
        return self.history.revisions
    
    def get_revision_oids(self):
        '''
        Returns the revision oids sorted by date of creation.
        '''
        return [r.oid() for r in sorted(self.get_revisions().mapped_items(), key=lambda r: -r.date.get())]
    
    def get_working_copies(self, sync_status=None):
        working_copies = []
        
        for r in self.get_revisions().mapped_items():
            if not r.is_working_copy() or r.is_working_copy(from_current_user=True):
                continue
            
            if sync_status is None or r.get_sync_status() == sync_status:
                working_copies.append(r)
        
        return working_copies
    
    def get_revision_names(self, sync_status=None, published_only=False):
        if sync_status is None and not published_only:
            return self.get_revisions().mapped_names()

        revisions = self.get_revisions().mapped_items()

        if published_only:
            revisions = filter(lambda r: not r.is_working_copy(), revisions)

        if sync_status is not None:
            revisions = filter(lambda r: r.get_sync_status() == sync_status, revisions)
        
        return [r.name() for r in revisions]
    
    def get_revision_statuses(self, published_only=False):
        revisions = self.get_revisions().mapped_items()
        
        if published_only:
            revisions = filter(lambda r: not r.is_working_copy(), revisions)
        
        return [(r.name(), r.get_sync_status()) for r in revisions]

    def has_revision(self, name, sync_status=None):
        exists = (name in self.history.revisions.mapped_names())

        if exists and sync_status:
            exists = exists and (self.history.revisions[name].get_sync_status() == sync_status)
        
        return exists

    def is_empty(self, on_current_site=True, published_only=False):
        revisions = self.get_revisions()
        empty = not bool(revisions.mapped_names())
        
        if not on_current_site:
            return empty
        
        for r in revisions.mapped_items():
            if published_only and r.is_working_copy():
                continue
            if r.get_sync_status() == 'Available':
                return False
        
        return True

    def get_last_edit_time(self):
        seen_name = self.current_user_sees.get()
        current = self.get_current_revision()

        if seen_name == "current":
            if current is None:
                if os.path.exists(self.get_path()):
                    return os.path.getmtime(self.get_path())
                else:
                    return 0
            else:
                return current.get_last_edit_time()
        else:
            seen = self.get_revision(seen_name)
            return seen.get_last_edit_time()

    def get_last_comment(self):
        seen_name = self.current_user_sees.get()
        current = self.get_current_revision()

        if seen_name == "current":
            if current is None:
                return "NO PUBLISH YET"
            else:
                return current.comment.get()
        else:
            seen = self.get_revision(seen_name)

            if seen.is_working_copy():
                return "WORKING COPY (%s)" % seen.user.get()
            else:
                return seen.comment.get()
    
    def add_revision(self, name=None, is_working_copy=False, comment="", ready_for_sync=True, path_format=None, from_revision=None, init_status=None):
        if path_format is None:
            path_format = self.path_format.get() or None
        
        r = self.get_revisions().add(
            name, is_working_copy, comment, ready_for_sync, path_format, from_revision, init_status
        )
        self.ensure_last_revision_oid()

        return r
    
    def ensure_last_revision_oid(self):
        last_revision_oid = self.last_revision_oid.get()

        if last_revision_oid is None:
            last_revision = self.get_head_revision()
            if last_revision is not None:
                self.last_revision_oid.set(last_revision.oid())
        else:
            last_revision = self.get_head_revision()
            if last_revision is not None and last_revision.oid() != last_revision_oid:
                self.last_revision_oid.set(last_revision.oid())

    def create_working_copy(self, from_revision=None, source_path=None, user_name=None, path_format=None):
        if user_name is None:
            user_name = self.root().project().get_user_name()

        revisions = self.get_revisions()
        working_copy = self.get_working_copy()

        # Overwrite current working copy
        if working_copy is not None:
            if working_copy.exists():
                os.remove(working_copy.get_path())

            revisions.remove(working_copy.name())
        
        working_copy = self.add_revision(
            user_name,
            is_working_copy=True,
            ready_for_sync=False,
            path_format=path_format
        )
        # Ensure parent folder exists
        os.makedirs(
            os.path.dirname(working_copy.get_path()),
            exist_ok=True
        )

        if source_path is None:
            source_path = self.get_template_path()

            if from_revision is not None:
                reference = self.get_revision(from_revision)

                if reference is None or reference.get_sync_status() != 'Available':
                    self.root().session().log_error(
                        f'Revision {from_revision} undefined or unavailable '
                        'on the current site. The created working copy will be empty.'
                    )
                else:
                    source_path = reference.get_path()
                    working_copy.source.set(reference.name())

        shutil.copy2(source_path, working_copy.get_path())

        if os.path.exists(working_copy.get_path()):
            working_copy.file_size.set(os.path.getsize(working_copy.get_path()))

        revisions.touch()
        self._map.touch()

        return working_copy

    def publish(self, revision_name=None, source_path=None, comment="", keep_editing=False, ready_for_sync=True, path_format=None):
        revisions = self.get_revisions()

        head_revision = self.add_revision(
            revision_name,
            ready_for_sync=ready_for_sync,
            comment=comment,
            path_format=path_format
        )

        # Ensure parent folder exists
        os.makedirs(
            os.path.dirname(head_revision.get_path()),
            exist_ok=True
        )

        # If source path is given, ignore working copy
        if source_path is not None:
            if os.path.exists(source_path):
                shutil.copy2(source_path, head_revision.get_path())
            else:
                self.root().session().log_error(
                    f'Source file {source_path} does not exist.'
                )
        else:
            working_copy = self.get_working_copy()
            head_revision.source.set(working_copy.source.get())

            if keep_editing:
                shutil.copy2(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
                working_copy.source.set(head_revision.name())
                working_copy.date.set(head_revision.date.get() + 1)
            else:
                shutil.move(
                    working_copy.get_path(),
                    head_revision.get_path()
                )

                #wc_dir_path = re.match(f'.*?{working_copy.name()}', working_copy.get_path())
                #if wc_dir_path is not None:
                #    wc_dir_path = wc_dir_path.group(0)
                #    shutil.rmtree(wc_dir_path)

                revisions.remove(working_copy.name())
        
        if os.path.exists(head_revision.get_path()):
            head_revision.file_size.set(os.path.getsize(head_revision.get_path()))

        # Compute published revision hash
        head_revision.compute_hash_action.run(None)
        self.last_revision_oid.set(head_revision.oid())

        revisions.touch()
        self._map.touch()

        return head_revision

    def make_current(self, revision):
        self.current_revision.set(revision.name())
        self.get_revisions().touch()

    def get_working_copy(self, user_name=None):
        if user_name is None:
            user_name = self.root().project().get_user_name()
        try:
            return self.get_revision(user_name)
        except flow.exceptions.MappedNameError:
            return None

    def get_head_revision(self, sync_status=None):
        revisions = self.get_revisions()

        for revision in reversed(revisions.mapped_items()):
            if not revision.is_working_copy() and (not sync_status or revision.get_sync_status() == sync_status):
                return revision

        return None

    def get_current_revision(self):
        try:
            return self.get_revision(self.current_revision.get())
        except flow.exceptions.MappedNameError:
            return None
    
    def to_upload_after_publish(self):
        auto_upload_files = self.root().project().admin.project_settings.get_auto_upload_files()

        for pattern in auto_upload_files:
            if fnmatch.fnmatch(self.display_name.get(), pattern):
                return True
        
        return False
    
    def ensure_file_user_status(self):
        status = None

        user_wc = self.get_working_copy()
        if user_wc:
            status = "latest"          

            head_revision = self.get_head_revision()
            if head_revision is not None and head_revision.date.get() > user_wc.date.get():
                status = "old"
            elif self.get_working_copies():
                status = "warning"
        
        return status
    
    def compute_child_value(self, child_value):
        current_user = self.root().project().get_user_name()

        if child_value is self.current_user_sees:
            try:
                child_value.set(self.active_users[current_user].get())
            except flow.exceptions.MappedNameError:
                child_value.set("current")
        elif child_value is self.file_user_status:
            child_value.set(self.ensure_file_user_status())
        else:
            super(TrackedFile, self).compute_child_value(child_value)
    
    def get_icon(self, extension=None):
        if extension is None:
            extension = self.format.get() or None
        
        return super(TrackedFile, self).get_icon(extension)
    
    def activate_oid(self):
        return self.open.oid()


class FileRefRevisionNameChoiceValue(FileRevisionWorkingCopyNameChoiceValue):

    def get_file(self):
        return self.action.source_file.get()


class ResetRef(flow.Action):

    _ref = flow.Parent()

    def allow_context(self, context):
        return context and context.endswith(".inline")
    
    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._ref.set(None)
        return self.get_result(refresh=True)


class ResetableTrackedFileRef(flow.values.Ref):

    SOURCE_TYPE = TrackedFile
    reset = flow.Child(ResetRef)


class PublishIntoFile(PublishFileAction):

    source_file = flow.SessionParam("").ui(
        editable=False,
        tooltip="File to publish to.",
    )
    source_revision_name = flow.Param(None, FileRevisionNameChoiceValue).watched().ui(
        label="Source revision"
    )
    target_file = flow.Connection(ref_type=ResetableTrackedFileRef).watched()
    revision_name = flow.Param("").watched()
    comment = flow.Param("", PresetValue)
    keep_editing = flow.SessionParam(True, PresetSessionValue).ui(hidden=True)
    upload_after_publish = flow.Param(False, UploadAfterPublishValue).ui(editor='bool')

    def get_buttons(self):
        self.message.set("<h2>Publish from an existing file</h2>")
        self.target_file.set(None)
        self.source_file.set(self._file.display_name.get())
        self.source_revision_name.revert_to_default()

        self.check_default_values()

        return ["Publish", "Cancel"]

    def allow_context(self, context):
        return None

    def check_file(self, file):
        expected_format = self._file.format.get()
        msg = "<h2>Publish from an existing file</h2>"
        error_msg = ""

        if not file:
            error_msg = "A target file must be set."
        elif file.format.get() != expected_format:
            error_msg = f"Target file must be in {expected_format} format."
        elif not self.source_revision_name.choices():
            error_msg = f"Target file has no revision available on current site."
        
        if error_msg:
            self.message.set(
                f"{msg}<font color=#FF584D>{error_msg}</font>"
            )
            return False
        
        # Check if other users are editing the target file
        working_copies = file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>"+n+"</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "Target file <b>%s</b> is currently being edited by one or more users (%s)."
                "</font></h3>"
                % (file.display_name.get(), ', '.join(user_names))
            )
        
        self.message.set(msg)
        return True
    
    def check_revision_name(self, name):
        msg = self.message.get()
        target_file = self.target_file.get()

        if not self.check_file(target_file):
            return False

        if target_file.has_revision(name):
            msg += (
                "<font color=#FF584D>"
                f"Target file already has a revision {name}."
                "</font>"
            )
            self.message.set(msg)

            return False
        
        self.message.set(msg)
        return True
    
    def _target_file(self):
        return self.target_file.get()
    
    def _revision_to_process(self):
        revision_name = self.revision_name.get()
        if not revision_name:
            revision_name = self.source_revision_name.get()

        return self._target_file().get_revision(revision_name)

    def child_value_changed(self, child_value):
        self.message.set("<h2>Publish from an existing file</h2>")

        if child_value is self.target_file:
            self.check_file(self.target_file.get())
            self.check_revision_name(self.source_revision_name.get())
        elif child_value is self.source_revision_name:
            value = self.source_revision_name.get()
            self.revision_name.set(value)
            self.comment.set("Created from %s (%s)" % (
                self._file.display_name.get(),
                value,
            ))
        elif child_value is self.revision_name:
            revision_name = self.revision_name.get()
            self.check_revision_name(revision_name)

    def run(self, button):
        if button == "Cancel":
            return

        target_file = self.target_file.get()

        # Check source file
        if not self.check_file(target_file):
            return self.get_result(close=False)
        
        revision_name = self.revision_name.get()
        if not revision_name:
            revision_name = self.source_revision_name.get()
        
        # Check choosen revision name
        if not self.check_revision_name(revision_name):
            return self.get_result(close=False)
        
        source_revision_name = self.source_revision_name.get()
        source_revision = self._file.get_revision(source_revision_name)
        
        # Publish in target file
        target_file.lock()

        publication = target_file.publish(
            revision_name=revision_name,
            source_path=source_revision.get_path(),
            comment=self.comment.get(),
        )
        target_file.make_current(publication)
        target_file.unlock()
        target_file._map.touch()

        if self.upload_after_publish.get():
            super(PublishFileAction, self).run(None)


class CreateWorkingCopyFromFile(flow.Action):

    ICON = ('icons.libreflow', 'edit-blank')

    _file = flow.Parent()
    source_file = flow.Connection(ref_type=ResetableTrackedFileRef).watched()
    source_revision_name = flow.Param(None, FileRefRevisionNameChoiceValue).ui(
        label="Source revision"
    )
    target_file = flow.SessionParam("").ui(
        editable=False,
        tooltip="File in which the working copy will be created.",
    )

    def get_buttons(self):
        msg = "<h2>Create working copy from another file</h2>"
        self.source_file.set(None)
        self.target_file.set(self._file.display_name.get())

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#FFA34D>"
                "You already have a working copy on %s. "
                "Creating a working copy will overwrite the current one."
                "</font><br>" % self._file.display_name.get()
            )
        else:
            msg += "<br>"
        
        self.message.set(msg)

        return ["Create", "Cancel"]

    def allow_context(self, context):
        return context and self._file.editable()
    
    def child_value_changed(self, child_value):
        if child_value is self.source_file:
            self.check_file(self.source_file.get())

            self.source_revision_name.touch()
            self.source_revision_name.revert_to_default()

    def check_file(self, file):
        expected_format = self._file.format.get()
        msg = "<h2>Create working copy from another file</h2>"
        error_msg = ""

        if self._file.has_working_copy(from_current_user=True):
            msg += (
                "<font color=#FFA34D>"
                "You already have a working copy on %s. "
                "Creating a working copy will overwrite the current one."
                "</font><br>" % self._file.display_name.get()
            )
        else:
            msg += "<br>"

        if not file:
            error_msg = "A source file must be set."
        elif file.format.get() != expected_format:
            error_msg = f"Source file must be in {expected_format} format."
        elif not self.source_revision_name.choices():
            error_msg = f"Source file has no revision available on current site."
        
        if error_msg:
            self.message.set(
                f"{msg}<font color=#FF584D>{error_msg}</font>"
            )
            return False

        self.message.set(msg + "<br><br>")
        
        return True
    
    def run(self, button):
        if button == "Cancel":
            return

        source_file = self.source_file.get()

        if not self.check_file(source_file):
            return self.get_result(close=False)
        
        source_revision = source_file.get_revision(self.source_revision_name.get())
        working_copy = self._file.create_working_copy(source_path=source_revision.get_path())

        self._file.set_current_user_on_revision(working_copy.name())
        self._file.touch()
        self._file.get_revisions().touch()


TrackedFile.create_working_copy_from_file.set_related_type(CreateWorkingCopyFromFile)
TrackedFile.create_working_copy_from_file.injectable()
TrackedFile.publish_into_file.set_related_type(PublishIntoFile)


class ClearFileSystemMapAction(ClearMapAction):
    def run(self, button):
        for item in self._map.mapped_items():
            if hasattr(item, "state") and hasattr(item, "current_user_sees"):
                item.get_revisions().clear()
                item.current_revision.set("")
                item.active_users.clear()

        super(ClearFileSystemMapAction, self).run(button)


class Folder(FileSystemItem):

    open = flow.Child(RevealFileInExplorer).ui(icon=('icons.gui', 'open-folder'))

    def create(self):
        os.makedirs(self.get_path())

    def remove(self):
        shutil.rmtree(self.get_path())
    
    def get_icon(self, extension=None):
        return ('icons.gui', 'folder-white-shape')


class OpenTrackedFolderRevision(RevealInExplorer):

    _revision = flow.Parent()
    
    def allow_context(self, context):
        return context and self._revision.get_sync_status() == 'Available'
    
    def needs_dialog(self):
        ret = RevealInExplorer.needs_dialog(self)

        if not ret:
            available = self._revision.get_sync_status() == 'Available'
            exists = self._revision.exists()

            if not available:
                self.message.set((
                    '<h2>Unavailable revision</h2>'
                    'This revision is not available on the current site.'
                ))
            elif not exists:
                self.message.set((
                    '<h2>Missing revision</h2>'
                    'This revision does not exist on the current site.'
                ))
            ret = (not available or not exists)
        
        return ret
    
    def get_buttons(self):
        return ['Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        super(OpenTrackedFolderRevision, self).run(button)
    
    def get_target_path(self):
        return self._revision.get_path()


class TrackedFolderRevision(Revision):

    open = flow.Child(OpenTrackedFolderRevision)

    def _get_default_suffix(self):
        return self.name()
    
    def _compute_path(self, path_format):
        kwords = keywords_from_format(path_format)
        settings = get_contextual_dict(self, 'settings')
        values = {}
        for kword in kwords:
            values[kword] = settings.get(kword, '')
        
        return path_format.format(**values)
    
    def compute_hash(self):
        return hash_folder(self.get_path())


class TrackedFolderRevisions(Revisions):

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(TrackedFolderRevision)


class TrackedFolderHistory(History):

    revisions = flow.Child(TrackedFolderRevisions).injectable()


class OpenTrackedFolderAction(flow.Action):

    ICON = ('icons.gui', 'open-folder')

    revision = flow.Param(None, RevisionsChoiceValue)

    _buttons = flow.SessionParam(list)
    _to_open = flow.SessionParam()
    _folder = flow.Parent()
    _task = flow.Parent(3)
    
    def get_buttons(self):
        return self._buttons.get()
    
    def allow_context(self, context):
        return context

    def needs_dialog(self):
        name = 'DefaultEditor'
        needs_dialog = self.root().session().cmds.SubprocessManager.get_runner_versions(name) is None
        self._to_open.revert_to_default()

        if needs_dialog:
            error_txt = '<div style="color: red">Error:</div>'
            self.root().session().log_error((f'Runner \'{name}\' not found: make sure it is '
                'registered in the project runner factory.\n\n'))
            self.message.set((f'<h3 style="font-weight: 400">{error_txt} '
                f'Application {name} not configured (see terminal).'))
            self._buttons.set(['Cancel'])
        else:
            self.revision.revert_to_default()
            buttons = []
            default_file = self.root().project().get_task_manager().get_task_files(self._task.name()).get(
                self._folder.name()
            )
            auto_open = False

            if default_file is not None and default_file[10]: # open last revision at double-clic
                last_rev = self._folder.get_head_revision()
                if last_rev is not None:
                    self._to_open.set(last_rev.name())
                    auto_open = True

            if not auto_open: # fall back to default behavior
                if self._folder.editable():
                    if not self._folder.has_working_copy(from_current_user=True, sync_status='Available'):
                        if not self._folder.get_revision_names(sync_status='Available', published_only=True):
                            msg = ("<h3>Empty folder</h3>Start to edit this folder "
                            "by creating a working copy.")
                        else:
                            msg = ("<h3>Open/edit folder</h3>Select a published "
                            "revision to open, or create a working copy from it.")
                            buttons.append('Open revision')
                        
                        buttons.append('Create a working copy')
                        needs_dialog = True
                    else:
                        self._to_open.set(self._folder.get_working_copy().name())
                else:
                    needs_dialog = True
                    msg = "<h3>Read-only folder</h3>"

                    if self._folder.get_revision_names(sync_status='Available', published_only=True):
                        msg += "Select a revision to open."
                        buttons.append('Open revision')
                    else:
                        msg += "This file is empty."

            if needs_dialog:
                buttons.append('Cancel')
                self.message.set(msg)
                self._buttons.set(buttons)

        return needs_dialog
    
    def run(self, button):
        if button == 'Cancel':
            return
        elif button == 'Create a working copy':
            # Create and open new working copy
            if self._folder.editable() and not self._folder.has_working_copy(from_current_user=True, sync_status='Available'):
                working_copy = self._folder.create_working_copy(
                    from_revision=self.revision.get() if self.revision.get() else None)
                working_copy.open.run(None)
            else:
                self.root().session().log_error("\n\nCould not create a working "
                f"copy for user '{self.root().project().get_user_name()}': this "
                "folder is not editable, or a working copy already exists.\n\n")
                return
        elif button == 'Open revision':
            # Open selected revision
            if self._folder.get_revision_names(sync_status='Available', published_only=True):
                revision_name = self.revision.get()

                if revision_name not in self.revision.choices() or not self._folder.has_revision(revision_name):
                    self.root().session().log_error("\n\nCould not open published "
                    f"revision '{revision_name}': this revision does not exist.\n\n")
                    return
                
                revision = self._folder.get_revision(self.revision.get())
                revision.open.run(None)
            else:
                self.root().session().log_error("\n\nCould not open a revision: "
                "this folder is empty.\n\n")
                return
        elif self._to_open.get() is not None: # Working copy exists
            revision = self._folder.get_revision(self._to_open.get())
            revision.open.run(None)
        else:
            self.root().session().log_error("\n\nCould not run open action: "
            "this folder is either empty or not editable.\n\n")


class FolderAvailableRevisionName(FileRevisionNameChoiceValue):

    action = flow.Parent()

    def get_file(self):
        return self.action._folder


class ResizeTrackedFolderImages(RunAction):
    '''
    Computes half-resized versions of all PNG images contained in a source tracked folder
    in another tracked folder suffixed with `_half`.
    '''
    _folder = flow.Parent()
    _files = flow.Parent(2)
    revision_name = flow.Param(None, FolderAvailableRevisionName).watched()
    publish_comment = flow.SessionParam("")

    def allow_context(self, context):
        return context

    def runner_name_and_tags(self):
        return 'ImageMagick', []
    
    def get_run_label(self):
        return 'Resize images'
    
    def extra_argv(self):
        in_pattern = '{}/*.png[{}]'.format(self._source_folder_path, self._resize_format)
        out_pattern = '{}/%[filename:base].png'.format(self._target_folder_path)
        return ['convert', in_pattern, '-set', 'filename:base', '%[basename]', out_pattern]
    
    def get_buttons(self):
        self.message.set((
            "<h2>Resize images in {0}</h2>"
            "Every PNG image included in this folder will have a resized version placed in the <b>{0}_half</b> folder.".format(
                self._folder.name()
            )
        ))
        self.revision_name.revert_to_default()

        return ['Resize images', 'Cancel']
    
    def child_value_changed(self, child_value):
        if child_value is self.revision_name:
            self.publish_comment.set(
                "Half-resized images from %s folder" % self._folder.name()
            )
    
    def _get_image_dimensions(self, img_path):
        exec_path = self.root().project().admin.user_environment['IMAGEMAGICK_EXEC_PATH'].get()
        
        dims = subprocess.check_output([exec_path, 'convert', img_path, '-format', '%wx%h', 'info:'])
        dims = dims.decode('UTF-8').split('x')

        return tuple(map(int, dims))
    
    def run(self, button):
        if button == 'Cancel':
            return

        # Setup target folder
        target_folder_name = self._folder.name() + '_half'
        
        if not self._files.has_mapped_name(target_folder_name):
            self._files.create_folder.folder_name.set(target_folder_name)
            self._files.create_folder.run(None)
        
        target_folder = self._files[target_folder_name]
        publication = target_folder.publish(
            revision_name=self.revision_name.get(),
            source_path=self._folder.get_revision(self.revision_name.get()).path.get(),
            comment=self.publish_comment.get()
        )

        # Cache source and target folder paths
        self._source_folder_path = self._folder.get_revision(self.revision_name.get()).path.get()
        self._target_folder_path = publication.path.get()
        
        # Get dimensions of the first image
        image_paths = glob.glob("%s/*.png" % self._source_folder_path)
        width, height = self._get_image_dimensions(image_paths[0])

        # Cache dimensions
        if height > width:
            self._resize_format = "x%s" % min(int(0.5 * height), 3840)
        else:
            self._resize_format = "%sx" % min(int(0.5 * width), 3840)
        
        super(ResizeTrackedFolderImages, self).run(button)

        self._files.touch()


class TrackedFolder(TrackedFile):

    open = flow.Child(OpenTrackedFolderAction)
    history = flow.Child(TrackedFolderHistory)
    resize_images = flow.Child(ResizeTrackedFolderImages)
    # mark_image_sequence = flow.Child(MarkSequence).ui(group='Advanced')
    mark_image_sequence = flow.Child(MarkImageSequence).injectable().ui(
        label='Mark image sequence')
    # submit_mark_sequence_job = flow.Child(SubmitMarkSequenceJob).ui(group='Advanced', hidden=True)
    
    def get_name(self):
        return self.complete_name.get()
    
    def get_icon(self, extension=None):
        return ('icons.gui', 'folder-white-shape')
    
    def create_working_copy(self, from_revision=None, user_name=None, path_format=None):
        if user_name is None:
            user_name = self.root().project().get_user_name()

        revisions = self.get_revisions()
        working_copy = self.get_working_copy()

        # TODO: Don't use os.path.dirname
        # Required here since folders are identified as zip files for synchronisation
        if working_copy is not None:
            if working_copy.exists():
                shutil.rmtree(working_copy.get_path())
            
            revisions.remove(working_copy.name())
        
        working_copy = self.add_revision(
            user_name,
            is_working_copy=True,
            ready_for_sync=False,
            path_format=path_format
        )
        wc_dir_path = working_copy.get_path()

        # Ensure parent folder exists
        os.makedirs(
            os.path.dirname(wc_dir_path),
            exist_ok=True
        )

        if from_revision is not None:
            reference = self.get_revision(from_revision)

            if reference is None or reference.get_sync_status() != 'Available':
                self.root().session().log_error(
                    f'Revision {from_revision} undefined or unavailable '
                    'on the current site. The created working copy will be empty.'
                )
            else:
                shutil.copytree(
                    reference.get_path(), wc_dir_path
                )
                working_copy.source.set(reference.name())
        else:
            # Create an empty working copy folder
            os.mkdir(wc_dir_path)
        
        if os.path.exists(wc_dir_path):
            working_copy.file_size.set(os.path.getsize(wc_dir_path))

        revisions.touch()
        self._map.touch()

        return working_copy

    def publish(self, revision_name=None, source_path=None, comment="", keep_editing=False, ready_for_sync=True, path_format=None):
        revisions = self.get_revisions()

        head_revision = self.add_revision(
            revision_name,
            ready_for_sync=ready_for_sync,
            comment=comment,
            path_format=path_format
        )

        if source_path is not None:
            if os.path.exists(source_path):
                shutil.copytree(
                    source_path, head_revision.get_path()
                )
            else:
                self.root().session().log_error(
                    f'Source file {source_path} does not exist.'
                )
        else:
            working_copy = self.get_working_copy()
            head_revision.source.set(working_copy.source.get())
            
            if keep_editing:
                shutil.copytree(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
                working_copy.source.set(head_revision.name())
                working_copy.date.set(head_revision.date.get() + 1)
            else:
                shutil.move(
                    working_copy.get_path(),
                    head_revision.get_path()
                )
                
                #wc_dir_path = re.match(f'.*?{working_copy.name()}', working_copy.get_path())
                #if wc_dir_path is not None:
                #    wc_dir_path = wc_dir_path.group(0)
                #    shutil.rmtree(wc_dir_path)

                revisions.remove(working_copy.name())

        if os.path.exists(head_revision.get_path()):
            head_revision.file_size.set(os.path.getsize(head_revision.get_path()))

        # Compute published revision hash
        head_revision.compute_hash_action.run(None)
        self.last_revision_oid.set(head_revision.oid())

        revisions.touch()
        self._map.touch()

        return head_revision

    def make_current(self, revision):
        self.current_revision.set(revision.name())
        self.get_revisions().touch()
    
    def to_upload_after_publish(self):
        auto_upload_files = self.root().project().admin.project_settings.get_auto_upload_files()

        for pattern in auto_upload_files:
            if fnmatch.fnmatch(self.name(), pattern):
                return True
        
        return False

    def compute_child_value(self, child_value):
        if child_value is self.display_name:
            child_value.set(self.name())
        else:
            TrackedFile.compute_child_value(self, child_value)


mapping = {r.name: r.index for r in TrackedFile._relations}
for relation in TrackedFolder._relations:
    if relation.name in ["open", "history"]:
        relation.index = mapping.get(relation.name)
TrackedFolder._relations.sort(key=lambda r: r.index)


class FileFormat(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'
    STRICT_CHOICES = False

    def choices(self):
        return self.root().project().admin.default_applications.mapped_names()
    
    def revert_to_default(self):
        formats = self.choices()
        if formats:
            self.set(formats[0])


class FileCategory(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    def choices(self):
        return ['Inputs', 'Works', 'Outputs']


class CreateFileSystemItemAction(flow.Action):

    _task = flow.Parent(2)

    def allow_context(self, context):
        return context

    def get_buttons(self):
        self.message.set(self._title())
        return ['Create', 'Cancel']
    
    def _title(self):
        raise NotImplementedError()
    
    def _warn(self, message):
        self.message.set((
            f'{self._title()}'
            f'<font color=#FFA34D>{message}</font>'
        ))

    def get_path_format(self, file_name):
        '''
        Returns the path format defined in the task manager
        for the file with the given name.

        If the file is not a default file of the current
        task, the task path format is returned.
        '''
        path_format = None
        mng = self.root().project().get_task_manager()
        default_files = mng.get_task_files(self._task.name())
        
        if file_name in default_files:
            # get from default file
            path_format = default_files[file_name][1]
        else:
            # get from default task
            path_format = mng.get_task_path_format(self._task.name())
        
        return path_format


class CreateFileAction(CreateFileSystemItemAction):

    ICON = ('icons.gui', 'add-file')

    _files = flow.Parent()

    file_name   = flow.SessionParam('').ui(label='Name')
    file_format = flow.SessionParam(value_type=FileFormat).ui(label='Format', choice_icons=FILE_EXTENSION_ICONS)
    category    = flow.SessionParam('Works', value_type=FileCategory)
    tracked     = flow.SessionParam(True).ui(editor='bool', hidden=True)

    def needs_dialog(self):
        self.file_format.revert_to_default()
        return super(CreateFileAction, self).needs_dialog()
    
    def _title(self):
        return '<h2>Create file</h2>'

    def run(self, button):
        if button == 'Cancel':
            return

        name, extension = self.file_name.get(), self.file_format.get()

        if self._files.has_file(name, extension):
            self._warn((
                f'File {name}.{extension} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)

        path_format = self.get_path_format(f'{self.file_name.get()}_{self.file_format.get()}')

        if path_format is None:
            self._warn((
                'The path format of this file is undefined. '
                'You must define at least a default path format '
                'in the default settings of the project task manager.'
            ))
            return self.get_result(close=False)
        
        f = self._files.add_file(
            name,
            extension=extension,
            base_name=name,
            display_name=f'{name}.{extension}',
            tracked=self.tracked.get(),
            default_path_format=path_format
        )
        f.file_type.set(self.category.get())
        self._files.touch()


class CreateFolderAction(CreateFileSystemItemAction):

    ICON = ('icons.gui', 'add-folder')

    _files = flow.Parent()

    folder_name = flow.SessionParam('').ui(label='Name')
    category    = flow.SessionParam('Works', value_type=FileCategory)
    tracked     = flow.SessionParam(True).ui(editor='bool', hidden=True)

    def _title(self):
        return '<h2>Create folder</h2>'

    def run(self, button):
        if button == 'Cancel':
            return
        
        name = self.folder_name.get()

        if self._files.has_folder(name):
            self._warn((
                f'Folder {name} already exists. '
                'Please choose another name.'
            ))
            return self.get_result(close=False)
        
        path_format = self.get_path_format(name)

        if path_format is None:
            self._warn((
                'The path format of this folder is undefined. '
                'You must define at least a default path format '
                'in the default settings of the project task manager.'
            ))
            return self.get_result(close=False)
        
        f = self._files.add_folder(
            name,
            base_name=name,
            display_name=name,
            tracked=self.tracked.get(),
            default_path_format=path_format
        )
        f.file_type.set(self.category.get())
        self._files.touch()


class FileSystemMap(EntityView):

    _STYLE_BY_STATUS = {
        'unlocked': ('icons.libreflow', 'blank'),
        'locked': ('icons.libreflow', 'lock-green'),
        'locked-other': ('icons.libreflow', 'lock-red')
    }

    _department = flow.Parent()

    create_file_action   = flow.Child(CreateFileAction).ui(label='Create file').injectable()
    create_folder_action = flow.Child(CreateFolderAction).ui(label='Create folder').injectable()

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(FileSystemItem)
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_file_collection().collection_name()

    def columns(self):
        return ['Name']
    
    def _get_item_property(self, item, property_name):
        self.mapped_names()
        return self._document_cache[item.oid()].get(property_name, None)
    
    def _ensure_item_property(self, item, property_name):
        prop = self._get_item_property(item, property_name)

        if prop is None:
            # Reload cache in case it does not contain the provided property
            self._document_cache = None
            prop = self._get_item_property(item, property_name)
        
        return prop

    def _fill_row_cells(self, row, item):
        row['Name'] = self._ensure_item_property(item, 'display_name')

    def _fill_row_style(self, style, item, row):
        style['Name_activate_oid'] = item.open.oid()
        style['Name_icon'] = item.get_icon(
            extension=self._ensure_item_property(item, 'format')
        )

    def _get_status_icon(self, item):
        self.mapped_names()

        user_name = self.root().project().get_user_name()
        locked_by = self._document_cache[item.oid()].get('locked_by', None)

        if locked_by is None:
            lock_key = 'unlocked'
        elif locked_by == user_name:
            lock_key = 'locked'
        else:
            lock_key = 'locked-other'
        
        folder, icon_name = self._STYLE_BY_STATUS[lock_key]
        
        return folder, icon_name
    
    def get_parent_path(self):
        '''
        Returns the parent path of files contained in this map.
        '''
        return self.oid()[1:]

    def add_file(self, name, extension, display_name=None, base_name=None, tracked=False, default_path_format=None):
        '''
        Create a file in this map.

        If provided, `base_name` define the name of the file in the file system,
        without its extension. Otherwise, it defaults to the provided `name`.
        '''
        if base_name is None:
            base_name = name
        if display_name is None:
            display_name = f'{name}.{extension}'
        if default_path_format is None:
            settings = get_contextual_dict(self, 'settings')
            default_path_format = settings.get('path_format')
        
        f = self.add(
            self._get_item_mapped_name(name, extension),
            object_type=self._get_item_type(tracked, extension)
        )

        f.configure(extension, base_name, display_name, default_path_format)
        
        return f
    
    def add_folder(self, name, display_name=None, base_name=None, tracked=False, default_path_format=None):
        '''
        Create a folder in this map.

        If provided, `base_name` define the name of the file in the file system,
        without its extension. Otherwise, it defaults to the provided `name`.
        '''
        if base_name is None:
            base_name = name
        if display_name is None:
            display_name = name
        if default_path_format is None:
            settings = get_contextual_dict(self, 'settings')
            default_path_format = settings.get('path_format')
        
        f = self.add(
            self._get_item_mapped_name(name),
            object_type=self._get_item_type(tracked)
        )
        
        f.configure(None, base_name, display_name, default_path_format)
        
        return f
    
    def has_file(self, name, extension):
        return self.has_mapped_name(
            self._get_item_mapped_name(name, extension)
        )
    
    def has_folder(self, name):
        return self.has_mapped_name(
            self._get_item_mapped_name(name)
        )

    def _get_item_mapped_name(self, name, extension=None):
        mapped_name = name
        if extension is not None:
            mapped_name += '_' + extension
        
        return mapped_name

    def _get_item_type(self, tracked, extension=None):
        mapped_type = File
        
        if tracked:
            if extension is None:
                mapped_type = TrackedFolder
            else:
                mapped_type = TrackedFile
        elif extension is None:
            mapped_type = Folder
        
        # Ensure type is injectable
        flow.injection.injectable(mapped_type)

        # Return resolved type
        return flow.injection.resolve(mapped_type, self)


class PageNumber(flow.values.SessionValue):

    DEFAULT_EDITOR = 'choice'

    _manager = flow.Parent()

    def choices(self):
        c = self._get_collection().get_entity_store().get_collection(self._get_collection().collection_name())
        page_count = -1 * (- c.count_documents({}) // self._get_collection().page_size())
        return [str(i) for i in range(1, page_count + 1)]
    
    def _get_collection(self):
        raise NotImplementedError
    
    def update_page_num(self):
        self._get_collection().page_num.set(int(self.get()))
        self._get_collection().touch()


class FilePageNumber(PageNumber):

    def _get_collection(self):
        return self._manager.files


class RevisionPageNumber(PageNumber):

    def _get_collection(self):
        return self._manager.revisions


class SyncStatusPageNumber(PageNumber):

    def _get_collection(self):
        return self._manager.sync_statutes


class PaginatedGlobalCollection(GlobalEntityCollection):

    _page_size = flow.IntParam(50)
    page_num = flow.SessionParam(1).ui(editor='int')

    def page_size(self):
        return self._page_size.get()

    def current_page_num(self):
        return self.page_num.get()


class FileManager(flow.Object):

    files = flow.Child(PaginatedGlobalCollection).ui(expanded=True, show_filter=True)
    files_page_num = flow.SessionParam(1, FilePageNumber).ui(label='Page').watched()
    revisions = flow.Child(PaginatedGlobalCollection).ui(expanded=True, show_filter=True)
    revisions_page_num = flow.SessionParam(1, RevisionPageNumber).ui(label='Page').watched()
    sync_statutes = flow.Child(PaginatedGlobalCollection).ui(expanded=True, show_filter=True)
    sync_statutes_page_num = flow.SessionParam(1, SyncStatusPageNumber).ui(label='Page').watched()
    
    def child_value_changed(self, child_value):
        if child_value is self.files_page_num:
            self.files_page_num.update_page_num()
        elif child_value is self.revisions_page_num:
            self.revisions_page_num.update_page_num()
        elif child_value is self.sync_statutes_page_num:
            self.sync_statutes_page_num.update_page_num()


class RemoveDefaultFileAction(flow.Action):

    ICON = ('icons.gui', 'remove-symbol')

    _item = flow.Parent()
    _map  = flow.Parent(2)

    def needs_dialog(self):
        return False
    
    def run(self, button):
        map = self._map
        map.remove(self._item.name())
        map.touch()


class DefaultFile(flow.Object):

    file_name   = flow.Param()
    path_format = flow.Param()
    groups      = flow.Param('*')
    enabled     = flow.BoolParam(False)

    remove = flow.Child(RemoveDefaultFileAction)

    def in_groups(self, group_names):
        if group_names is None:
            return True
        
        for pattern in self.groups.get().replace(' ', '').split(','):
            if all([fnmatch.fnmatch(group_name, pattern) for group_name in group_names]):
                return True
        
        return False
    
    def get_icon(self):
        name, ext = os.path.splitext(
            self.file_name.get()
        )
        if ext:
            return FILE_EXTENSION_ICONS.get(
                ext[1:], ('icons.gui', 'text-file-1')
            )
        else:
            return ('icons.gui', 'folder-white-shape')


class CreateDefaultFileAction(flow.Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')

    file_name = flow.SessionParam('').ui(placeholder='layout.blend')
    path_format = flow.SessionParam('').ui(
        placeholder='{film}/{shot}/{file}/{revision}',
        tooltip=('Used to generate the file revision paths. It may contain keys '
                 '(between brackets {}) defined in the contextual dict.'))
    groups = flow.SessionParam('').ui(
        placeholder='layout',
        tooltip='A list of coma-separated wildcard patterns')
    enabled = flow.SessionParam(False).ui(editor='bool')

    _map = flow.Parent()

    def get_buttons(self):
        self.message.set('<h2>Create a default file preset</h2>')
        return ['Add', 'Cancel']
    
    def _filename_is_valid(self):
        if self.file_name.get() == '':
            self.message.set((
                '<h2>Create a default file preset</h2><font color=#FFA34D>'
                'File name must not be empty.</font>'
            ))
            return False
        
        for df in self._map.mapped_items():
            if self.file_name.get() == df.file_name.get():
                self.message.set((
                    '<h2>Create a default file preset</h2>'
                    '<font color=#FFA34D>A default file named '
                    f'<b>{self.file_name.get()}</b> already '
                    'exists. Please choose another name.</font>'
                ))
                return False
        
        return True
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        if not self._filename_is_valid():
            return self.get_result(close=False)
        
        i = 0
        while self._map.has_mapped_name('default%04i' % i):
            i += 1
        
        default_file = self._map.add('default%04i' % i)
        default_file.file_name.set(self.file_name.get())
        default_file.groups.set(self.groups.get())
        default_file.enabled.set(self.enabled.get())
        
        # Consider empty path format as undefined
        if not self.path_format.get():
            default_file.path_format.set(None)
        else:
            default_file.path_format.set(
                self.path_format.get()
            )

        self._map.touch()


class DefaultFileMap(flow.Map):

    add_default_file = flow.Child(CreateDefaultFileAction).ui(label='Add')

    @classmethod
    def mapped_type(cls):
        return DefaultFile
    
    def is_default(self, file_name):
        for item in self.mapped_items():
            if file_name == item.name():
                return True
        
        return False
    
    def columns(self):
        return ['Enabled', 'Name', 'Path format', 'Groups']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.file_name.get()
        row['Path format'] = item.path_format.get()
        row['Groups'] = item.groups.get()
        row['Enabled'] = ''
    
    def _fill_row_style(self, style, item, row):
        style['Name_icon'] = item.get_icon()
        style['Enabled_icon'] = ('icons.gui', 'check' if item.enabled.get() else 'check-box-empty')


class EnableDefaultFileAction(flow.Action):

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
        self._map.touch()


class ChangePathFormatAction(flow.Action):

    path_format = flow.SessionParam()

    _item = flow.Parent()
    _map  = flow.Parent(2)

    def get_buttons(self):
        self.path_format.set(
            self._item.path_format.get()
        )
        return ['Save', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        self._item.path_format.set(
            self.path_format.get()
        )
        self._map.touch()


class DefaultFileViewItem(flow.Object):

    file_name   = flow.SessionParam().ui(hidden=True)
    path_format = flow.SessionParam()
    enabled     = flow.SessionParam().ui(editor='bool')

    toggle_enabled     = flow.Child(EnableDefaultFileAction)
    change_path_format = flow.Child(ChangePathFormatAction)

    _action = flow.Parent(2)

    def refresh(self):
        default = self.root().project().get_default_file_presets()[
            self.name()
        ]
        self.file_name.set(default.file_name.get())
        self.path_format.set(default.path_format.get())
        self.enabled.set(
            not self.exists() and default.enabled.get()
        )
    
    def exists(self):
        name, ext = os.path.splitext(
            self.file_name.get()
        )
        
        if ext:
            return self._action.get_file_map().has_file(name, ext[1:])
        else:
            return self._action.get_file_map().has_folder(name)
    
    def create(self):
        name, ext = os.path.splitext(
            self.file_name.get()
        )

        if ext:
            self._action.get_file_map().add_file(
                name,
                extension=ext[1:],
                base_name=name,
                display_name=self.file_name.get(),
                tracked=True,
                default_path_format=self.path_format.get()
            )
        else:
            self._action.get_file_map().add_folder(
                name,
                base_name=name,
                display_name=name,
                tracked=True,
                default_path_format=self.path_format.get()
            )
    
    def get_icon(self):
        name, ext = os.path.splitext(
            self.file_name.get()
        )
        if ext:
            return FILE_EXTENSION_ICONS.get(
                ext[1:], ('icons.gui', 'text-file-1')
            )
        else:
            return ('icons.gui', 'folder-white-shape')


class ShowPathFormatAction(flow.Action):

    _map = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._map.show_path_format.set(
            not self._map.show_path_format.get()
        )
        self._map.touch()


class DefaultFileView(flow.DynamicMap):

    show_path_format = flow.SessionParam(False).ui(editor='bool', hidden=True)

    toggle_path_format = flow.Child(ShowPathFormatAction)

    _action = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return flow.injection.injectable(DefaultFileViewItem)
    
    def mapped_names(self, page_num=0, page_size=None):
        default_files = self.root().project().get_default_file_presets()
        target_groups = self._action.get_target_groups()

        if target_groups is None:
            names = default_files.mapped_names()
        else:
            names = []

            for f in default_files.mapped_items():
                if f.in_groups(target_groups):
                    names.append(f.name())
        
        return names
    
    def columns(self):
        cols = ['Enabled', 'Name']
        if self.show_path_format.get():
            cols.append('Path format')
        
        return cols
    
    def refresh(self):
        for item in self.mapped_items():
            item.refresh()
        self.touch()
    
    def _configure_child(self, item):
        item.refresh()
    
    def _fill_row_cells(self, row, item):
        row['Enabled'] = ''
        row['Name'] = item.file_name.get()
        row['Path format'] = item.path_format.get()
    
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
        
        style['Path format_activate_oid'] = item.change_path_format.oid()
        for col in ['Enabled', 'Name']:
            style['%s_activate_oid' % col] = item.toggle_enabled.oid()


class CreateDefaultFilesAction(flow.Action):

    default_files = flow.Child(DefaultFileView).ui(expanded=True)

    def get_buttons(self):
        self.default_files.refresh()
        return ['Create', 'Cancel']
    
    def get_target_groups(self):
        return None
    
    def get_file_map(self):
        '''
        Must return an instance of libreflow.baseflow.file.FileSystemMap
        '''
        raise NotImplementedError
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        for item in self.default_files.mapped_items():
            if item.exists() or not item.enabled.get():
                continue
            
            item.create()


class FileSystemRef(EntityRef):

    SOURCE_TYPE = FileSystemItem

    file_type = Property()

    _parent = flow.Parent(2)

    def get_goto_oid(self):
        return self.get()._parent.oid()


class FileSystemRefCollection(EntityRefMap):

    @classmethod
    def mapped_type(cls):
        return FileSystemRef
    
    def add_ref(self, source_oid, file_type):
        ref = super(FileSystemRefCollection, self).add_ref(source_oid)
        ref.file_type.set(file_type)
        return ref
    
    def collection_name(self):
        mgr = self.root().project().get_entity_manager()
        return mgr.get_file_ref_collection().collection_name()