from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui
from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager
from kabaret.app import resources
from PySide6 import QtCharts

from ...resources.icons import gui as _

from .qmodel import QFileHistoryModel, QFileStatutesModel
from .delegate import QFileHistoryDelegate, QFileStatutesDelegate
from .file_history import HistoryGraph


class RevisionStatutesButton(QtWidgets.QPushButton):

    def __init__(self):
        super(RevisionStatutesButton, self).__init__('')
        icon = QtGui.QIcon()
        icon.addFile(
            resources.get('icons.gui', 'location-worldwide'),
            # size=QtCore.QSize(30, 30),
            state=QtGui.QIcon.On)
        icon.addFile(
            resources.get('icons.gui', 'location-worldwide-disabled'),
            # size=QtCore.QSize(30, 30),
            state=QtGui.QIcon.Off)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(25, 25))
        self.setCheckable(True)
        self.setToolTip('Show/hide file locations')
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setFixedWidth(40)


class SitesViewItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, tree, controller, site_name, ordered_sites=None):
        super(SitesViewItem, self).__init__()
        self.tree = tree
        self.site_name = site_name
        self.controller = controller

        self.setFlags(self.flags() | QtCore.Qt.ItemIsUserCheckable)

        text = f"{self.controller.get_short_name(self.site_name)}"

        if self.controller.get_working_site_type(site_name) == "Studio":
            icon = resources.get_icon(("icons.gui", "home"))
        else:
            icon = resources.get_icon(("icons.gui", "user"))

        self.setIcon(0, icon)
        if self.site_name == self.controller.current_site_name:
            self.setText(0, f"{text} (current site)")
            self.setCheckState(1, QtCore.Qt.Checked)
            return

        self.setText(0, text)

        if site_name in ordered_sites:
            self.setCheckState(1, QtCore.Qt.Checked)
        else:
            self.setCheckState(1, QtCore.Qt.Unchecked)


class SitesView(QtWidgets.QTreeWidget):

    def __init__(self, controller):
        super(SitesView, self).__init__()
        self.controller = controller
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setColumnCount(2)

        headerH = ["Sites", "Always Display"]
        self.setHeaderLabels(headerH)
        self.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.itemChanged.connect(self._on_item_changed)

        self.setDragDropMode(self.DragDropMode.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def refresh(self):
        if self.topLevelItemCount() > 1:
            self.clear()

        sites = self.controller.sites()
        ordered_sites = self.controller.get_only_studios()

        if "..." in ordered_sites:
            ordered_sites = ordered_sites[:-1]

        if self.controller.ensure_presets():
            sites = self.controller.ensure_presets().keys()
            ordered_sites = self.controller.get_presets()

        for index, site in enumerate(sites):
            item = SitesViewItem(self, self.controller, site, ordered_sites)
            self.addTopLevelItem(item)
            self.resizeColumnToContents(index)

            if not self.controller.get_non_active_sites(site):
                item.setForeground(0, QtGui.QColor("gray"))

    def _on_item_changed(self, item, column):
        if item.site_name == self.controller.current_site_name:
            icon = resources.get_icon(("icons.libreflow", "warning"))
            item.setIcon(1, icon)
            item.setToolTip(1, "Current site always display in second column")


class OptionHistoryView(QtWidgets.QDialog):

    def __init__(self, header, controller):
        super(OptionHistoryView, self).__init__()
        self.file_header = header
        self.controller = controller
        self.build()

    def build(self):
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setWeight(QtGui.QFont.Bold)
        self.label_name = QtWidgets.QLabel("Displaying Site History")
        self.label_name.setFont(font)
        self.label_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.sites_list = SitesView(self.controller)

        self.save_button = QtWidgets.QPushButton("Save")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.save_button)
        hlo.addWidget(self.cancel_button)

        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self.label_name)
        vlo.addWidget(self.sites_list)
        vlo.addLayout(hlo)
        self.setLayout(vlo)

        self.save_button.clicked.connect(self._on_save_button_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_button_clicked)

    def _on_save_button_clicked(self):
        ordered_site_names_dict = {}

        for index in range(self.sites_list.topLevelItemCount()):
            item = self.sites_list.topLevelItem(index)

            item.checkState(1)
            ordered_site_names_dict[item.site_name] = True if item.checkState(1) == QtCore.Qt.Checked else False

        self.controller.update_preset(ordered_site_names_dict)
        self.file_header.button_display_more.setChecked(False)
        self.file_header.button_display_more.clicked.emit()

        self.accept()

    def _on_cancel_button_clicked(self):
        self.close()


