import re
import functools
import six
import os
import json
from libreflow.resources import styles
from libreflow.resources.styles.lfs_tech import LfsTechStyle
from libreflow.resources.styles.custom_style import CustomStyle
from libreflow.flows.resources.gui.styles.default_style import DefaultStyle
from kabaret.app import plugin
from kabaret.app.actors.flow.actor import ProjectRoot
from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, FlowView, FlowPage, CustomPageHost
from kabaret.app.ui.gui.widgets.flow.script_line import ScriptLine
from kabaret.app.ui.gui.widgets.flow.flow_form import FlowForm
from kabaret.app.ui.gui.widgets.flow.navigator import Navigator
from kabaret.app.ui.gui.widgets.flow.navigation_control import (
    NavigationOIDControls
)
from kabaret.app.ui.view import ViewMixin
from kabaret.app import resources

from ...search.view import SearchSettingsDialog
from ...search.data import icons as _

from ....resources.icons import gui as _

from .navigation_control import NavigationBar


class StoreLayoutAction(QtWidgets.QDialog):
    '''
    Dialog for saving a layout preset
    '''

    def __init__(self, parent):
        super(StoreLayoutAction, self).__init__(parent)
        self.setWindowTitle('Save Layout')
        self.session = parent.session

        self.build()
    
    def build(self):
        self.setLayout(QtWidgets.QVBoxLayout())

        # Create title
        title = QtWidgets.QLabel('<h2>Enter preset name</h2>')
        self.layout().addWidget(title)

        # Create combobox selection
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems(['']+list(self.session.get_layout_presets().keys()))
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('[^<>:"\/\\\|?*]+')))
        self.combo_box.currentTextChanged.connect(self._on_text_combobox_changed)
        self.layout().addWidget(self.combo_box)

        # Create checkbox for window position
        self.window_checkbox = QtWidgets.QCheckBox("Save Window Position")
        self.window_checkbox.setChecked(False)
        self.layout().addWidget(self.window_checkbox)

        # Create button
        b = QtWidgets.QPushButton(self)
        b.setText('Save Layout')
        b.clicked.connect(self._on_save_button_clicked)
        self.layout().addWidget(b)

        self.setFixedSize(350, 175)

    def _on_save_button_clicked(self):
        # Show a message box if a preset is gonna be overwrited
        if self.combo_box.currentText() in list(self.session.get_layout_presets().keys()):
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText(f'<h3>{self.combo_box.currentText()} already exists.</h3>')
            msgBox.setInformativeText("Do you want to replace it?")
            msgBox.setWindowIcon(resources.get_icon(('icons.gui', 'kabaret_icon')))
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            ret = msgBox.exec()

            return self.accept() if ret == QtWidgets.QMessageBox.Yes else None

        # Switch to error style if combobox is empty
        if self.combo_box.currentText() == '':
            self.combo_box.setProperty('error', True)
            self.combo_box.setToolTip('!!! ERROR: Preset name cannot be empty.')
            return self.combo_box.style().polish(self.combo_box)
        
        return self.accept()

    def _on_text_combobox_changed(self, text):
        # Disable error style when combobox input has changed
        if self.combo_box.property('error') == True:
            self.combo_box.setProperty('error', False)
            self.combo_box.style().polish(self.combo_box)


class DeleteLayoutAction(QtWidgets.QDialog):
    '''
    Dialog for delete a layout preset
    '''

    def __init__(self, parent):
        super(DeleteLayoutAction, self).__init__(parent)
        self.setWindowTitle('Delete Layout')
        self.session = parent.session

        self.build()
    
    def build(self):
        self.setLayout(QtWidgets.QVBoxLayout())

        # Create title
        title = QtWidgets.QLabel('<h2>Select layouts to delete</h2>')
        self.layout().addWidget(title)

        # Create user layout presets list
        self.listw = QtWidgets.QListWidget(self)
        for layout_name in list(self.session.get_layout_presets().keys()):
            item = QtWidgets.QListWidgetItem(layout_name)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.listw.addItem(item)
        self.layout().addWidget(self.listw)

        # Create button
        b = QtWidgets.QPushButton(self)
        b.setText('Delete')
        b.clicked.connect(self.accept)
        self.layout().addWidget(b)

        self.setFixedSize(375, 300)

    def getLayouts(self):
        # Return checked layouts
        checked = []
        for row in range(self.listw.count()):
            item = self.listw.item(row)
            if item.checkState():
                checked.append(item.text())
        
        return checked


