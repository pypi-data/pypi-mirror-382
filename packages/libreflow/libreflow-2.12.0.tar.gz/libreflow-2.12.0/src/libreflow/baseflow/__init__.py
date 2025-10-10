import os
import json
import gazu
import getpass
import pathlib
import fnmatch
import re
import unicodedata

from kabaret.app import resources
from kabaret.app.resources import ResourcesError
from kabaret import flow
from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtGui,
    QtCore,
)
from kabaret.app.ui.gui.widgets.editors import editor_factory
from kabaret.flow_contextual_dict import ContextualView, get_contextual_dict
from kabaret.subprocess_manager.runners import Explorer
from kabaret.flow_entities.store import EntityStore

from .users import Users, UserEnvironment, UserBookmarks, UserProfile
from .lib import Assets
from .shot import SequenceCollection
from .runners import (
    Krita,
    KritaRunner,
    Blender,
    AfterEffects,
    AfterEffectsRender,
    VSCodium,
    NotepadPP,
    MarkSequenceRunner,
    Firefox,
    SessionWorker,
    DefaultEditor,
    ImageMagick,
    RV,
    Nuke,
    PremierePro,
    Mrviewer,
    TvPaint,
    Photoshop,
    PythonRunner,
    DefaultApps,
    RunnerHandlers,
)
from .site import (
    Synchronize,
    GotoCurrentSiteQueue,
    WorkingSites,
    ExchangeSites,
    MinioFileUploader,
    MinioFileDownloader,
    ExchangeSiteChoiceValue,
)
from .file import TrackedFile, Revision, DefaultFileMap
from .kitsu import KitsuAPIWrapper, KitsuBindings, KitsuTasks, KitsuTaskAvailableStatutes
from .dependency import DependencyTemplates
from .mytasks import MyTasks
from .search import Search
from ..utils.flow.import_files import ImportFilesAction


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


