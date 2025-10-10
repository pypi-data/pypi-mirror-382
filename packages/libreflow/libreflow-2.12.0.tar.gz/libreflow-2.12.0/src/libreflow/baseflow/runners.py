import os
import re
import sys
import platform
import subprocess
import logging
import time
from pathlib import Path
from datetime import datetime

import kabaret.app.resources as resources
from kabaret import flow
from kabaret.subprocess_manager.runner_factory import Runner, RunnerHandler
from kabaret.subprocess_manager.flow import RunAction
from kabaret.flow_entities.entities import Entity, Property
from ..utils.kabaret.flow_entities.entities import CustomEntityCollection

from ..resources.icons import flow as flow_icons
from ..resources.icons import applications as _
from ..resources.scripts import blender as _
from ..resources.scripts import tvpaint as _


FILE_EXTENSIONS = [
    "blend",
    "kra",
    "png",
    "jpg",
    "txt",
    "nk",
    "abc",
    "mov",
    "psd",
    "psb",
    "aep",
    "prproj",
    "zip",
    "mp4",
    "mxf",
    "fbx",
    "ai",
    "json",
    "jsx",
    "obj",
    "wav",
    "xpix",
    "usd",
    "usda",
    "usdz",
    "tvpp",
    "tvp",
    "tvpx",
]
FILE_EXTENSION_ICONS = {
    "blend": ("icons.libreflow", "blender"),
    "kra": ("icons.libreflow", "krita"),
    "png": ("icons.gui", "picture"),
    "jpg": ("icons.gui", "picture"),
    "txt": ("icons.gui", "text-file-1"),
    "nk": ("icons.libreflow", "nuke"),
    "abc": ("icons.flow", "alembic"),
    "aep": ("icons.libreflow", "afterfx"),
    "psd": ("icons.flow", "photoshop"),
    "psb": ("icons.flow", "photoshop"),
    "prproj": ("icons.libreflow", "premiere-pro"),
    "mov": ("icons.flow", "quicktime"),
    "ai": ("icons.libreflow", "illustrator"),
    "zip": ("icons.libreflow", "archive"),
    "mp4": ("icons.gui", "youtube-logo"),
    "mxf": ("icons.gui", "youtube-logo"),
    "fbx": ("icons.libreflow", "fbx"),
    "json": ("icons.libreflow", "json"),
    "jsx": ("icons.libreflow", "jsx"),
    "obj": ("icons.libreflow", "3d-object"),
    "wav": ("icons.gui", "youtube-logo"),
    "xpix": ("icons.gui", "text-file-1"),
    "usd": ("icons.gui", "text-file-1"),
    "usda": ("icons.gui", "text-file-1"),
    "usdz": ("icons.gui", "text-file-1"),
    "tvpp": ("icons.libreflow", "tvpaint"),
    "tvp": ("icons.libreflow", "tvpaint"),
    "tvpx": ("icons.libreflow", "tvpaint"),
}
RUNNER_ICONS = {
    "AfterEffects": ("icons.libreflow", "afterfx"),
    "AfterEffectsRender": ("icons.libreflow", "afterfx"),
    "Photoshop": ("icons.flow", "photoshop"),
    "Blender": ("icons.libreflow", "blender"),
    "DefaultEditor": ("icons.flow", "action"),
    "Explorer": ("icons.flow", "explorer"),
    "Firefox": ("icons.flow", "notepad"),
    "ImageMagick": ("icons.flow", "action"),
    "Krita": ("icons.libreflow", "krita"),
    "MarkSequenceRunner": ("icons.flow", "action"),
    "MinioFileDownloader": ("icons.flow", "action"),
    "MinioFileUploader": ("icons.flow", "action"),
    "Mrviewer": ("icons.flow", "quicktime"),
    "NotepadPP": ("icons.flow", "notepad"),
    "Nuke": ("icons.libreflow", "nuke"),
    "PremierePro": ("icons.libreflow", "premiere-pro"),
    "RV": ("icons.applications", "rv"),
    "SessionWorker": ("icons.flow", "action"),
    "VSCodium": ("icons.libreflow", "vscodium"),
    "TvPaint": ("icons.libreflow", "tvpaint"),
}

