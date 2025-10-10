from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui
from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager
from kabaret.app import resources

from ...resources.icons import libreflow as _

from .qmodel import QFileListModel
from .delegate import QFileListDelegate


class FileActionsButton(QtWidgets.QToolButton):
    """
    Holds the file's action shortcuts displayed in the file list.
    """
    def __init__(self, flow_page, file_type, row, action_manager, controller):
        super(FileActionsButton, self).__init__()
        self.controller = controller
        self.action_manager = action_manager
        self.file_type = file_type
        self.row = row
        self.flow_page = flow_page
        self.build()
    
    def build(self):
        self.setIcon(resources.get_icon(('icons.gui', 'menu')))
        self.setIconSize(QtCore.QSize(16, 16))
        self.setStyleSheet('QToolButton::menu-indicator { image: none; }')
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setFixedWidth(30)

        # Add actions
        self.menu = QtWidgets.QMenu('File actions')
        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setArrowType(QtCore.Qt.NoArrow)
        self.setMenu(self.menu)
    
    def mousePressEvent(self, event):
        data = self.controller.file_data(self.file_type, self.row)
        data.update_actions()

        has_actions = self.action_manager.update_oid_menu(
            data.file_oid, self.menu, with_submenus=True
        )

        if data.ref_oid is not None:
            if has_actions:
                self.menu.addSeparator()
            
            a = self.menu.addAction(
                'Unlink', lambda oid=data.ref_oid, file_type=self.file_type: self.controller.remove_ref(oid, file_type)
            )
            a.setIcon(resources.get_icon(('icons.gui', 'ref-broken')))

        super(FileActionsButton, self).mousePressEvent(event)

    def _on_action_menu_triggered(self, action):
        self.flow_page.show_action_dialog(action.oid)


class FileListItemWidget(QtWidgets.QWidget):
    """
    Represents a file in a list.
    """
    def __init__(self, flow_page, file_type, row, action_manager, controller):
        super(FileListItemWidget, self).__init__()
        self.controller = controller
        self.action_manager = action_manager
        self.file_type = file_type
        self.row = row
        self.flow_page = flow_page
        self.rect_text_width = 0
        self.metrics_text_width = 0
        
        self.build()
        self.installEventFilter(self)

    def build(self):
        self.data = self.controller.file_data(self.file_type, self.row)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_lo = QtWidgets.QHBoxLayout(self.buttons_widget)
        self.buttons_lo.setContentsMargins(0,0,0,0)
        self.buttons_lo.setSpacing(0)
       
        self.button_secondary = FileActionsButton(self.flow_page, self.file_type, self.row, self.action_manager, self.controller)
        self.button_secondary.setFixedSize(25, 25)
        self.button_secondary.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)

        self.buttons_main = []

        for fa in self.data.main_actions:
            b = QtWidgets.QPushButton('')
            b.setIcon(resources.get_icon(fa.icon))
            b.setToolTip(fa.label)
            b.setFixedSize(self.button_secondary.size())
            b.setStyleSheet('QPushButton { background-color: rgba(255, 255, 255, 0); }')
            b.clicked.connect(lambda checked=False, a=fa: self._on_action_menu_triggered(a))
            self.buttons_main.append(b)
        
        hlo = QtWidgets.QHBoxLayout()
        hlo.addStretch(1)

        for b in self.buttons_main:
            self.buttons_lo.addWidget(b)
        
        hlo.addWidget(self.buttons_widget)
        hlo.addWidget(self.button_secondary)
        hlo.setSpacing(0)
        hlo.setContentsMargins(4, 0, 4, 0)
        self.setLayout(hlo)

    def get_buttons_count(self):
        count = 0
        for i in reversed(range(self.buttons_lo.count())):
            widget = self.buttons_lo.itemAt(i).widget()
            if widget.isVisible():
                count += 1
        
        return count
    
    # Make main actions responsive
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Resize or event.type() == QtCore.QEvent.Paint:
            if self.rect_text_width < self.metrics_text_width:
                for btn in self.buttons_main:
                    if btn.isVisible():
                        btn.hide()
                        break

            elif (self.rect_text_width - self.metrics_text_width) >= self.button_secondary.width():
                for btn in reversed(self.buttons_main):
                    if not btn.isVisible():
                        btn.show()
                        break

            return True

        return False

    def _on_action_menu_triggered(self, action):
        self.flow_page.show_action_dialog(action.oid)