class LoginPageWidget(CustomPageWidget):
    def build(self):
        self.error_count = 0

        # Get project root oid
        self.project_oid = self.session.cmds.Flow.split_oid(self.oid)[0][1]

        # Build UI
        self.label = QtWidgets.QLabel(self)
        self.label.setText("<h2>Welcome back!</h2>")

        self.description_label = QtWidgets.QLabel(self)
        self.kitsu_url = self.session.cmds.Flow.get_value(
            f"{self.project_oid}/admin/kitsu/server_url"
        )
        if "https" in self.kitsu_url:
            self.description_label.setText(
                f'Enter your Kitsu credentials for server: <a href="{self.kitsu_url}">{self.kitsu_url.split("https://")[1]}</a>'
            )
        else:
            self.description_label.setText(
                f'Enter your Kitsu credentials for server: <a href="{self.kitsu_url}">{self.kitsu_url.split("http://")[1]}</a>'
            )
        self.description_label.setOpenExternalLinks(True)

        self.lineedit_kitsu_login = QtWidgets.QLineEdit()
        self.lineedit_kitsu_login.setPlaceholderText("Login")

        self.lineedit_kitsu_password = QtWidgets.QLineEdit()
        self.lineedit_kitsu_password.setPlaceholderText("Password")

        self.error_label = QtWidgets.QLabel(self)
        self.error_label.hide()

        self.error_image = QtWidgets.QLabel(self)
        try:
            resources.get("gifs", "magic_word")
            self.gif = QtGui.QMovie(resources.get("gifs", "magic_word"))
            self.gif.setScaledSize(QtCore.QSize(200, 200))
            self.error_image.setMovie(self.gif)
        except ResourcesError:
            self.gif = None

        self.button_login = QtWidgets.QPushButton("Log in")
        self.button_login.setMinimumWidth(100)

        # Set kitsu_password field input mode
        self.lineedit_kitsu_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineedit_kitsu_password.setInputMethodHints(
            QtCore.Qt.ImhHiddenText
            | QtCore.Qt.ImhNoPredictiveText
            | QtCore.Qt.ImhNoAutoUppercase
        )

        lo = QtWidgets.QVBoxLayout(self)
        lo.addWidget(self.label)
        lo.addWidget(self.description_label)
        lo.addSpacing(10)
        lo.addWidget(self.lineedit_kitsu_login)
        lo.addWidget(self.lineedit_kitsu_password)

        footer = QtWidgets.QHBoxLayout()
        fo_left = QtWidgets.QVBoxLayout()
        fo_right = QtWidgets.QHBoxLayout()

        fo_left.addWidget(self.error_label)
        fo_left.addWidget(self.error_image)

        fo_right.addStretch()
        fo_right.addWidget(self.button_login, alignment=QtCore.Qt.AlignTop)

        footer.addLayout(fo_left)
        footer.addLayout(fo_right)
        lo.addLayout(footer)
        lo.addStretch()

        self.button_login.clicked.connect(self.on_connection_validated)
        self.lineedit_kitsu_login.returnPressed.connect(self.on_connection_validated)
        self.lineedit_kitsu_password.returnPressed.connect(self.on_connection_validated)

    def on_connection_validated(self):
        kitsu_login = self.lineedit_kitsu_login.text()
        kitsu_password = self.lineedit_kitsu_password.text()
        logged_in = self.session.cmds.Flow.call(
            self.project_oid,
            "log_in",
            args=[kitsu_login, kitsu_password],
            kwargs={},
        )

        if not logged_in:
            text = (
                "<font color=#fba071><b>Login failed... Check credentials !</font></b>"
            )
            self.error_label.setText(text)
            self.error_label.show()
            self.error_count += 1
            if self.gif and self.error_count > 2:
                self.gif.start()
            return

        self.error_label.setText("")

        # Back to Wizard if we were there
        # And start CreateKitsu matching action
        wizard_default_page = self.session.cmds.Flow.call(
            "/Home/Wizard", "get_default_page", {}, {}
        )
        if wizard_default_page is not None:
            if wizard_default_page == "Users":
                self.page.show_action_dialog(
                    f"{self.project_oid}/admin/users/create_users"
                )
            elif wizard_default_page == "Tasks":
                self.page.show_action_dialog(
                    f"{self.project_oid}/admin/project_settings/task_manager/default_tasks/add_kitsu_tasks"
                )
            return self.page.goto("/Home/Wizard")

        self.page.refresh()


class LoginPage(flow.Object):

    kitsu_server_url = flow.Param("")


class SynchronizeFilesResult(flow.Action):

    def allow_context(self, context):
        return False

    def get_buttons(self):
        return ["Close"]

    def run(self, button):
        return


class SynchronizeFiles(Synchronize):

    ICON = ("icons.libreflow", "sync")

    result = flow.Child(SynchronizeFilesResult)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        exchange_site = self.root().project().get_exchange_site()

        if not exchange_site.configured.get():
            self.message.set(
                (
                    "<h3><font color=#D5000D>"
                    "Exchange site not configured"
                    "</font></h3>"
                    "Please configure the exchange site of this project."
                )
            )
            return ["Configure exchange site", "Cancel"]

        self.message.set(
            (
                "<h3><font color=#D66700>"
                "Synchronizing all requested files may freeze your session for a while."
                "</font></h3>"
            )
        )
        return ["Confirm", "Cancel"]

    def allow_context(self, context):
        return context and context.endswith(".details")

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Configure exchange site":
            exchange_site = self.root().project().get_exchange_site()
            return self.get_result(next_action=exchange_site.configuration.oid())

        site = self.root().project().get_current_site()
        nb_processed_init = site.count_jobs(status="PROCESSED")
        nb_waiting_init = site.count_jobs(status="WAITING")
        nb_error_init = site.count_jobs(status="ERROR")
        # Process jobs
        super(SynchronizeFiles, self).run(button)
        # Print final counts
        nb_processed = site.count_jobs(status="PROCESSED") - nb_processed_init
        nb_error = site.count_jobs(status="ERROR") - nb_error_init

        if nb_processed == nb_waiting_init and nb_error == 0:
            msg = (
                "<h3><font color=#029600>" "Synchronization successful !" "</font></h3>"
            )
        else:
            msg = ""

            if nb_processed < nb_waiting_init:
                msg += (
                    "<h3><font color=#D66700>"
                    f"Synchronized files: {nb_processed}/{nb_waiting_init}"
                    "</font></h3>"
                )
            if nb_error > 0:
                msg += (
                    "<h3><font color=#D5000D>"
                    f"Errors: {nb_error}/{nb_waiting_init}"
                    "</font></h3>"
                )

        if nb_error_init > 0:
            msg += (
                "<h3><font color=#D5000D>"
                f"Other waiting errors: {nb_error_init}"
                "</font></h3>"
            )

        self.result.message.set(msg)

        return self.get_result(next_action=self.result.oid())