logger = logging.getLogger("kabaret")


# Runners
# -----------------


class DefaultEditor(Runner):
    @classmethod
    def can_edit(cls, filename):
        return True

    def executable(self):
        if platform.system() == "Darwin":
            return "open"
        elif platform.system() == "Linux":
            return "xdg-open"
        return None

    def run(self):
        if platform.system() == "Windows":
            os.startfile(self.argv()[0])
        else:
            super(DefaultEditor, self).run()


class EditFileRunner(Runner):

    ICON = ("icons.flow", "action")

    @classmethod
    def can_edit(cls, filename):
        ext = os.path.splitext(filename)[1]
        supported_exts = cls.supported_extensions()

        return supported_exts is None or ext in supported_exts

    @classmethod
    def supported_extensions(cls):
        """
        Supported file extensions.

        Return None by default to allow any extension.
        """
        return None

    def show_terminal(self):
        return False

    def exec_env_var(self, version=None):
        key = self.__class__.__name__.upper()

        if version is not None:
            key += "_%s" % version.upper().replace(".", "_")

        return "%s_EXEC_PATH" % key

    def executable(self):
        try:
            exec_path = os.environ[self.exec_env_var(self.version)]
            logging.getLogger("kabaret").log(
                logging.INFO, f"[RUNNER] Launch: {exec_path}"
            )
            return exec_path
        except KeyError:
            exec_path = os.environ[self.exec_env_var()]
            logging.getLogger("kabaret").log(
                logging.INFO, f"[RUNNER] Launch: {exec_path}"
            )
            return exec_path


class ImageMagick(EditFileRunner):

    @classmethod
    def can_edit(cls, filename):
        return True


class Blender(EditFileRunner):

    ICON = ("icons.libreflow", "blender")
    TAGS = [
        "Modeling",
        "Sculpting",
        "Animation",
        "Rigging",
        "3D Drawing",
        "Rendering",
        "Simulation",
        "Video Editing",
        "VFX",
    ]

    @classmethod
    def supported_versions(cls):
        return ["2.83", "2.90", "2.91", "2.92", "2.93"]

    @classmethod
    def supported_extensions(cls):
        return [".blend"]

    @classmethod
    def runner_handlers(cls):
        return [
            dict(
                handler_type="ERROR",
                description="Blender has crashed",
                pattern="(Writing: .+\.crash\.txt)\n",
                whence=500,
            ),
            dict(
                handler_type="ERROR",
                description="LFS Playblast addon is not enabled in Blender preferences",
                pattern="(KeyError: 'bpy_prop_collection\[key\]: key \"lfs_playblast\" not found')",
                whence=300,
            ),
            dict(
                handler_type="ERROR",
                description="Marked Image Sequence not found. Make sure ImageMagick is installed on your computer.",
                pattern=".*(?:fileseq.exceptions.FileSeqException).*(?:no sequence found on disk).*(?:marked).*",
                whence=300,
            ),
            dict(
                handler_type="ERROR",
                description="FFMpeg cannot be found. Make sure you have this dependency installed.",
                pattern=".*(?:subprocess.CalledProcessError).*(?:ffmpeg).*",
                whence=300,
            ),
            dict(
                handler_type="ERROR",
                description="Blender operator unrecognized",
                pattern=".*(?:keyword).*(?:unrecognized)",
                whence=300,
            ),
            dict(
                handler_type="INFO",
                description="Render progress",
                pattern="(Fra.*|Saved:.*|.Time:.*|Exporting Audio|Marking image.*|Generating video.*)",
                whence=300,
            ),
            dict(
                handler_type="SUCCESS",
                description="Render complete",
                pattern="(Rendered playblast(?:.*))",
                whence=300,
            ),
        ]


class Krita(EditFileRunner):

    ICON = ("icons.libreflow", "krita")
    TAGS = ["2D Drawing", "Image Editing"]

    @classmethod
    def supported_versions(cls):
        return ["4.3.0"]

    @classmethod
    def supported_extensions(cls):
        return [".kra", ".png", ".jpg"]


