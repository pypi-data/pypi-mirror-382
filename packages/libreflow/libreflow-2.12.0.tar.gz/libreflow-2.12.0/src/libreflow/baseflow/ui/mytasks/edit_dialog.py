import os
import pprint
from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
    QtGui,
)
from kabaret.app import resources
from kabaret.app.ui.gui.icons import flow as _

from libreflow.baseflow.runners import FILE_EXTENSION_ICONS
from ....resources.icons import gui as _

from .components import LabelIcon


class FileUploadItem(QtWidgets.QWidget):
    """A single item in listWidget."""
    removed = QtCore.Signal(QtWidgets.QListWidgetItem)

    def __init__(self, combobox, text, path, listwidgetItem, primary_file):
        super().__init__()
        self.combobox = combobox
        self.text = text
        self.path = path
        self.listwidgetItem = listwidgetItem
        self.primary_file = primary_file
        self.checked = True

        self.build()

    def build(self):
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(5,0,0,0)

        name, ext = os.path.splitext(self.text)
        if ext:
            file_icon = FILE_EXTENSION_ICONS.get(
                ext[1:], ('icons.gui', 'text-file-1')
            )
        else:
            file_icon = ('icons.gui', 'folder-white-shape')

        label_icon = QtWidgets.QLabel('')
        icon = QtGui.QIcon(resources.get_icon(file_icon))
        pixmap = icon.pixmap(QtCore.QSize(13,13))
        label_icon.setPixmap(pixmap)

        file_name = QtWidgets.QLabel(self.text)

        self.horizontalLayout.addWidget(label_icon)
        self.horizontalLayout.addWidget(file_name)
        self.horizontalLayout.addStretch()

        if self.primary_file:
            self.checked = False
            self.checkbox = QtWidgets.QToolButton(self)
            self.checkbox.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'check-box-empty'))))
            self.checkbox.setFixedSize(20,20)
            self.checkbox.setIconSize(QtCore.QSize(10,10))
            self.checkbox.clicked.connect(self._on_checkbox_clicked)
            self.installEventFilter(self)
            self.horizontalLayout.addWidget(self.checkbox)
        else:
            self.delete = QtWidgets.QToolButton(self)
            self.delete.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'remove-symbol'))))
            self.delete.setFixedSize(20,20)
            self.delete.setIconSize(QtCore.QSize(10,10))
            self.delete.setToolTip("Delete")
            self.delete.clicked.connect(lambda: self.removed.emit(self.listwidgetItem))
            self.horizontalLayout.addWidget(self.delete)
    
    def setChecked(self, state):
        if state:
            self.checked = True
            self.checkbox.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'check'))))
        else:
            self.checked = False
            self.checkbox.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'check-box-empty'))))
            
        self.combobox.setTopText()
        
    def _on_checkbox_clicked(self):
        self.setChecked(False) if self.checked else self.setChecked(True)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                self._on_checkbox_clicked()
                return True
        
        return False


class FilesUploadComboBox(QtWidgets.QComboBox):

    def __init__(self, *args):
        super(FilesUploadComboBox, self).__init__(*args)
        self.listw = QtWidgets.QListWidget(self)
        self.setModel(self.listw.model())
        self.setView(self.listw)
        self.activated.connect(self.setTopText)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        qss = '''QListView {
                    border: 0px;
                }
                QListView::item:selected {
                    background: transparent;
                }
                QListView::item:hover {
                    background-color: #273541;
                }'''
        self.setStyleSheet(qss)
        self.view().window().setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.view().window().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setAcceptDrops(True)
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        self.view().viewport().installEventFilter(self)
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        self.addPrimaryFiles()

    def addItem(self, text, path, primary_file=None):
        item = QtWidgets.QListWidgetItem(self.listw)
        itemWidget = FileUploadItem(self, text, path, item, primary_file)
        itemWidget.removed.connect(self.removeItem)
        item.setSizeHint(itemWidget.sizeHint())
        self.listw.addItem(item)
        self.listw.setItemWidget(item, itemWidget)
        self.setTopText()
    
    def addFiles(self, paths):
        for path in paths:
            exist = False
            for i in range(self.listw.count()):
                item = self.listw.item(i)
                widget = self.listw.itemWidget(item)
                if widget.path == path:
                    exist = True
                    break
            if not exist:
                filename = os.path.split(path)[1]
                self.addItem(filename, path)

    def addPrimaryFiles(self):
        for data in self.parent().task_item.file_data:
            check = self.parent().page_widget.is_uploadable(data.label)
            if check:
                rev = self.parent().page_widget.session.cmds.Flow.call(
                    data.oid(), 'get_head_revision', ['Available'], {}
                )
                if rev:
                    self.addItem(data.label, rev.get_path(), True)

    def removeItem(self, item):
        view = self.view()
        index = view.indexFromItem(item)
        view.takeItem(index.row())
        self.setTopText()

    def clear(self):
        for i in reversed(range(self.listw.count())):
            item = self.listw.item(i)
            widget = self.listw.itemWidget(item)
            if widget.primary_file:
                widget.setChecked(False)
            else:
                self.removeItem(item)
        self.setTopText()

    def setTopText(self):
        list_text = self.fetchFilesNames()
        text = ", ".join(list_text)
        if not text:
            count = 0
            for i in range(self.listw.count()):
                if self.listw.itemWidget(self.listw.item(i)).primary_file:
                    count = count + 1
            if count > 1:
                return self.setEditText(str(count) + ' Primary files available')
        
        metrics = QtGui.QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, QtCore.Qt.ElideRight, self.lineEdit().width())
        if '…' in elidedText:
            elidedText = str(len(list_text)) + ' Files'
        self.setEditText(elidedText)

    def fetchFilesNames(self):
        return [
            self.listw.itemWidget(self.listw.item(i)).text
            for i in range(self.listw.count())
            if self.listw.itemWidget(self.listw.item(i)).checked
        ]

    def fetchItems(self):
        return [
            self.listw.itemWidget(self.listw.item(i))
            for i in range(self.listw.count())
            if self.listw.itemWidget(self.listw.item(i)).checked
        ]

    def count(self):
        return self.view().count()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.addFiles([url.toLocalFile() for url in event.mimeData().urls()])

    # Methods for make combobox less buggy
    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    if self.closeOnLineEditClick:
                        self.hidePopup()
                    else:
                        self.showPopup()
                    return True

        if object == self.view().viewport():
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        # Make sure scrollbar is correctly reset
        self.listw.verticalScrollBar().setValue(0)
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False