class GotoBookmarks(flow.Action):
    ICON = ("icons.gui", "star")

    def needs_dialog(self):
        return False

    def run(self, button):
        return self.get_result(goto=self.root().project().admin.bookmarks.oid())


class GoToMyTasks(flow.Action):
    ICON = ("icons.gui", "mytasks")

    def allow_context(self, context):
        return context

    def needs_dialog(self):
        return False

    def run(self, button):
        return self.get_result(goto=self.root().project().mytasks.oid())


class WorkingSiteChoiceValue(flow.values.ChoiceValue):

    _parent = flow.Parent()

    def choices(self):
        return self.root().project().get_working_sites().mapped_names()


class CleanZipFiles(flow.Action):

    ICON = ("icons.libreflow", "clean")

    def __init__(self, parent, name):
        super(CleanZipFiles, self).__init__(parent, name)
        self._paths = []

    def get_buttons(self):
        self.message.set("<h2>Remove ZIP files</h2>")
        return ["Confirm", "Search", "Cancel"]

    def run(self, button):
        if button == "Cancel":
            return
        elif button == "Search":
            root_project = self.root().project().get_root().replace("\\", "/")
            self._paths = []
            file_count = 0
            file_size = 0

            root_lib = os.path.join(root_project, "lib").replace("\\", "/")
            root_film = os.path.join(root_project, "siren").replace("\\", "/")

            for root_path in (root_lib, root_film):
                for root, _, files in os.walk(root_path):
                    norm_root = root.replace("\\", "/").replace(root_project, "")

                    for f in files:
                        match = re.search(
                            "lib/(chars|props|sets)/.*/.*/.*/.*/v\d\d\d", norm_root
                        )
                        match = match or re.search(
                            "/siren/sq\d\d/sc\d\d\d\d/.*/.*/v\d\d\d", norm_root
                        )

                        if match is not None and os.path.splitext(f)[1] == ".zip":
                            path = os.path.join(root, f)
                            file_count += 1
                            file_size += os.path.getsize(path)
                            self._paths.append(path)

            self.message.set(
                (
                    "<h2>Remove ZIP files</h2>"
                    "<b>%i</b> ZIP files found in this project (~%03f Gb)."
                    '<h3><font color="#D5000D">Remove all ?</font></h3>'
                    % (file_count, file_size * 0.000000001)
                )
            )

            return self.get_result(close=False)
        else:
            for p in self._paths:
                try:
                    self.root().session().log_warning("Remove file %s" % p)
                    os.remove(p)
                except Exception:
                    self.root().session().log_warning("Failed to remove file %s" % p)


class Synchronization(flow.Object):

    ICON = ("icons.libreflow", "sync")

    _project = flow.Parent()
    synchronize_files = flow.Child(SynchronizeFiles)
    show_jobs = flow.Child(GotoCurrentSiteQueue)

    def summary(self):
        nb_waiting_jobs = (
            self.root().project().get_current_site().count_jobs(status="WAITING")
        )

        if nb_waiting_jobs > 0:
            return (
                "<font color=#D5000D><b>"
                f"{nb_waiting_jobs} job(s) waiting"
                "</b></font>"
            )