class KritaRunner(EditFileRunner):

    ICON = ("icons.libreflow", "krita")

    @classmethod
    def supported_extensions(cls):
        return [".kra"]


class AfterEffects(EditFileRunner):

    ICON = ("icons.libreflow", "afterfx")

    @classmethod
    def supported_extensions(cls):
        return [".aep", ".png", ".jpg"]


class AfterEffectsRender(EditFileRunner):

    ICON = ("icons.libreflow", "afterfx")

    @classmethod
    def supported_extensions(cls):
        return [".aep"]

    @classmethod
    def runner_handlers(cls):
        return [
            dict(
                handler_type="ERROR",
                description="AERender stopped",
                pattern="(aerender ERROR Une connexion existante a.*distant\.|aerender ERROR An existing connection was forcibly closed by the remote host.)",
                whence=200,
            ),
            dict(
                handler_type="ERROR",
                description="Composition not found",
                pattern="(aerender ERROR: No comp was found with the given name.)",
                whence=200,
            ),
            dict(
                handler_type="ERROR",
                description="Missing render settings",
                pattern="(aerender ERROR: No render settings template was found with the given name.)",
                whence=100,
            ),
            dict(
                handler_type="ERROR",
                description="Missing output module",
                pattern="(aerender ERROR: No output module template was found with the given name.)",
                whence=200,
            ),
            dict(
                handler_type="INFO",
                description="Render progress",
                pattern=".*\(\d*\).*",
                whence=300,
            ),
            dict(
                handler_type="SUCCESS",
                description="Render complete",
                pattern=".*(?:Finished composition|Total Time Elapsed).*",
                whence=300,
            ),
        ]


class VSCodium(EditFileRunner):

    ICON = ("icons.libreflow", "vscodium")
    TAGS = ["Text editing", "IDE"]

    @classmethod
    def supported_extensions(cls):
        return [".txt"]


class NotepadPP(EditFileRunner):

    ICON = ("icons.flow", "notepad")
    TAGS = ["Text editing"]

    @classmethod
    def supported_extensions(cls):
        return [".txt"]


class Firefox(EditFileRunner):

    ICON = ("icons.flow", "notepad")
    TAGS = ["Browser"]

    @classmethod
    def can_edit(cls, filename):
        return True


class RV(EditFileRunner):

    ICON = ("icons.applications", "rv")
    TAGS = ["Video editing"]

    def show_terminal(self):
        return True

    def keeps_terminal(self):
        return False


class Nuke(EditFileRunner):

    ICON = ("icons.libreflow", "nuke")
    TAGS = [
        "Compositing",
        "Video Editing",
        "VFX",
    ]

    @classmethod
    def supported_extensions(cls):
        return [".nk"]


class PremierePro(EditFileRunner):

    ICON = ("icons.libreflow", "premiere-pro")
    TAGS = ["Video Editing"]

    @classmethod
    def supported_extensions(cls):
        return [".prproj"]


class Mrviewer(EditFileRunner):

    ICON = ("icons.flow", "quicktime")
    TAGS = ["Video editing"]

    def show_terminal(self):
        return True

    def keeps_terminal(self):
        return False


class TvPaint(EditFileRunner):

    ICON = ("icons.libreflow", "tvpaint")
    TAGS = ["Video Editing"]

    @classmethod
    def supported_extensions(cls):
        return [".tvpp", ".tvp", ".tvpx"]

    def argv(self):
        """
        Must return the list of arg values for the command to run
        including self.extra_argv.
        Default is to return extra_argv
        """
        return self.extra_argv + [
            f'script={resources.get("scripts.tvpaint", "save_dependencies.grg")}'
        ]

    def run(self):
        cmd = [self.executable()]
        cmd.extend(self.argv())

        env = self.env()

        os_flags = {}

        # Disowning processes in linux/mac
        if hasattr(os, "setsid"):
            os_flags["preexec_fn"] = os.setsid

        # Disowning processes in windows
        if hasattr(subprocess, "STARTUPINFO"):
            # Detach the process
            os_flags["creationflags"] = subprocess.CREATE_NEW_CONSOLE

            # # Hide the process console
            startupinfo = subprocess.STARTUPINFO()
            if self.show_terminal():
                flag = "/C"
                if self.keep_terminal():
                    flag = "/K"
                cmd = ["cmd", flag] + cmd

            os_flags["startupinfo"] = startupinfo

        logger.debug("Running Subprocess: %r", cmd)

        if not os.path.exists(self._get_log_dir()):
            os.mkdir(self._get_log_dir())

        # Store run time used to compute log paths
        self._last_run_time = time.time()
        cmd = [str(arg) for arg in cmd]
        self._last_cmd = " ".join(cmd)

        self.create_log_path()
        self.handle_extra_handlers()
        with open(self._log_path, "w+") as log_fd:
            self._popen = subprocess.Popen(
                cmd,
                env=env,
                stdout=log_fd,
                stderr=log_fd,
                bufsize=0,  # unbuffered mode to avoid missing lines
                **os_flags,
            )