class FileHeader(QtWidgets.QWidget):

    def __init__(self, file_widget):
        super(FileHeader, self).__init__()
        self.file_widget = file_widget
        self.controller = file_widget.controller
        self.build()
    
    def build(self):
        self.label_icon = QtWidgets.QLabel('')
        self.label_icon.setFixedWidth(40)
        self.label_icon.setAlignment(QtCore.Qt.AlignCenter)

        font = QtGui.QFont()
        font.setPointSize(15)
        font.setWeight(QtGui.QFont.Bold)
        self.label_name = QtWidgets.QLabel('')
        self.label_name.setFont(font)
        self.label_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        self.kitsu_icon = QtWidgets.QLabel('')
        self.kitsu_icon.setFixedWidth(40)
        self.kitsu_icon.setAlignment(QtCore.Qt.AlignCenter)

        self.button_goto_source = QtWidgets.QPushButton()
        icon = resources.get_icon(('icons.gui', 'share-symbol'))
        self.button_goto_source.setIcon(icon)
        self.button_goto_source.setIconSize(QtCore.QSize(18, 18))
        self.button_goto_source.setFixedHeight(30)
        self.button_goto_source.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.button_statutes = RevisionStatutesButton()

        self.button_option_sites = QtWidgets.QPushButton()
        icon = resources.get_icon(('icons.gui', 'cog-wheel-silhouette'))
        self.button_option_sites.setIcon(icon)
        self.button_option_sites.setIconSize(QtCore.QSize(22, 22))
        self.button_option_sites.setToolTip('Options Displaying Site History')
        self.button_option_sites.setFixedHeight(40)
        self.button_option_sites.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.button_option_sites.hide()

        self.button_display_more = QtWidgets.QPushButton("Display More")
        self.button_display_more.setToolTip('Display All Sites')
        self.button_display_more.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.button_display_more.hide()
        self.button_display_more.setCheckable(True)
        
        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.label_icon)
        hlo.addWidget(self.label_name)
        hlo.addWidget(self.kitsu_icon)
        hlo.addStretch(1)
        hlo.addWidget(self.button_goto_source)
        hlo.addStretch(1)
        hlo.addWidget(self.button_display_more)
        hlo.addWidget(self.button_option_sites)
        hlo.addWidget(self.button_statutes)
        hlo.setContentsMargins(0, 0, 0, 0)
        hlo.setSpacing(2)
        self.setLayout(hlo)

        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor('#303233'))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.setFixedHeight(40)

        self.button_goto_source.clicked.connect(self._on_button_goto_source_clicked)
        self.button_statutes.toggled.connect(self._on_button_statutes_toggled)
        self.button_display_more.clicked.connect(self._on_button_display_more_clicked)
        self.button_option_sites.clicked.connect(self._on_button_option_sites_clicked)
    
    def update(self):
        selected = self.controller.selected_file()
        pm = resources.get_pixmap(*selected.icon)
        self.label_icon.setPixmap(pm.scaled(28, 28, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.label_name.setText(selected.label)
        
        if selected.ref_oid is not None:
            self.button_goto_source.setText(selected.goto_source_display)
            self.button_goto_source.show()
        else:
            self.button_goto_source.hide()

        kitsu = resources.get_pixmap('icons.libreflow', 'kitsu')

        if selected.head_revision is not None:
            if selected.head_revision.status.get() == "on_kitsu":
                self.kitsu_icon.setPixmap(
                    kitsu.scaled(
                        20,
                        20,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation,
                    )
                )
            else:
                self.kitsu_icon.setPixmap(QtGui.QPixmap())
        else:
            self.kitsu_icon.setPixmap(QtGui.QPixmap())
    
    def toggle_file_statutes(self):
        self.button_statutes.setChecked(
            not self.button_statutes.isChecked()
        )
    
    def _on_button_goto_source_clicked(self, checked=False):
        selected = self.controller.selected_file()
        self.controller.goto(selected.goto_oid)
    
    def _on_button_statutes_toggled(self, checked):
        self.file_widget.set_show_statutes(checked)
        if checked:
            self.button_display_more.show()
            self.button_option_sites.show()
        else:
            self.button_display_more.hide()
            self.button_option_sites.hide()

    def _on_button_display_more_clicked(self, checked):
        self.file_widget.display_all_sites(checked)

        if checked:
            self.button_display_more.setText("Display Less")
        else:
            self.button_display_more.setText("Display More")

    def _on_button_option_sites_clicked(self):
        self.file_widget.show_option_view()


class FileHistoryView(QtWidgets.QTableView):
    """
    Represents the revision history of the active file.
    """
    def __init__(self, controller):
        super(FileHistoryView, self).__init__()
        self.controller = controller

        self.setModel(QFileHistoryModel(controller))
        self.setItemDelegate(QFileHistoryDelegate())
        self.verticalHeader().hide()
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignVCenter)
        self.horizontalHeader().setMinimumSectionSize(100)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 100)
        self.setColumnWidth(1, 110)
        self.setColumnWidth(2, 110)
        self.setColumnWidth(4, 100)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setShowGrid(False)
        # self.setSpan(0, 0, self.controller.selected_file_revision_count(), 1)

        self.action_manager = ObjectActionMenuManager(
            controller.session, controller.show_action_dialog, 'Flow.map'
        )
        self.action_menu = QtWidgets.QMenu()

        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self.doubleClicked.connect(self._on_item_double_clicked)

    def display_all_sites(self, checked):
        self.controller.display_all_sites(checked)

    def set_show_statutes(self, checked):
        if checked:
            fileStatutesModel = QFileStatutesModel(self.controller)
            self.setModel(fileStatutesModel)
            self.setItemDelegate(QFileStatutesDelegate())
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(0, 100)
        else:
            self.setModel(QFileHistoryModel(self.controller))
            self.setItemDelegate(QFileHistoryDelegate())
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
            self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
            self.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(0, 100)
            self.setColumnWidth(1, 100)
            self.setColumnWidth(2, 100)
            self.setColumnWidth(4, 100)

    def selected_revision(self):
        if len(self.selectedIndexes()) > 0:
            if isinstance(self.model(), QFileStatutesModel):
                return self.selectedIndexes()[0].data(role=QtCore.Qt.UserRole).oid
            elif isinstance(self.model(), QFileHistoryModel):
                return self.selectedIndexes()[0].data(role=QtCore.Qt.UserRole)[0].oid
        
        return None

    def selectionChanged(self, selected, deselected):
        # print('update_history_link_weights')
        self.controller.update_history_link_weights(
            [i.row() for i in self.selectionModel().selectedRows()]
        )
        # print(self.controller.link_weights)

        if len(self.selectedIndexes()) > 0:
            QtWidgets.QApplication.instance().selectChanged.emit(self.selected_revision())
        elif self.controller.selected_file():
            QtWidgets.QApplication.instance().selectChanged.emit(self.controller.selected_file().file_oid)

        super(FileHistoryView, self).selectionChanged(selected, deselected)

    def update_graph(self):
        self.model().dataChanged.emit(self.model().index(0, 0), self.model().index(self.model().rowCount() - 1, 0))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.emit(event.pos())
            self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        else:
            index = self.indexAt(event.pos())
            if index.isValid():
                QtWidgets.QApplication.instance().selectChanged.emit(
                    index.data(QtCore.Qt.UserRole).oid
                    if isinstance(self.model(), QFileStatutesModel)
                    else index.data(QtCore.Qt.UserRole)[0].oid
                )
            super(FileHistoryView, self).mousePressEvent(event)

    def _on_context_menu_requested(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return

        selected = self.selectionModel().selectedRows(0)

        if len(selected) > 1:
            oids = []
            for i in selected:
                data = self.controller.selected_file_revision_data(i.row())
                oids.append(data.oid)

            actions = self.action_manager.update_oids_menu(
                oids, self.action_menu, with_submenus=True
            )
        else:
            # Select right-clicked item
            self.selectionModel().select(
                index, QtCore.QItemSelectionModel.ClearAndSelect | QtCore.QItemSelectionModel.Rows
            )

            data = self.controller.selected_file_revision_data(index.row())
            actions = self.action_manager.update_oid_menu(
                data.oid, self.action_menu, with_submenus=True
            )

        if actions:
            self.action_menu.exec_(self.viewport().mapToGlobal(pos))

    def _on_item_double_clicked(self, index):
        data = self.controller.selected_file_revision_data(index.row())

        if data.activate_oid is None:
            self.controller.goto(data.oid)
        else:
            self.controller.show_action_dialog(data.activate_oid)


class FileStatutesView(QtWidgets.QTableView):
    """
    Represents the synchronisation statutes of the active file.
    """
    pass


class FileContent(QtWidgets.QWidget):

    def __init__(self, controller):
        super(FileContent, self).__init__()
        self.controller = controller
        self.build()
    
    def build(self):
        self.history_view = FileHistoryView(self.controller)
        self.label_loading = QtWidgets.QLabel('Loading history...')
        self.label_loading.setAlignment(QtCore.Qt.AlignCenter)
        font = self.label_loading.font()
        font.setPointSize(12)
        self.label_loading.setFont(font)
        # self.history_view.setRenderHint(QtGui.QPainter.Antialiasing)
        # self.history_graph = HistoryGraph()
        # self.history_graph_view = QtCharts.QChartView(self.history_graph)
        # self.history_graph_view.setRenderHint(QtGui.QPainter.Antialiasing)
        # self.history_graph_view.setFixedWidth(200)
        hlo = QtWidgets.QHBoxLayout()
        # hlo.addWidget(self.history_graph_view)
        hlo.addWidget(self.history_view)
        hlo.addWidget(self.label_loading)
        hlo.setSpacing(0)
        hlo.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hlo)

        self.label_loading.hide()
    
    def update(self, loading=False):
        if loading:
            self.history_view.hide()
            self.label_loading.show()
        else:
            self.history_view.show()
            self.label_loading.hide()


class FileWidget(QtWidgets.QWidget):
    """
    Displays the content of the task's selected file.
    """
    
    def __init__(self, task_widget, parent):
        super(FileWidget, self).__init__(parent)
        self.controller = task_widget.controller
        self.build()
    
    def build(self):
        self.header = FileHeader(self)
        self.content = FileContent(self.controller)
        self.option_sites = OptionHistoryView(self.header, self.controller)
        # self.option_sites.setVisible(False)
        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self.header)
        vlo.addWidget(self.content)
        vlo.setSpacing(0)
        vlo.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlo)
    
    def update(self, loading=False):
        self.header.update()
        self.content.update(loading)
    
    def beginResetHistoryModel(self):
        self.content.history_view.model().beginResetModel()

    def endResetHistoryModel(self):
        self.content.history_view.model().endResetModel()
    
    def set_show_statutes(self, b):
        self.content.history_view.set_show_statutes(b)

    def display_all_sites(self, b):
        self.content.history_view.display_all_sites(b)
    
    def toggle_file_statutes(self):
        self.header.toggle_file_statutes()

    def show_option_view(self):
        self.option_sites.sites_list.refresh()
        self.option_sites.setVisible(True)