class LogOut(flow.Action):

    ICON = ("icons.libreflow", "log_out")

    def needs_dialog(self):
        return False

    def allow_context(self, context):
        return context and context.endswith(".details")

    def run(self, button):
        project = self.root().project()
        kitsu_config = "%s/kitsu_config.json" % project.user_settings_folder()

        if os.path.exists(kitsu_config):
            os.remove(kitsu_config)

        project.log_out()

        return self.get_result(goto=project.oid(), refresh=True)


class KitsuConfig(flow.Object):

    ICON = ("icons.libreflow", "kitsu")

    server_url = flow.Param().watched()
    project_name = flow.Param().watched()
    project_id = flow.Computed(cached=True)
    project_type = flow.Computed(cached=True)
    uploadable_files = flow.Param("")
    bindings = flow.Child(KitsuBindings)
    tasks = flow.Child(KitsuTasks)
    task_statutes = flow.Param(list, KitsuTaskAvailableStatutes)
    gazu_api = flow.Child(KitsuAPIWrapper).ui(hidden=True)
    configured = flow.Computed().ui(editor="bool", hidden=True)

    def child_value_changed(self, child_value):
        self.project_id.touch()

    def compute_child_value(self, child_value):
        if child_value is self.project_id:
            try:
                self.project_id.set(self.gazu_api.get_project_id())
            except Exception:
                self.root().session().log_error(
                    "Cannot access Kitsu project entity, some features may be unavailable"
                )
        elif child_value is self.project_type:
            if self.gazu_api.host_is_valid():
                try:
                    self.project_type.set(self.gazu_api.get_project_type())
                except Exception:
                    self.root().session().log_error(
                        "Cannot access Kitsu project entity, some features may be unavailable"
                    )
        elif child_value is self.configured:
            self.configured.set(self.project_id.get() is not None)

    def is_uploadable(self, file_name):
        patterns = self.uploadable_files.get().split(",")

        for pattern in patterns:
            pattern = pattern.replace(" ", "")
            if fnmatch.fnmatch(file_name, pattern):
                return True

        return False

    def summary(self):
        if not self.configured.get():
            return (
                "<font color=#D5000D>"
                "<b>Server URL</b> and <b>project name</b> "
                "unset: Kitsu features won't be available"
            )


class ProjectSettings(flow.Object):

    ICON = ("icons.gui", "settings")

    project_code = flow.Param()
    project_nice_name = flow.Param()
    project_thumbnail = flow.Param().ui(editor="image")
    show_project_name = flow.BoolParam()
    support = flow.Param("")
    frame_rate = flow.Param(24.0)
    width = flow.Param(1920)
    height = flow.Param(1080)

    settings = flow.Child(ContextualView)
    default_files = flow.Child(DefaultFileMap)
    non_editable_files = flow.Param("")
    auto_upload = flow.Param("").ui(
        tooltip="Enable <b>upload after publish</b> by default for all files matching the provided patterns"
    )
    hide_upload_after_publish = flow.Param("")
    clean_zip_files = flow.Child(CleanZipFiles).ui(label="Clean ZIP files")
    enable_file_lock = flow.BoolParam(False)
    revision_statutes = flow.Param(list)
    optional_publish_comment = flow.BoolParam(False)
    enable_publish_read_only = flow.BoolParam(True).ui(
        label="Enable Read Only For Publish",
        true_text="Only for Blender at the moment",
        false_text="Only for Blender at the moment",
    )
    import_files_object = flow.Connection(related_type=ImportFilesAction).ui(
        label="Import Files Action", hidden=True
    )

    def __init__(self, parent, name):
        super(ProjectSettings, self).__init__(parent, name)
        # Set default import files action
        base_action = self.root().get_object(
            f"{self.root().project().oid()}/import_files"
        )

        if (
            isinstance(base_action, ImportFilesAction)
            and self.import_files_object.get() is None
        ):
            self.import_files_object.set(base_action)

    def get_auto_upload_files(self):
        return self.auto_upload.get().replace(" ", "").split(",")

    def get_hidden_upload_files(self):
        return self.hide_upload_after_publish.get().replace(" ", "").split(",")