class Photoshop(EditFileRunner):

    ICON = ("icons.flow", "photoshop")
    TAGS = ["2D Drawing", "Image Editing"]

    @classmethod
    def supported_extensions(cls):
        return [".psd", ".psb", ".png", ".jpg"]


class PythonRunner(Runner):

    ICON = ("icons.flow", "action")

    def executable(self):
        return sys.executable

    def show_terminal(self):
        return False

    def keep_terminal(self):
        return False


class MarkSequenceRunner(PythonRunner):

    TAGS = ["Mark image sequence"]

    def argv(self):
        script_path = "%s/../scripts/mark_sequence.py" % os.path.dirname(__file__)
        return [script_path] + self.extra_argv

    @classmethod
    def runner_handlers(cls):
        return [
            dict(
                handler_type="ERROR",
                description="Image sequence not found",
                pattern="(fileseq\.exceptions\.FileSeqException: no sequence found on disk matching.*)",
                whence=400,
            ),
            dict(
                handler_type="INFO",
                description="Marking started",
                pattern=".(?:PLAYBLAST).*(?:Marking started...)",
                whence=300,
            ),
            dict(
                handler_type="SUCCESS",
                description="Marking complete",
                pattern=".(?:PLAYBLAST).*(?:Marking finished !)",
                whence=300,
            ),
        ]


class SessionWorker(PythonRunner):

    def argv(self):
        args = [
            "%s/../scripts/session_worker.py" % (os.path.dirname(__file__)),
            self.runner_name(),
        ]
        args += self.extra_argv
        return args

    @classmethod
    def runner_handlers(cls):
        return [
            dict(
                handler_type="ERROR",
                description="Image sequence not found",
                pattern=".*(?:Image sequence not found).*",
                whence=400,
            ),
            dict(
                handler_type="INFO",
                description="Marking started",
                pattern=".(?:PLAYBLAST).*(?:Marking started...)",
                whence=300,
            ),
            dict(
                handler_type="SUCCESS",
                description="Marking complete",
                pattern=".(?:PLAYBLAST).*(?:Marking finished !)",
                whence=300,
            ),
        ]


class LaunchSessionWorker(RunAction):

    def runner_name_and_tags(self):
        return "SessionWorker", []

    def launcher_oid(self):
        raise NotImplementedError()

    def launcher_exec_func_name(self):
        raise NotImplementedError()

    def launcher_exec_func_args(self):
        return []

    def launcher_exec_func_kwargs(self):
        return {}

    def extra_argv(self):
        return [
            self.launcher_oid(),
            self.launcher_exec_func_name(),
            self.launcher_exec_func_args(),
            self.launcher_exec_func_kwargs(),
        ]

    def runner_configured(self):
        """
        Returns None if the type of the runner run by this action is registered in the
        project's runner factory, or a message as a string describing the error.
        """
        msg = None
        name, tags = self.runner_name_and_tags()
        versions = (
            self.root().session().cmds.SubprocessManager.get_runner_versions(name, tags)
        )
        if versions is None:
            msg = (
                f"Runner '{name}' not found: make sure it is "
                "registered in the project runner factory.\n\n"
            )
        return msg

    def run(self, button):
        """
        Sets the environment variable which contains the runner executable path
        before launching the runner.
        """
        name, tags = self.runner_name_and_tags()

        rid = (
            self.root()
            .session()
            .cmds.SubprocessManager.run(
                runner_name=name,
                tags=tags,
                version=self.get_version(button),
                label=self.get_run_label(),
                extra_argv=self.extra_argv(),
                extra_env=self.extra_env(),
            )
        )
        return self.get_result(runner_id=rid)