class EditStatusDialog(QtWidgets.QDialog):

    def __init__(self, task_item):
        super(EditStatusDialog, self).__init__(task_item)
        self.task_item = task_item
        self.page_widget = task_item.page_widget
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMaximumSize(600, 300)

        self.build()
    
    def build(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20,20,20,20)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Window))
        self.setPalette(palette)

        self.content_layout = QtWidgets.QGridLayout()
        self.content_layout.setAlignment(QtCore.Qt.AlignTop)
      
        self.content_layout.addWidget(LabelIcon(('icons.flow', 'input')), 0, 0, QtCore.Qt.AlignVCenter)
        self.content_layout.addWidget(QtWidgets.QLabel('Target Status'), 0, 1, QtCore.Qt.AlignVCenter)
        self.target_status = QtWidgets.QComboBox()
        self.target_status.addItems(sorted(self.page_widget.get_task_statutes(False)))
        self.target_status.setCurrentText('Work In Progress')
        self.content_layout.addWidget(self.target_status, 0, 2, 1, 3, QtCore.Qt.AlignVCenter)

        self.content_layout.addWidget(LabelIcon(('icons.flow', 'input')), 1, 0, QtCore.Qt.AlignVCenter)
        self.content_layout.addWidget(QtWidgets.QLabel('Comment'), 1, 1, QtCore.Qt.AlignVCenter)
        self.comment = QtWidgets.QTextEdit('')
        self.content_layout.addWidget(self.comment, 1, 2, 1, 3, QtCore.Qt.AlignVCenter)

        self.content_layout.addWidget(LabelIcon(('icons.flow', 'input')), 2, 0, QtCore.Qt.AlignVCenter)
        self.content_layout.addWidget(QtWidgets.QLabel('Files'), 2, 1, QtCore.Qt.AlignVCenter)
        self.files = FilesUploadComboBox(self)
        self.content_layout.addWidget(self.files, 2, 2, QtCore.Qt.AlignVCenter)

        self.files_buttons = QtWidgets.QWidget()
        self.files_buttons_lo = QtWidgets.QHBoxLayout()
        self.files_buttons_lo.setContentsMargins(0,0,0,0)
        self.files_buttons_lo.setSpacing(0)
        self.files_buttons.setLayout(self.files_buttons_lo)

        self.button_add = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.gui', 'add-file'))), '')
        self.button_add.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_add.clicked.connect(self._on_add_files_button_clicked)
        self.files_buttons_lo.addWidget(self.button_add)
        self.button_clear = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.libreflow', 'delete'))), '')
        self.button_clear.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_clear.clicked.connect(self._on_clear_button_clicked)
        self.files_buttons_lo.addWidget(self.button_clear)

        self.content_layout.addWidget(self.files_buttons, 2, 3, QtCore.Qt.AlignVCenter)
        self.content_layout.setColumnStretch(2, 1)

        # Buttons
        self.button_layout = QtWidgets.QHBoxLayout()

        self.button_post = QtWidgets.QPushButton('Post')
        self.button_cancel = QtWidgets.QPushButton('Cancel')

        self.button_post.clicked.connect(self._on_post_button_clicked)
        self.button_cancel.clicked.connect(self._on_cancel_button_clicked)

        self.button_post.setAutoDefault(False)
        self.button_cancel.setAutoDefault(False)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.button_post)
        self.button_layout.addWidget(self.button_cancel)

        self.layout.addLayout(self.content_layout)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def sizeHint(self):
        return QtCore.QSize(530, 275)

    def _on_add_files_button_clicked(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)

        if dialog.exec_():
            paths = dialog.selectedFiles()
            self.files.addFiles(paths)

    def _on_clear_button_clicked(self):
        self.files.clear()

    def _on_post_button_clicked(self):
        items = self.files.fetchItems()
        if len(items) == 1:
            if items[0].primary_file:
                self.page_widget.upload_preview(
                    self.task_item.data.entity_id.get(),
                    self.task_item.data.task_type.get(),
                    self.target_status.currentText(),
                    items[0].path,
                    self.comment.toPlainText()
                )
                return self.page_widget.content.list.refresh(True)
        
        paths = [item.path for item in items]
        self.page_widget.set_task_status(
            self.task_item.data.task_id.get(),
            self.target_status.currentText(),
            self.comment.toPlainText(),
            paths
        )
        self.page_widget.content.list.refresh(True)

    def _on_cancel_button_clicked(self):
        self.close()