class MultisiteConfig(flow.Object):

    ICON = ("icons.gui", "sitemap")

    current_site_name = flow.Computed(cached=True)
    root_dir = flow.Computed(cached=True)
    temp_dir = flow.Computed(cached=True)
    exchange_site_name = (
        flow.Param("default_exchange", ExchangeSiteChoiceValue)
        .watched()
        .ui(editable=False)
    )
    working_sites = flow.Child(WorkingSites).ui(label="Working sites")
    exchange_sites = flow.Child(ExchangeSites).ui(label="Exchange sites")
    sites_data = flow.Computed(cached=True).ui(hidden=True)

    def child_value_changed(self, child_value):
        if child_value is self.exchange_site_name:
            self.touch()

    def compute_child_value(self, child_value):
        if child_value is self.root_dir:
            """
            TODO : Override by site on multisite !
            """
            root_dir = None
            if "ROOT_DIR" in os.environ:
                self.root().session().log_warning(
                    "ROOT_DIR was defined by the environement !"
                )
                root_dir = os.environ["ROOT_DIR"]
            else:
                # Otherwise, get current site's root dir
                root_dir = self.working_sites[
                    self.current_site_name.get()
                ].root_folder.get()

            child_value.set(root_dir)
        elif child_value is self.temp_dir:
            path = self.root_dir.get()

            if path is not None:
                path = os.path.join(path, ".tmp")

                if not os.path.exists(path):
                    os.makedirs(path)

            self.temp_dir.set(path)
        elif child_value is self.current_site_name:
            if "KABARET_SITE_NAME" in os.environ:
                site_name = os.environ["KABARET_SITE_NAME"]
            else:
                site_name = os.environ["KABARET_CLUSTER_NAME"]

            if not self.working_sites.has_mapped_name(site_name):
                self.root().session().log_warning(
                    (
                        f"Site {site_name} not found in project working sites. "
                        "Falling back to default."
                    )
                )
                site_name = "default"

            child_value.set(site_name)
        elif child_value is self.sites_data:
            self.sites_data.set(self._compute_sites_data())

    def _compute_sites_data(self):
        data = {}

        for s in self.root().project().get_working_sites().mapped_items():
            data[s.name()] = {
                "is_default": True,
                "is_active": s.is_active.get(),
                "short_name": s.short_name.get(),
            }
        for s in self.root().project().get_exchange_sites().mapped_items():
            data[s.name()] = {
                "is_default": True,
                "is_active": s.is_active.get(),
                "short_name": s.short_name.get(),
            }

        return data

    def summary(self):
        current_site = self.working_sites[self.current_site_name.get()]
        exchange_site = self.exchange_sites[self.exchange_site_name.get()]

        if not current_site.configured.get():
            return (
                "<font color=#D5000D>"
                f"Current site <b>{current_site.name()}</b> "
                "needs to be configured</font>"
            )

        if not exchange_site.configured.get():
            return (
                "<font color=#D5000D>"
                f"Exchange site <b>{exchange_site.name()}</b> "
                "needs to be configured.</font>"
            )