# Handlers
# -----------------


class HandlerRunnerName(flow.values.SessionValue):

    DEFAULT_EDITOR = "choice"

    def choices(self):
        runners = self.root().project().get_factory().find_runners()
        return sorted([r[0] for r in runners])

    def revert_to_default(self):
        names = self.choices()
        if names:
            self.set(names[0])


class HandlerTypeChoiceValue(flow.values.ChoiceValue):

    CHOICES = ["ERROR", "WARNING", "INFO", "SUCCESS"]


class HandlerTypeSessionChoiceValue(flow.values.SessionValue):

    DEFAULT_EDITOR = "choice"

    def choices(self):
        return ["ERROR", "WARNING", "INFO", "SUCCESS"]


class RemoveHandlerEdit(flow.Action):

    ICON = ("icons.gui", "remove-symbol")

    _handler = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        return False

    def run(self, button):
        _map = self._map

        _map.remove(self._handler.name())
        _map.touch()


class RunnerHandlerEdit(Entity):

    runner = Property()
    handler_type = Property()
    description = Property()
    pattern = Property().ui(editor="textarea")
    whence = Property().ui(editor="int")
    enabled = Property().ui(editor="bool")
    remove = flow.Child(RemoveHandlerEdit)


class RunnerHandlersEdits(CustomEntityCollection):

    @classmethod
    def mapped_type(cls):
        return RunnerHandlerEdit

    def columns(self):
        return ["Application", "Description"]

    def _fill_row_cells(self, row, item):
        row["Application"] = item.runner.get()
        row["Description"] = item.description.get()

    def _fill_row_style(self, style, item, row):
        factory = self.root().project().get_factory()

        style["icon"] = factory.get_runner(item.runner.get()).runner_icon()
        if not item.enabled.get():
            for c in self.columns():
                style[f"{c}_foreground-color"] = "#606060"


class RemoveHandlerOverride(flow.Action):

    ICON = ("icons.gui", "remove-symbol")

    _handler = flow.Parent()
    _map = flow.Parent(2)

    def allow_context(self, context):
        return context and "default_edit" in self._handler.status.get()

    def needs_dialog(self):
        return False

    def run(self, button):
        _map = self._map

        edit_index = re.search(r"(edit\d+)", self._handler.status.get()).group(0)
        _map.edits.remove(f"{self._handler.runner.get().lower()}_{edit_index}")
        _map.touch()


class RemoveHandler(flow.Action):

    ICON = ("icons.gui", "remove-symbol")

    _handler = flow.Parent()
    _map = flow.Parent(2)

    def allow_context(self, context):
        return context and (
            "edit" in self._handler.status.get()
            and "default" not in self._handler.status.get()
        )

    def needs_dialog(self):
        return False

    def run(self, button):
        _map = self._map

        _map.edits.remove(self._handler.name())
        _map.touch()


