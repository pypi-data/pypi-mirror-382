from kabaret.app import resources
from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore
from kabaret.app.ui.gui.widgets.main_window import DockTitleBar, DockWidget, MainWindowManager


class DefaultDockTitleBar(DockTitleBar):

    def __init__(self, main_window_manager, dock, view):
        super(DockTitleBar, self).__init__(dock)
        self.mwm = main_window_manager
        self.dock = dock
        self.dock.topLevelChanged.connect(self.on_floating)
        self.view = view

        self.maximized = False
        self.installed = False
        self.btn_size = 33

        lo = QtWidgets.QVBoxLayout(self)
        lo.setSpacing(0)
        lo.setContentsMargins(0,0,0,0)

        container = QtWidgets.QFrame()
        container.setObjectName('DockBackground')
        lo.addWidget(container)
        
        container_lo = QtWidgets.QGridLayout(container)
        container_lo.setContentsMargins(0,0,9,0)

        self.btn_view_menu = QtWidgets.QToolButton()
        self.btn_view_menu.setObjectName('DockButton')
        self.btn_view_menu.setIcon(resources.get_icon(('icons.gui', 'menu_dots')))
        self.btn_view_menu.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_view_menu.setToolTip('View Options')
        self.btn_view_menu.setFixedSize(QtCore.QSize(self.btn_size, self.btn_size))

        self.title = QtWidgets.QLabel(self.view.view_title())

        self.btn_duplicate = QtWidgets.QPushButton()
        self.btn_duplicate.setObjectName('DockButton')
        self.btn_duplicate.setIcon(resources.get_icon(('icons.gui', 'duplicate')))
        self.btn_duplicate.setMaximumSize(QtCore.QSize(self.btn_size, self.btn_size))

        self.btn_maximize = QtWidgets.QPushButton()
        self.btn_maximize.setObjectName('DockButton')
        self.btn_maximize.setIcon(resources.get_icon(('icons.gui', 'maximize')))
        self.btn_maximize.setMaximumSize(QtCore.QSize(self.btn_size, self.btn_size))
        
        self.btn_close = QtWidgets.QPushButton()
        self.btn_close.setObjectName('DockButton')
        self.btn_close.setIcon(resources.get_icon(('icons.gui', 'close')))
        self.btn_close.setMaximumSize(QtCore.QSize(self.btn_size, self.btn_size))

        container_lo.addWidget(self.btn_view_menu, 0, 0, alignment=QtCore.Qt.AlignVCenter)
        container_lo.setColumnStretch(1, 1)
        container_lo.addWidget(self.title, 0, 0, 0, 5, alignment=QtCore.Qt.AlignCenter)
        container_lo.addWidget(self.btn_duplicate, 0, 2, alignment=QtCore.Qt.AlignVCenter)
        container_lo.addWidget(self.btn_maximize, 0, 3, alignment=QtCore.Qt.AlignVCenter)
        container_lo.addWidget(self.btn_close, 0, 4, alignment=QtCore.Qt.AlignVCenter)

        self.btn_maximize.clicked.connect(lambda checked=False, self=self: self.mwm.toggle_maximized_dock(self))
        self.btn_duplicate.clicked.connect(lambda checked=False: self.view.create_view())
        self.btn_close.clicked.connect(lambda checked=False: self.dock.close())

        try:
            self.view.set_on_view_title_change(self.on_view_title_change)
        except Exception as err:
            self.installed = False
            raise err
        else:
            try:
                self.install_tools()
            except Exception as err:
                self.installed = False
                raise err
            else:
                self.installed = True

    def sizeHint(self):
        return QtCore.QSize(5, self.btn_size)

    def minimumSizeHint(self):
        return QtCore.QSize(5, self.btn_size)

    def get_container(self):
        return self.findChild(QtWidgets.QFrame, "DockBackground")
    
    def install_tools(self):
        self.btn_view_menu.setMenu(self.view.view_menu)
        self.btn_view_menu.setToolTip(self.view.view_menu.title())
        self.installed = True
    
    def uninstall_tools(self):
        # FIXME: shouldn't a Hide be enough?
        self.btn_view_menu.setMenu(None)
    
    def on_view_title_change(self):
        self.title.setText(self.view.view_title())
        self.dock.setWindowTitle(self.view.view_title())
    
    def on_floating(self, b):
        if b:
            self.dock.setTitleBarWidget(None)
            self.uninstall_tools()
        else:
            self.dock.setTitleBarWidget(self)
            self.install_tools()
        self.dock.setFocus()


class DefaultMainWindowManager(MainWindowManager):

    def create_docked_view_dock(self, view, hidden=False, area=None):
        dock = DockWidget(self.dock_closed, view.view_title(), self.main_window)
        tb = DefaultDockTitleBar(self, dock, view)
        if tb.installed:
            dock.setTitleBarWidget(tb)
        else:
            tb.deleteLater()

        dock.setWidget(view)

        dock.visibilityChanged.connect(
            lambda visible, dock=dock, view=view: self.dock_visibility_changed(visible, dock, view)
        )
        dock.dockLocationChanged.connect(
            lambda area, dock=dock, view=view: self.dock_location_changed(area, dock, view)
        )
        dock.setObjectName('Dock_%s_%i' % (view.view_title(), len(self._docks),))

        area = area or QtCore.Qt.LeftDockWidgetArea
        self.main_window.addDockWidget(area, dock)

        if hidden:
            dock.hide()

        # Auto tabify views of matching type name:
        target_view = self.find_docked_view(view.view_type_name(), area=area)
        if target_view is not None:
            target_view.dock_widget().show()
            dock.show()
            self.main_window.tabifyDockWidget(target_view.dock_widget(), dock)

        self._docks.append(dock)

        dock.setFocus()

        if len(self._docks) > 1:
            for d in self._docks:
                if d.titleBarWidget() and d.titleBarWidget().btn_maximize:
                    d.titleBarWidget().btn_maximize.setEnabled(True)
        else:
            for d in self._docks:
                if d.titleBarWidget() and d.titleBarWidget().btn_maximize:
                    d.titleBarWidget().btn_maximize.setEnabled(False)

        return dock

    def toggle_maximized_dock(self, titlebar):
        button = titlebar.btn_maximize
        keeped = titlebar.dock

        if self._maximised_to_restore is None:
            button.setIcon(resources.get_icon(('icons.gui', 'minimize')))
            self._maximised_to_restore = self.main_window.saveState()
            for d in self._docks:
                if d is keeped:
                    d.setFocus()
                    continue
                d.hide()

        else:
            button.setIcon(resources.get_icon(('icons.gui', 'maximize')))

            self.main_window.restoreState(self._maximised_to_restore)
            self._maximised_to_restore = None
