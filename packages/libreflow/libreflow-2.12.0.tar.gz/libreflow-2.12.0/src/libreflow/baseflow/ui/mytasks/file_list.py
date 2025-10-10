from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui
from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager
from kabaret.app import resources

from ....resources.icons import libreflow as _

from ..delegate import QFileListDelegate
from ..file_list import (
    FileList as BaseFileList,
    FileListItemWidget as BaseFileListItemWidget,
    FileActionsButton as BaseFileActionsButton
)
from .qmodel import QTaskFileListModel


class TaskFileActionsButton(BaseFileActionsButton):
    """
    Holds the file's action shortcuts displayed in the file list.
    """
    def __init__(self, widget):
        super(BaseFileActionsButton, self).__init__()
        self.widget = widget
        self.build()

    def mousePressEvent(self, event):
        data = self.widget.task_item.file_data[self.widget.row]
        data.update_actions()

        has_actions = self.widget.action_manager.update_oid_menu(
            data.oid(), self.menu, with_submenus=True
        )

        super(BaseFileActionsButton, self).mousePressEvent(event)

    def _on_action_menu_triggered(self, action):
        self.widget.flow_page.show_action_dialog(action.oid)


class TaskFileListItemWidget(BaseFileListItemWidget):
    """
    Represents a file in a list.
    """
    def __init__(self, task_item, flow_page, row, action_manager):
        super(BaseFileListItemWidget, self).__init__()
        self.task_item = task_item
        self.action_manager = action_manager
        self.row = row
        self.flow_page = flow_page
        self.rect_text_width = 0
        self.metrics_text_width = 0

        self.build()
        self.installEventFilter(self)

    def build(self):
        self.data = self.task_item.file_data[self.row]

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.installEventFilter(self)
        self.buttons_lo = QtWidgets.QHBoxLayout(self.buttons_widget)
        self.buttons_lo.setContentsMargins(0,0,0,0)
        self.buttons_lo.setSpacing(0)

        self.button_secondary = TaskFileActionsButton(self)
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

    def _on_action_menu_triggered(self, action):
        self.flow_page.show_action_dialog(action.oid)


class TaskFileList(BaseFileList):

    def __init__(self, task_item):
        super(BaseFileList, self).__init__()
        self.setObjectName('TaskFileList')
        self.task_item = task_item
        self.page_widget = task_item.page_widget
        self.flow_page = task_item.page_widget.page
        self.session = task_item.page_widget.session
        
        self.model = QTaskFileListModel(self.task_item)
        self.setModel(self.model)
        self.setItemDelegate(QFileListDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(35)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignVCenter)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

        self.action_manager = ObjectActionMenuManager(
            self.session, self.flow_page.show_action_dialog, 'Flow.map'
        )
        self.action_menu = QtWidgets.QMenu()

        self.setStyleSheet('#TaskFileList { border: none; background: transparent; gridline-color: #504f4f;}')

        self.customContextMenuRequested.connect(self._on_context_menu_requested)
        self.doubleClicked.connect(self._on_item_double_clicked)

    def update(self):
        for row in range(self.model.rowCount()):
            self.setIndexWidget(
                self.model.index(row, 0),
                TaskFileListItemWidget(self.task_item, self.flow_page, row, self.action_manager)
            )

    def selectionChanged(self, selected, deselected):
        super(BaseFileList, self).selectionChanged(selected, deselected)

    def mousePressEvent(self, event):
        super(BaseFileList, self).mousePressEvent(event)

        if event.button() == QtCore.Qt.RightButton:
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.emit(event.pos())
            self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        else:
            if event.button() == QtCore.Qt.LeftButton:
                if not self.indexAt(event.pos()).isValid():
                    self.clearSelection()

    def dragEnterEvent(self, event):
        super(BaseFileList, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(BaseFileList, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().text().startswith('file:///'):
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.toLocalFile()))

            return self.handle_dropped_files(links)

    def handle_dropped_files(self, paths):
        self.session.cmds.Flow.set_value(
            '/'+self.task_item.task_oid.split('/')[1]+'/import_files/paths', paths
        )
        self.session.cmds.Flow.set_value(
            '/'+self.task_item.task_oid.split('/')[1]+'/import_files/source_task', self.task_item.task_oid
        )
        
        self.flow_page.show_action_dialog('/'+self.task_item.task_oid.split('/')[1]+'/import_files')

    def _on_context_menu_requested(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        
        data = self.task_item.file_data[index.row()]
        has_actions = self.action_manager.update_oid_menu(
            data.oid(), self.action_menu, with_submenus=True
        )

        if has_actions:
            self.action_menu.exec_(self.viewport().mapToGlobal(pos))

    def _on_item_double_clicked(self, index):
        data = self.task_item.file_data[index.row()]
        self.flow_page.show_action_dialog(data.activate_oid)