class Admin(flow.Object):

    ICON = ("icons.gui", "team-admin")

    _project = flow.Parent()

    project_settings = flow.Child(ProjectSettings).injectable()
    users = flow.Child(Users).ui(show_filter=True, sort_by="ID").injectable()
    multisites = flow.Child(MultisiteConfig).ui(label="Sites")
    kitsu = flow.Child(KitsuConfig)

    dependency_templates = flow.Child(DependencyTemplates)

    user_environment = flow.Child(UserEnvironment).ui(
        expanded=False, label="Session environment"
    )
    default_applications = flow.Child(DefaultApps).ui(expanded=False).injectable()
    runner_handlers = flow.Child(RunnerHandlers).ui(expanded=False)

    login_page = flow.Child(LoginPage).ui(hidden=True)

    store = flow.Child(EntityStore)

    def _fill_ui(self, ui):
        user = self.root().project().get_user()
        ui["hidden"] = user is None or user.status.get() != "Admin"


class Project(flow.Object):

    log_out_action = flow.Child(LogOut).ui(label="Log out")
    goto_my_tasks = flow.Child(GoToMyTasks).ui(label="My Tasks")
    mytasks = flow.Child(MyTasks).ui(hidden=True)
    search = flow.Child(Search).ui(hidden=True)
    import_files = flow.Child(ImportFilesAction).ui(dialog_size=(800, 600))

    user = flow.Child(UserProfile)
    asset_lib = flow.Child(Assets).ui(expanded=True)
    sequences = flow.Child(SequenceCollection).ui(expanded=True)
    admin = flow.Child(Admin)
    synchronization = flow.Child(Synchronization).ui(expanded=True)

    _RUNNERS_FACTORY = None

    def settings(self):
        return self.admin.project_settings

    def get_root(self, alternative=None):
        """
        alternative can be used if root_dir.get() returns None
        """
        root_dir = self.admin.multisites.root_dir.get()
        if root_dir is None and alternative != None:
            root_dir = alternative
        return root_dir

    def get_temp_folder(self):
        return self.admin.multisites.temp_dir.get()

    def set_user_name(self, username):
        """
        Sets the name of the current user.
        """
        project_settings_folder = self.project_settings_folder()

        if not os.path.exists(project_settings_folder):
            os.makedirs(project_settings_folder)

        user_file = os.path.join(project_settings_folder, "current_user.json")

        with open(user_file, "w+") as f:
            user_config = dict(username=username)
            json.dump(user_config, f)

        self.user.current_user_id.touch()

    def get_user_name(self):
        """
        Returns the name of the current user.
        """
        return self.user.current_user_id.get()

    def get_user(self, name=None):
        """
        If provided, returns the user of this project with the
        given `name`. Return the project's current user otherwise.

        In any case, None is returned if no user is found.
        """
        if name is None:
            name = self.get_user_name()

        if not self.admin.users.has_mapped_name(name):
            return None

        return self.admin.users[name]

    def get_users(self):
        return self.admin.users

    def get_current_site(self):
        """
        Returns the site within which the current
        session is beeing run.
        """
        return self.get_working_site(self.admin.multisites.current_site_name.get())

    def get_current_site_name(self):
        return self.admin.multisites.current_site_name.get()

    def get_working_site(self, name):
        """
        Returns the working site of the project
        with the given name.
        """
        return self.get_working_sites()[name]

    def get_exchange_site(self):
        """
        Returns the first exchange site found in
        project's registered site list.
        """
        return self.get_exchange_sites()[self.admin.multisites.exchange_site_name.get()]

    def set_exchange_site(self, name):
        return self.admin.multisites.exchange_site_name.set(name)

    def get_working_sites(self):
        return self.admin.multisites.working_sites

    def get_exchange_sites(self):
        return self.admin.multisites.exchange_sites

    def is_admin(self, username):
        try:
            return self.admin.users.is_admin(username)
        except flow.exceptions.MappedNameError:
            # Unregistered user not admin by default
            return False

    def show_login_page(self):
        kitsu_api = self.kitsu_api()
        valid_host = kitsu_api.host_is_valid()

        if not valid_host:
            logged_in = False
        else:
            logged_in = kitsu_api.current_user_logged_in()

        if not logged_in:
            try:
                f = open("%s/kitsu_config.json" % self.user_settings_folder(), "r")
            except IOError:
                logged_in = False
            else:
                kitsu_config = json.load(f)
                kitsu_api.set_host(kitsu_config["kitsu_host"])
                kitsu_api.set_tokens(kitsu_config["tokens"])

                logged_in = kitsu_api.current_user_logged_in()

        return not kitsu_api.host_is_valid() or not logged_in

    def update_kitsu_host(self, server_url):
        kitsu_api = self.kitsu_api()
        kitsu_api.set_server_url(server_url)
        kitsu_api.set_host(server_url + "/api")

        return kitsu_api.host_is_valid()

    def log_in(self, login, password):
        kitsu = self.kitsu_api()
        self.update_kitsu_host(self.admin.kitsu.server_url.get())

        # Check if the login matches a registered user
        user = self.admin.users.get_user(login)

        # Authenticate to Kitsu
        if user:
            logins = user.login.get()

            for saved_login in logins:
                status = kitsu.log_in(saved_login, password)
                if not status:
                    continue
                
                if logins.index(saved_login) != 0:
                    user.login.set(logins[::-1]) # Reversed
                break
        elif not kitsu.log_in(login, password):
            # Invalid credentials
            return False

        # Create user if not exists
        if user is None:
            user_data = gazu.client.get_current_user()
            user = self.admin.users.add_user(
                name=re.sub("[^a-zA-Z]", "", strip_accents(user_data["full_name"]).lower()),
                login=login,
            )

        self.set_user_name(user.name())

        # Save authentification tokens

        user_settings_folder = self.user_settings_folder()
        if not os.path.exists(user_settings_folder):
            os.makedirs(user_settings_folder)

        tokens = kitsu.get_tokens()
        kitsu_config = {}
        kitsu_config["tokens"] = tokens
        kitsu_config["kitsu_host"] = kitsu.get_host()

        if user_settings_folder is not None:
            with open("%s/kitsu_config.json" % user_settings_folder, "w+") as f:
                json.dump(kitsu_config, f)

        return True
    
    def log_out(self):
        self.kitsu_api().log_out()

    def kitsu_config(self):
        return self.admin.kitsu

    def kitsu_api(self):
        return self.admin.kitsu.gazu_api

    def kitsu_bindings(self):
        return self.admin.kitsu.bindings

    def get_contextual_view(self, context_name):
        if context_name == "settings":
            return self.admin.project_settings.settings

    def get_default_contextual_edits(self, context_name):
        if context_name == "settings":
            return dict(
                project_name=self.name(),
                project_code=self.admin.project_settings.project_code.get(),
                user=self.get_user_name(),
                user_code=self.get_user().get_code(),
                site=self.get_current_site_name(),
                site_code=self.get_current_site().get_code(),
                frame_rate=self.admin.project_settings.frame_rate.get(),
                width=self.admin.project_settings.width.get(),
                height=self.admin.project_settings.height.get(),
                default_shot_layout_files="{sequence}_{shot}_layout.blend, {sequence}_{shot}_layout-movie.mov",
                default_shot_animation_files="{sequence}_{shot}_animation.blend, {sequence}_{shot}_animation-movie.mov, {sequence}_{shot}_animation-export.abc",
                default_asset_model_files="{asset_name}_model.blend, {asset_name}_model-movie.mov, {asset_name}_model-export.abc",
                default_asset_rig_files="{asset_name}_rig.blend, {asset_name}_rig-turnaround.mov",
                project_thumbnail="{ROOT_DIR}TECH/{PROJECT}_thumbnail.png",
            )

    def project_settings_folder(self):
        return os.path.join(pathlib.Path.home(), ".libreflow", self.name())

    def user_settings_folder(self):
        """
        DEPRECATED ! TO DELETE ?
        """
        return os.path.join(self.project_settings_folder(), self.get_user_name())

    def get_default_file_presets(self):
        """
        Must return an instance of libreflow.baseflow.file.DefaultFileMap.
        """
        return self.admin.project_settings.default_files

    def get_default_tasks(self):
        return self.root().project().get_task_manager().default_tasks

    def get_project_thumbnail2(self):
        image = self.admin.project_settings.project_thumbnail.get()
        return image

    def get_project_thumbnail(self):
        contextual_dict = get_contextual_dict(self, "settings")
        contextual_dict["ROOT_DIR"] = self.get_root()
        if "project_thumbnail" not in contextual_dict:
            return None
        path = None

        try:
            path = contextual_dict["project_thumbnail"].format(**contextual_dict)
        except KeyError:
            return None

        if path and os.path.exists(path):
            return path
        else:
            return None

    def update_user_environment(self):
        self.admin.user_environment.update()

    def _register_runners(self):
        self._RUNNERS_FACTORY.ensure_runner_type(DefaultEditor)
        self._RUNNERS_FACTORY.ensure_runner_type(Blender)
        self._RUNNERS_FACTORY.ensure_runner_type(Krita)
        self._RUNNERS_FACTORY.ensure_runner_type(KritaRunner)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffects)
        self._RUNNERS_FACTORY.ensure_runner_type(AfterEffectsRender)
        self._RUNNERS_FACTORY.ensure_runner_type(VSCodium)
        self._RUNNERS_FACTORY.ensure_runner_type(NotepadPP)
        self._RUNNERS_FACTORY.ensure_runner_type(MarkSequenceRunner)
        self._RUNNERS_FACTORY.ensure_runner_type(Explorer)
        self._RUNNERS_FACTORY.ensure_runner_type(MinioFileUploader)
        self._RUNNERS_FACTORY.ensure_runner_type(MinioFileDownloader)
        self._RUNNERS_FACTORY.ensure_runner_type(SessionWorker)
        self._RUNNERS_FACTORY.ensure_runner_type(Firefox)
        self._RUNNERS_FACTORY.ensure_runner_type(ImageMagick)
        self._RUNNERS_FACTORY.ensure_runner_type(RV)
        self._RUNNERS_FACTORY.ensure_runner_type(Nuke)
        self._RUNNERS_FACTORY.ensure_runner_type(PremierePro)
        self._RUNNERS_FACTORY.ensure_runner_type(Mrviewer)
        self._RUNNERS_FACTORY.ensure_runner_type(TvPaint)
        self._RUNNERS_FACTORY.ensure_runner_type(Photoshop)
        self._RUNNERS_FACTORY.ensure_runner_type(PythonRunner)

    def ensure_runners_loaded(self):
        session = self.root().session()
        subprocess_manager = session.get_actor("SubprocessManager")

        if self._RUNNERS_FACTORY is None:
            self._RUNNERS_FACTORY = subprocess_manager.create_new_factory(
                "Libre Flow Tools"
            )
            self._register_runners()

        subprocess_manager.ensure_factory(self._RUNNERS_FACTORY)

    def get_factory(self):
        self.ensure_runners_loaded()
        return self._RUNNERS_FACTORY

    def get_entity_store(self):
        return self.admin.store

    def get_entity_manager(self):
        raise NotImplementedError(
            (
                "This method must return the entity manager holding "
                "the collections of entities of this project."
            )
        )

    def get_task_manager(self):
        raise NotImplementedError(
            (
                "This method must return the task manager holding "
                "the default tasks and task templates of this project."
            )
        )

    def get_sync_manager(self):
        return self.synchronization.synchronize_files

    def get_import_files(self):
        return self.admin.project_settings.import_files_object.get()

    def touch(self):
        super(Project, self).touch()
        self.ensure_runners_loaded()
        self.update_user_environment()

    def _fill_ui(self, ui):
        if self._RUNNERS_FACTORY is None:
            self.ensure_runners_loaded()
        
        ui["custom_page"] = "libreflow.baseflow.ui.homepage.HomepageWidget"
        self.touch()