class DefaultFlowPage(FlowPage):

    def __init__(self, parent, view, start_oid, root_oid):
        super(FlowPage, self).__init__(parent)

        self.view = view
        self.session = view.session

        self._navigator = Navigator(
            self.session, root_oid, start_oid
        )
        self._navigator.set_create_view_function(view.create_view)

        self.nav_bar = NavigationBar(self, self._navigator)
        self.nav_ctrl = self.nav_bar.nav_ctrl
        self.nav_oid = self.nav_bar.nav_oid_bar.nav_oid
        self.nav_oid_field = self.nav_bar.nav_oid_bar.nav_oid_field

        self.custom_page_host = CustomPageHost(self)
        self.custom_page_host.hide()
        self.form = FlowForm(self, self)

        lo = QtWidgets.QVBoxLayout()
        lo.addWidget(self.nav_bar)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        self.setLayout(lo)
        lo.addWidget(self.form, 100)
        lo.addWidget(self.custom_page_host, 100)

        self._navigator.add_on_current_changed(self.refresh)
        self._navigator.add_on_list_changed(self.nav_bar.nav_ctrl.update_controls)

        self._source_view_id = None

    def refresh(self):
        oid = self.current_oid()
        view_title = self.session.cmds.Flow.get_source_display(oid)
        self.view.set_view_title(view_title)

        self.clear()

        self.nav_oid.update_controls()
        self.nav_ctrl.update_controls()

        ui = self.session.cmds.Flow.get_object_ui(oid)
        self.view.set_show_navigation_bar(ui.get('navigation_bar', True))
        
        custom_page = ui.get('custom_page')
        if self.view.login_check:
            if self.show_login_page(oid):
                custom_page = 'libreflow.baseflow.LoginPageWidget'

        if custom_page:
            self.custom_page_host.host(oid, custom_page)
            self.form.hide()
        else:
            self.custom_page_host.unhost()
            self.form.show()
            self.form.build_roots(oid)

        # Update session layout autosave
        if self.session.layout_autosave and self.view.dock_widget() and self.session.layout_load is False:
            self.session.store_layout_preset(
                self.session.get_views_state(main_geometry=True),
                autosave=True
            )

        self.view.clearFocus()
        self.nav_oid_field.reject()
        self.view.setFocus()

    def show_login_page(self, oid):
        # Check if root is a Project
        o = self.session.get_actor('Flow').get_object(oid)
        root = o.root()
        if type(root) is ProjectRoot:
            if root.project().show_login_page():
                return True
        
        return False

    def receive_event(self, event, data):
        super(DefaultFlowPage, self).receive_event(event, data)
        if event == "focus_changed":
            # Update dock title bar background color depending on the active view status
            view_id = data["view_id"]

            titlebar = self.view.dock_widget().titleBarWidget()
            if not titlebar:
                return
            
            dock_background = titlebar.get_container()
            dock_background.setProperty(
                "current", True if view_id == self.view.view_id() else False
            )

            dock_background.style().polish(dock_background)
            dock_background.update()