class FileList(QtWidgets.QTableView):
    """
    Represents a list of files of a given type (input, output, work) present in a task.
    """
    def __init__(self, task_widget, file_type):
        super(FileList, self).__init__()
        self.task_widget = task_widget
        self.controller = task_widget.controller
        self.session = task_widget.controller.session
        self.file_type = file_type
        
        self.model = QFileListModel(self.controller, file_type)
        self.setModel(self.model)
        self.setItemDelegate(QFileListDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(35)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignVCenter)
        self.horizontalHeader().setStretchLastSection(True)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

        self.action_manager = ObjectActionMenuManager(
            task_widget.session, task_widget.page.show_action_dialog, 'Flow.map'
        )
        self.action_menu = QtWidgets.QMenu()

        self.update()

        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self.doubleClicked.connect(self._on_item_double_clicked)
        self.installEventFilter(self)
    
    def update(self):
        for row in range(self.model.rowCount()):
            self.setIndexWidget(
                self.model.index(row, 0),
                FileListItemWidget(self.controller.task_widget.page, self.file_type, row, self.action_manager, self.controller)
            )

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Hide:
            # Reset selection when the widget is hidden
            QtWidgets.QApplication.instance().selectChanged.emit(None)
            return True
        
        return super().eventFilter(source, event)

    def selectionChanged(self, selected, deselected):
        if selected.indexes():
            index = selected.indexes()[0]
            self.controller.update_selected(self.file_type, index.row())
        else:
            QtWidgets.QApplication.instance().selectChanged.emit(None)
            self.task_widget.setFocus()
    
    def mousePressEvent(self, event):
        super(FileList, self).mousePressEvent(event)
        
        if event.button() == QtCore.Qt.RightButton:
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.emit(event.pos())
            self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        else:
            if event.button() == QtCore.Qt.LeftButton:
                if not self.indexAt(event.pos()).isValid():
                    self.controller.clear_selected()
                else:
                    QtWidgets.QApplication.instance().selectChanged.emit(self.controller.selected_file().file_oid)

    def dragEnterEvent(self, event):
        if not event.mouseButtons() & QtCore.Qt.LeftButton:
            event.ignore()
            return

        if self.session.cmds.Flow.can_handle_mime_formats(
            event.mimeData().formats()
        ):
            event.acceptProposedAction()
        else:
            super(FileList, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self.session.cmds.Flow.can_handle_mime_formats(
                event.mimeData().formats()
        ):
            event.acceptProposedAction()
        else:
            super(FileList, self).dragMoveEvent(event)
    
    def dropEvent(self, event):
        if event.mimeData().text().startswith('file:///'):
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))
            
            return self.controller.handle_dropped_files(links)

        md = {}
        for format in event.mimeData().formats():
            md[format] = event.mimeData().data(format).data()
        oids, urls = self.session.cmds.Flow.from_mime_data(md)

        if not oids and not urls:
            return False  # let the event propagate up
        
        self.controller.handle_dropped_oids(oids, self.file_type)
    
    def supportedDropActions(self):
        return QtCore.Qt.CopyAction
    
    def beginResetModel(self):
        self.model.beginResetModel()

    def endResetModel(self):
        self.model.endResetModel()
    
    def _on_context_menu_requested(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        
        data = self.controller.file_data(self.file_type, index.row())
        has_actions = self.action_manager.update_oid_menu(
            data.file_oid, self.action_menu, with_submenus=True
        )

        if data.ref_oid is not None:
            if has_actions:
                self.action_menu.addSeparator()
            
            a = self.action_menu.addAction(
                'Unlink', lambda oid=data.ref_oid, file_type=self.file_type: self.controller.remove_ref(oid, file_type)
            )
            a.setIcon(resources.get_icon(('icons.gui', 'ref-broken')))

        if has_actions or data.ref_oid is not None:
            self.action_menu.exec_(self.viewport().mapToGlobal(pos))
    
    def _on_item_double_clicked(self, index):
        data = self.controller.file_data(self.file_type, index.row())
        
        if data.activate_oid is None:
            self.controller.goto(data.oid)
        else:
            self.controller.show_action_dialog(data.activate_oid)


class FileListActionsWidget(QtWidgets.QWidget):
    """
    Holds actions related to a file list widget.
    """
    def __init__(self, flow_page, controller):
        super(FileListActionsWidget, self).__init__()
        self.controller = controller
        self.flow_page = flow_page
        self.build()
    
    def build(self):
        hlo = QtWidgets.QHBoxLayout()
        hlo.addStretch(1)

        for fa in self.controller.task_file_actions():
            b = QtWidgets.QPushButton('')
            b.setIcon(resources.get_icon(fa.icon))
            b.setToolTip(fa.label)
            b.setFixedWidth(40)
            # b.setStyleSheet('background-color: rgba(255, 255, 255, 0);')
            b.clicked.connect(lambda checked=False, a=fa: self._on_action_menu_triggered(a))
            hlo.addWidget(b)
        
        hlo.setSpacing(0)
        hlo.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hlo)

    def _on_action_menu_triggered(self, action):
        self.flow_page.show_action_dialog(action.oid)


class FileListsWidget(QtWidgets.QWidget):
    """
    Displays the task's input, output and working files.
    """
    def __init__(self, task_widget, parent):
        super(FileListsWidget, self).__init__(parent)
        self.task_widget = task_widget
        self.file_lists = {}
        self.build()
    
    def build(self):
        self.file_lists['Inputs'] = FileList(self.task_widget, 'Inputs')
        self.file_lists['Works'] = FileList(self.task_widget, 'Works')
        self.file_lists['Outputs'] = FileList(self.task_widget, 'Outputs')
        self.file_buttons = FileListActionsWidget(self.task_widget.page, self.task_widget.controller)

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.file_lists['Inputs'], 0, 0)
        glo.addWidget(self.file_lists['Works'], 0, 1)
        glo.addWidget(self.file_lists['Outputs'], 0, 2)
        glo.addWidget(self.file_buttons, 1, 0, 1, 3)
        glo.setSpacing(2)
        glo.setContentsMargins(0, 0, 0, 0)
        self.setLayout(glo)
    
    def clear_list_selection(self, file_type):
        self.file_lists[file_type].clearSelection()
    
    def clear_selection(self):
        for l in self.file_lists.values():
            l.clearSelection()
    
    def beginResetModel(self, file_type):
        self.file_lists[file_type].beginResetModel()

    def endResetModel(self, file_type):
        self.file_lists[file_type].endResetModel()
    
    def beginResetModels(self):
        for l in self.file_lists.values():
            l.beginResetModel()

    def endResetModels(self):
        for l in self.file_lists.values():
            l.endResetModel()
    
    def update(self, file_type):
        self.file_lists[file_type].update()
    
    def updateLists(self):
        for l in self.file_lists.values():
            l.update()