class EditRunnerHandler(flow.Action):

    ICON = ("icons.libreflow", "edit-blank")

    runner = flow.Param("", HandlerRunnerName).ui(
        editable=False, choice_icons=RUNNER_ICONS
    )
    handler_type = flow.Param("", HandlerTypeChoiceValue)
    description = flow.Param().ui(editable=False)
    pattern = flow.Param().ui(editor="textarea")
    whence = flow.IntParam()
    enabled = flow.BoolParam()

    _handler = flow.Parent()
    _map = flow.Parent(2)

    def get_buttons(self):
        self.runner.set(self._handler.runner.get())
        self.handler_type.set(self._handler.handler_type.get())
        self.description.set(self._handler.description.get())
        self.pattern.set(self._handler.pattern.get())
        self.whence.set(self._handler.whence.get())
        self.enabled.set(self._handler.enabled.get())

        buttons = ["Save"]
        if "default_edit" in self._handler.status.get():
            buttons.append("Restore default")

        return buttons + ["Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        edit_index = re.search(r"(edit\d+)", self._handler.status.get())
        if edit_index is not None:
            edit_index = edit_index.group(0)

        edit_name = f"{self._handler.runner.get().lower()}_{edit_index}"

        if button == "Restore default":
            self._map.edits.remove(edit_name)
        else:
            if self._map.edits.has_mapped_name(edit_name):
                handler = self._map.edits[edit_name]
            else:
                index = str(len(self._map.edits.mapped_names()) + 1)
                handler = self._map.edits.add(
                    f"{self.runner.get().lower()}_edit{index}"
                )

            handler.runner.set(self.runner.get())
            handler.handler_type.set(self.handler_type.get())
            handler.description.set(self.description.get())
            handler.pattern.set(self.pattern.get())
            handler.whence.set(self.whence.get())
            handler.enabled.set(self.enabled.get())

        self._map.touch()


class RunnerHandler(Entity):

    runner = flow.Computed()
    handler_type = flow.Computed()
    description = flow.Computed()
    pattern = flow.Computed().ui(editor="textarea")
    whence = flow.Computed().ui(editor="int")
    status = flow.Computed()
    enabled = flow.Computed().ui(editor="bool")
    edit = flow.Child(EditRunnerHandler).ui(dialog_size=(600, 450))
    remove = flow.Child(RemoveHandler)
    reset_to_default = flow.Child(RemoveHandlerOverride).ui(label="Restore default")

    _map = flow.Parent()

    def compute_child_value(self, child_value):
        child_value.set(self._map.get_child_value(self.name(), child_value.name()))


class AddRunnerHandler(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    runner = flow.SessionParam(None, HandlerRunnerName).ui(choice_icons=RUNNER_ICONS)
    handler_type = flow.SessionParam("", HandlerTypeSessionChoiceValue)
    description = flow.SessionParam("")
    pattern = flow.SessionParam("").ui(editor="textarea")
    whence = flow.SessionParam(200).ui(
        tooltip="Number of last bytes used to search for errors"
    )

    _map = flow.Parent()

    def needs_dialog(self):
        self.runner.revert_to_default()
        return True

    def get_buttons(self):
        return ["Add", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        index = str(len(self._map.edits.mapped_names()) + 1)
        handler = self._map.edits.add(f"{self.runner.get().lower()}_edit{index}")
        handler.runner.set(self.runner.get())
        handler.handler_type.set(self.handler_type.get())
        handler.description.set(self.description.get())
        handler.pattern.set(self.pattern.get())
        handler.whence.set(self.whence.get())
        handler.enabled.set(True)

        self._map.touch()


class RunnerHandlers(flow.DynamicMap):

    edits = flow.Child(RunnerHandlersEdits).ui(hidden=True)

    add_handler = flow.Child(AddRunnerHandler).ui(dialog_size=(600, 400))

    def __init__(self, parent, name):
        super(RunnerHandlers, self).__init__(parent, name)
        self._cache = None

    @classmethod
    def mapped_type(cls):
        return RunnerHandler

    def mapped_names(self, page_num=0, page_size=None):
        if self._cache is None:
            # Collect and append base (default) runner handlers
            factory = self.root().project().get_factory()
            base_handlers = factory.list_runner_handlers()

            self._cache = {}

            for runner_name, handlers in base_handlers.items():
                runner_icon = factory.get_runner(runner_name).runner_icon()
                for handler in handlers:
                    data = {}
                    data.update(
                        runner=runner_name,
                        handler_type=handler["handler_type"],
                        description=handler["description"],
                        pattern=handler["pattern"],
                        whence=handler["whence"],
                        status="default",
                        enabled=True,
                        icon=(
                            runner_icon
                            if runner_icon
                            else ("icons.gui", "cog-wheel-silhouette")
                        ),
                    )

                    i = str(len(self._cache) + 1)
                    self._cache[f"{runner_name.lower()}_{i}"] = data

            # Collect for extra and overrides handlers
            edit_names = set(self.edits.mapped_names())

            for name in edit_names:
                handler_edit = self.edits[name]

                runner_icon = factory.get_runner(
                    handler_edit.runner.get()
                ).runner_icon()
                data = {}

                # Override if handler already exists
                exist = [
                    handler_name
                    for handler_name, data in self._cache.items()
                    if data["description"] == handler_edit.description.get()
                ]
                if exist:
                    handler_name = exist[0]
                    status = re.search(r"(edit\d+)", handler_edit.name()).group(0)
                    self._cache[handler_name] = dict(
                        runner=handler_edit.runner.get(),
                        handler_type=handler_edit.handler_type.get(),
                        description=handler_edit.description.get(),
                        pattern=handler_edit.pattern.get(),
                        whence=handler_edit.whence.get(),
                        status=f"default_{status}",
                        enabled=handler_edit.enabled.get(),
                        icon=(
                            runner_icon
                            if runner_icon
                            else ("icons.gui", "cog-wheel-silhouette")
                        ),
                    )
                # Create if completely new handler
                else:
                    data.update(
                        runner=handler_edit.runner.get(),
                        handler_type=handler_edit.handler_type.get(),
                        description=handler_edit.description.get(),
                        pattern=handler_edit.pattern.get(),
                        whence=handler_edit.whence.get(),
                        status=re.search(r"(edit\d+)", handler_edit.name()).group(0),
                        enabled=handler_edit.enabled.get(),
                        icon=(
                            runner_icon
                            if runner_icon
                            else ("icons.gui", "cog-wheel-silhouette")
                        ),
                    )

                    i = str(len(self._cache) + 1)
                    self._cache[handler_edit.name()] = data

        # Re-sort with overrides handlers
        self._cache = dict(sorted(self._cache.items()))

        return self._cache.keys()

    def columns(self):
        return ["Application", "Description"]

    def touch(self):
        self._cache = None
        self._mng.children.clear()
        super(RunnerHandlers, self).touch()

    def get_child_value(self, mapped_name, value_name):
        self.mapped_names()
        return self._cache[mapped_name][value_name]

    def _fill_row_cells(self, row, item):
        row["Application"] = item.runner.get()
        row["Description"] = item.description.get()

    def _fill_row_style(self, style, item, row):
        style["icon"] = self.get_child_value(item.name(), "icon")
        if not item.enabled.get():
            for c in self.columns():
                style[f"{c}_foreground-color"] = "#606060"


# Default Applications
# -----------------


class DefaultExtension(flow.values.SessionValue):
    DEFAULT_EDITOR = "choice"
    _map = flow.Parent(4)

    def choices(self):
        return sorted(set(FILE_EXTENSIONS) - set(self._map.mapped_names()))

    def revert_to_default(self):
        exts = self.choices()
        if exts:
            self.set(exts[0])


class SelectFileExtension(flow.Action):
    extension = flow.SessionParam(value_type=DefaultExtension).ui(
        choice_icons=FILE_EXTENSION_ICONS
    )
    _value = flow.Parent()

    def needs_dialog(self):
        self.extension.revert_to_default()
        return True

    def get_buttons(self):
        return ["Confirm", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return

        self._value.set(self.extension.get())


class FileExtension(flow.values.SessionValue):
    select = flow.Child(SelectFileExtension)


class RunnerName(flow.values.SessionValue):
    """
    Lists the names of all runner types registered
    in the project's runner factory compatible with
    the default application extension (`DefaultApp.name()`). # todo: update
    """

    DEFAULT_EDITOR = "choice"
    STRICT_CHOICES = False
    _parent = flow.Parent()

    def choices(self):
        runners = (
            self.root()
            .project()
            .get_factory()
            .find_runners(f"*.{self._parent.get_file_extension()}")
        )

        return [r[0] for r in runners]

    def revert_to_default(self):
        names = self.choices()
        if names:
            self.set(names[0])
        else:
            self.set(None)


class RunnerVersion(flow.values.SessionValue):
    """
    Lists the available versions of the runner
    selected in the parent action.
    """

    DEFAULT_EDITOR = "choice"
    STRICT_CHOICES = False
    _action = flow.Parent()

    def choices(self):
        factory = self.root().project().get_factory()
        versions = [
            v
            for v in factory.get_runner_versions(self._action.runner_name.get())
            if v is not None
        ]
        return ["Default"] + versions

    def revert_to_default(self):
        self.set("Default")


class AddDefaultApp(flow.Action):
    """
    Create a new extension with an associated default
    application.
    """

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    file_extension = flow.Param("", value_type=FileExtension).watched()
    runner_name = flow.Param(value_type=RunnerName).ui(label="Application").watched()
    runner_version = flow.Param(value_type=RunnerVersion).ui(label="Version")
    _map = flow.Parent()

    def needs_dialog(self):
        self.file_extension.revert_to_default()
        self.message.set("")
        return True

    def get_buttons(self):
        return ["Add", "Cancel"]

    def get_file_extension(self):
        return self.file_extension.get()

    def child_value_changed(self, child_value):
        if child_value is self.runner_name:
            self.runner_version.touch()
        elif child_value is self.file_extension:
            self.runner_name.revert_to_default()

    def run(self, button):
        if button == "Cancel":
            return

        ext = self.file_extension.get()
        if re.fullmatch(r"\w+", ext) is None:
            self.message.set(f"'{ext}' is not a valid file extension.")
            return self.get_result(close=False)

        app = self._map.add(ext)
        app.runner_name.set(self.runner_name.get())
        app.runner_version.set(self.runner_version.get())
        self._map.touch()


class EditDefaultApp(flow.Action):
    """
    Edit the name and version of a runner associated
    to an extension.
    """

    ICON = ("icons.libreflow", "edit-blank")

    runner_name = (
        flow.SessionParam(value_type=RunnerName).ui(label="Application").watched()
    )
    runner_version = flow.SessionParam(value_type=RunnerVersion).ui(label="Version")
    _app = flow.Parent()

    def needs_dialog(self):
        self.runner_name.set_watched(False)
        current_runner = self._app.runner_name.get()
        if current_runner in self.runner_name.choices():
            self.runner_name.set(current_runner)
        else:
            self.runner_name.revert_to_default()
        self.runner_name.set_watched(True)

        return True

    def get_buttons(self):
        return ["Save", "Cancel"]

    def get_file_extension(self):
        return self._app.name()

    def child_value_changed(self, child_value):
        if child_value is self.runner_name:
            self.runner_version.touch()

    def run(self, button):
        if button == "Cancel":
            return

        self._app.runner_name.set(self.runner_name.get())
        self._app.runner_version.set(self.runner_version.get())
        self._app.touch()


class RemoveDefaultApp(flow.Action):
    """
    Remove a default application.
    """

    ICON = ("icons.gui", "remove-symbol")

    _app = flow.Parent()
    _map = flow.Parent(2)

    def needs_dialog(self):
        return False

    def run(self, button):
        _map = self._map
        _map.remove(self._app.name())
        _map.touch()


class DefaultApp(flow.Object):
    """
    Mapping between a file extension and a runner type.

    The actual extension is the name of the object
    (`DefaultApp.name()`).
    """

    runner_name = flow.Param()
    runner_version = flow.Param()
    edit = flow.Child(EditDefaultApp)
    remove = flow.Child(RemoveDefaultApp)


class DefaultApps(flow.Map):
    """
    Maps a file extension with one of the runner types
    available in the project's runner factory.
    """

    add_default_app = flow.Child(AddDefaultApp).ui(label="Add default application")

    @classmethod
    def mapped_type(cls):
        return DefaultApp

    def columns(self):
        return ["Extension", "Application", "Version"]

    def _fill_row_cells(self, row, item):
        row["Extension"] = item.name()
        row["Application"] = item.runner_name.get()
        version = item.runner_version.get()
        row["Version"] = version if version else "Default"

    def _fill_row_style(self, style, item, row):
        style["activate_oid"] = item.edit.oid()
        style["icon"] = FILE_EXTENSION_ICONS.get(
            item.name(), ("icons.gui", "cog-wheel-silhouette")
        )