class DefaultFlowView(FlowView):

    def __init__(self, session, view_id=None, hidden=False, area=None, oid=None, root_oid=None):
        self._start_oid = oid
        self._root_oid = root_oid
        self.options_menu = None
        self.layouts_menu = None
        self.themes_menu = None
        self.dev_menu = None
        self.script_line = None
        self.flow_page = None
        self.login_check = True

        try:
            parent = session.main_window_manager.main_window
        except AttributeError:
            raise TypeError(
                'The "%s" view cannont be used in a session without a main_window'%(
                    self.__class__.__name__
                )
            )
        ViewMixin.__init__(self, session, view_id)
        QtWidgets.QWidget.__init__(self, None)

        self.hidden = hidden
        self.area = area
        self._main_window_manager = session.main_window_manager

        # Restore correct DockWidgetArea enum value from string
        self.areaEnum = dict(
            LeftDockWidgetArea=QtCore.Qt.LeftDockWidgetArea,
            RightDockWidgetArea=QtCore.Qt.RightDockWidgetArea,
            TopDockWidgetArea=QtCore.Qt.TopDockWidgetArea,
            BottomDockWidgetArea=QtCore.Qt.BottomDockWidgetArea,
        )

        if isinstance(self.area, str):
            self.area = self.getAreaFromEnum()

        # Menu
        self.view_menu = QtWidgets.QMenu(self.view_title())
        if self.session.layout_manager:
            self.view_menu.aboutToShow.connect(self.build_layouts_menu)

        # Tools
        self._header_tools = {}
        self._header_tools_layout = QtWidgets.QHBoxLayout()

        content_widget = QtWidgets.QWidget(self)

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        self.setLayout(lo)

        hlo = QtWidgets.QHBoxLayout()
        hlo.setContentsMargins(0, 0, 0, 0)
        header_widgets_layout = QtWidgets.QHBoxLayout()
        hlo.addStretch()
        hlo.addLayout(header_widgets_layout, 100)
        hlo.addLayout(self._header_tools_layout)
        lo.addLayout(hlo)
        top_layout = QtWidgets.QHBoxLayout()
        lo.addLayout(top_layout)
        lo.addWidget(content_widget, 100)
        self._build(
            self, top_layout, content_widget,
            self, header_widgets_layout
        )

        self._update_menus()

        dock = self._main_window_manager.create_docked_view_dock(self, hidden=hidden, area=self.area)

        # This is needed for layout state
        # Multi instance view types must use another policy
        dock.setObjectName(self.view_id())
    
    def build_top(self, top_parent, top_layout, header_parent, header_layout):
        self.build_menu()

        # Script line
        self.script_line = ScriptLine(top_parent, self)
        self.script_line.hide()
        top_layout.addWidget(self.script_line, 100)

        # Search bar
        if self.session._search_index_uri is not None:
            self.search_dialog = SearchSettingsDialog(top_parent, self.session)
            self.options_menu.addSeparator()
            self.options_menu.addAction(
                resources.get_icon(('icons.search', 'magn-glass')),
                'Search settings',
                self._show_search_options
            )

    def build_menu(self):
        # Options Menu
        self.options_menu = self.view_menu.addMenu('Options')

        a = self.options_menu.addAction('Show Navigation Bar')
        a.setCheckable(True)
        a.setChecked(True)
        a.toggled.connect(self.set_show_navigation_bar)
        self._show_nav_bar_action = a

        a = self.options_menu.addAction('Show Hidden Relations')
        a.setCheckable(True)
        a.setChecked(False)
        a.toggled.connect(self.set_show_hidden_relations)

        a = self.options_menu.addAction('Show References')
        a.setCheckable(True)
        a.setChecked(False)
        a.toggled.connect(self.set_show_references_relations)

        self.options_menu.addAction('Create New View')

        #Themes
        self.themes_menu = self.options_menu.addMenu('Themes')

        themes_group = QtWidgets.QActionGroup(self)

        classic = self.themes_menu.addAction('Classic')
        classic.setCheckable(True)
        themes_group.addAction(classic)
        classic.triggered.connect(lambda: self._set_theme('classic'))

        dark = self.themes_menu.addAction('Dark')
        dark.setCheckable(True)
        themes_group.addAction(dark)
        dark.triggered.connect(lambda: self._set_theme('dark'))

        kabaret = self.themes_menu.addAction('Kabaret')
        kabaret.setCheckable(True)
        themes_group.addAction(kabaret)
        kabaret.triggered.connect(lambda: self._set_theme('kabaret'))

        if 'LF_THEME' in os.environ:
            if os.environ['LF_THEME'] == 'classic':
                classic.setChecked(True)
            elif os.environ['LF_THEME'] == 'dark':
                dark.setChecked(True)
            else :
                kabaret.setChecked(True)

        self.options_menu.addSeparator()
        self.options_menu.addAction(
            'Activate DEV Tools',
            self._activate_dev_tools
        )

        # Show layout menu when manager is enabled
        if self.session.layout_manager:
            self.build_layouts_menu()
        
        # Show Process View button
        a = self.view_menu.addAction('Processes')
        a.triggered.connect(self._show_processes_view_action)

    def build_layouts_menu(self):
        current_home_oid = ''
        if self.flow_page:
            current_home_oid = re.match('\/[^\/]*', self.flow_page.current_oid()).group(0)

        # Create menu if it doesn't exist or clear its contents for updating
        if self.layouts_menu is not None:
            self.layouts_menu.clear()
        else:
            self.layouts_menu = self.view_menu.addMenu('Layouts')
        
        # Split layouts by projects if we are on home page
        project_menus = {}
        if self.flow_page and current_home_oid.startswith('/Home'):
            projects_info = self.session.get_actor("Flow").get_projects_info()
            for project in projects_info:
                name = project[0]
                project_menus[name] = self.layouts_menu.addMenu(name)

        # Add user layout presets
        self.layout_icon = resources.get_icon(('icons.gui', 'ui-layout'))
        for name, layout in sorted(six.iteritems(self.session.get_layout_presets())):
            if project_menus:
                project_found = False

                for project_name, menu in project_menus.items():
                    for view_data in layout['views']:
                        view_state = view_data[-1]
                        if 'oid' in view_state:
                            if view_state['oid'].startswith(f'/{project_name}'):
                                a = menu.addAction(self.layout_icon, name)
                                a.triggered.connect(functools.partial(self._on_set_layout_action, layout))

                                project_found = True
                                break

                # Add directly to layout root menu if no project has been found in views
                if not project_found:
                    a = QtGui.QAction(self.layout_icon, name)
                    a.triggered.connect(functools.partial(self._on_set_layout_action, layout))

                    self.layouts_menu.insertAction(menu.menuAction(), a)
            else:
                # Show layouts only of current project
                for view_data in layout['views']:
                    view_state = view_data[-1]
                    if 'oid' in view_state:
                        if view_state['oid'].startswith(current_home_oid):
                            a = self.layouts_menu.addAction(self.layout_icon, name)
                            a.triggered.connect(functools.partial(self._on_set_layout_action, layout))
                            break

        # Add a separator
        self.layouts_menu.addSeparator()

        # Add store layout action
        a = self.layouts_menu.addAction(
            resources.get_icon(('icons.gui', 'plus-symbol-in-a-rounded-black-square')),
            'Store Current Layout'
        )
        a.triggered.connect(self._on_store_current_layout_action)

        # Add delete layout action
        a = self.layouts_menu.addAction(
            resources.get_icon(('icons.gui', 'minus-button')),
            'Delete Layout'
        )
        a.triggered.connect(self._on_delete_layout_action)

        # Add layout session autosaves
        recover_menu = self.layouts_menu.addMenu(
            resources.get_icon(('icons.gui', 'share-post-symbol')),
            'Recover Session Layout'
        )

        for name, layout in sorted(six.iteritems(self.session.get_layout_presets(autosaves=True)), reverse=True):
            a = QtGui.QAction(self.layout_icon, name, self.layouts_menu)
            a.triggered.connect(functools.partial(self._on_set_layout_action, layout))
            recover_menu.addAction(a)

    def build_page(self, main_parent):
        self.flow_page = DefaultFlowPage(
            main_parent, self, self._start_oid, self._root_oid
        )

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.addWidget(self.flow_page)
        self.flow_page.show()

        main_parent.setLayout(lo)
        self.flow_page.refresh()

    def toggle_login_check(self):
        self.login_check = False if self.login_check else True
        self.flow_page.refresh()
    
    def _activate_dev_tools(self):
        if self.dev_menu is not None:
            return
        self.dev_menu = self.view_menu.addMenu('[DEV]')

        self.dev_menu.addAction('Toggle Script Line', self.toggle_script_line)

        a = self.view_menu.addAction('Group Relations')
        a.setCheckable(True)
        a.setChecked(True)
        a.toggled.connect(self.set_group_relations)

        a = self.dev_menu.addAction('Show Protected Relations')
        a.setCheckable(True)
        a.setChecked(False)
        a.toggled.connect(self.set_show_protected_relations)

        a = self.dev_menu.addAction('Toggle Kitsu Login')
        a.setCheckable(True)
        a.setChecked(self.login_check)
        a.toggled.connect(self.toggle_login_check)

        self.dev_menu.addSeparator()

        self.dev_menu.addAction('Reload Projects Definition', self.reload_projects)

        self.toggle_script_line()
    
    def _set_theme(self, theme):
        styles_folder = os.path.dirname(styles.__file__)

        with open(styles_folder + '/current_style.txt', 'w') as f:
            d = dict(current_style = theme)
            json.dump(d, f)
        
        if theme == 'classic':
            LfsTechStyle().apply()
            LfsTechStyle().apply()
        elif theme == 'dark' :
            CustomStyle().apply()
            CustomStyle().apply()
        else :
            DefaultStyle().apply()
            DefaultStyle().apply()

    def _show_search_options(self):
        self.search_dialog.show()

    def _show_processes_view_action(self):
        subprocess_view = self.session.find_view('SubprocessView')
        if subprocess_view.isVisible() is False:
            subprocess_view.dock_widget().show()

    #
    #       LAYOUT MANAGEMENT
    #

    def isHidden(self):
        return self.hidden
    
    def areaPosition(self):
        return self.area

    def getAreaFromEnum(self):
        return self.areaEnum[self.area] if self.area in self.areaEnum else None

    def _on_set_layout_action(self, layout):
        # Don't delete us inside an signal handler from us:
        QtCore.QTimer.singleShot(
            100, lambda l=layout, s=self.session: s.set_views_state(l)
        )

    def _on_store_current_layout_action(self):
        dialog = StoreLayoutAction(self)

        # Store and update menu if accepted
        cancel = dialog.exec_() != dialog.Accepted
        name = dialog.combo_box.currentText().strip()
        dialog.deleteLater()
        if cancel or not name:
            return

        self.session.store_layout_preset(
            self.session.get_views_state(main_geometry=dialog.window_checkbox.isChecked()),
            name
        )
        self.build_layouts_menu()

    def _on_delete_layout_action(self):
        dialog = DeleteLayoutAction(self)

        # Delete and update menu if accepted
        cancel = dialog.exec_() != dialog.Accepted
        dialog.deleteLater()
        if cancel:
            return

        self.session.delete_layout_preset(dialog.getLayouts())
        self.build_layouts_menu()


class DefaultFlowViewPlugin:
    """
    Default Flow view.

    Will only be installed if no other view
    is registered under the "Flow" view type name.
    """

    @plugin(trylast=True)
    def install_views(session):
        if not session.is_gui():
            return

        type_name = DefaultFlowView.view_type_name()
        if not session.has_view_type(type_name):
            session.register_view_type(DefaultFlowView)
            session.add_view(type_name, area=QtCore.Qt.LeftDockWidgetArea)
