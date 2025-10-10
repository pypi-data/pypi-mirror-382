import time

from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources

from .files_list import FilesList

STYLESHEET = '''
    QLineEdit#PresetComboBox {
        border: none;
        padding: 0px;
    }
'''


class PopUpDialog(QtWidgets.QFrame):

    def __init__(self, page_widget):
        QtWidgets.QFrame.__init__(self)
        self.setObjectName('PopUpDialog')
        self.page_widget = page_widget

        self.setStyleSheet(
            '''
            #PopUpDialog {
                background-color: rgba(0,0,0,0.5);
                border-radius: 5px;
            }
            #PopUpMessage {
                background-color: palette(window);
                border-radius: 5px;
            }
            '''
        )
        
        self.build()

    def build(self):
        container_lo = QtWidgets.QVBoxLayout(self)
       
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(QtGui.QFont.Bold)

        message_widget = QtWidgets.QFrame()
        message_widget.setObjectName('PopUpMessage')
        message_widget.setFixedWidth(200)

        message_lo = QtWidgets.QVBoxLayout(message_widget)
        message_lo.setContentsMargins(20,20,20,20)
        message_lo.setSpacing(10)

        self.main_label = QtWidgets.QLabel('Resolving files')
        self.main_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_label.setFont(font)
        
        self.description_label = QtWidgets.QLabel('Please wait...')
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)

        message_lo.addWidget(self.main_label)
        message_lo.addWidget(self.description_label)

        container_lo.addWidget(message_widget, alignment=QtCore.Qt.AlignCenter)

    def pop(self, main_text, description_text):
        self.page_widget.popup.show()

        self.main_label.setText(main_text)
        self.description_label.setText(description_text)


class DragDropWidget(QtWidgets.QFrame):

    def __init__(self, custom_widget):
        super(DragDropWidget, self).__init__(custom_widget)
        self.custom_widget = custom_widget
        
        self.setAcceptDrops(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setStyleSheet(
            '''
            background-color: palette(base);
            border: palette(dark);
            border-radius: 5px;
            '''
        )
        
        self.build()

    def build(self):
        lo = QtWidgets.QVBoxLayout(self)

        asset = QtWidgets.QWidget()
        asset_lo = QtWidgets.QVBoxLayout(asset)
        
        icon = QtGui.QIcon(resources.get_icon(('icons.gui', 'file')))
        pixmap = icon.pixmap(QtCore.QSize(128, 128))
        icon_lbl = QtWidgets.QLabel('')
        icon_lbl.setPixmap(pixmap)
        
        label = QtWidgets.QLabel('Drop your files here')

        asset_lo.addWidget(icon_lbl, alignment=QtCore.Qt.AlignCenter)
        asset_lo.addWidget(label, alignment=QtCore.Qt.AlignCenter)
        
        lo.addWidget(asset, alignment=QtCore.Qt.AlignCenter)

    def dragEnterEvent(self, event):
        event.accept() if event.mimeData().hasUrls else event.ignore()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            paths.append(str(url.toLocalFile()))
        
        self.custom_widget.add_files(paths)


class ImportFilesWidget(CustomPageWidget):

    def build(self):
        self.setStyleSheet(STYLESHEET)
        self.clear_map()

        glo = QtWidgets.QGridLayout(self)

        self.dragdrop = DragDropWidget(self)

        self.popup = PopUpDialog(self)
        self.popup.hide()
        
        self.list = FilesList(self)
        self.list.hide()

        self.list_count = QtWidgets.QLabel(str(self.list.get_count())+' files')
        
        self.button_settings = QtWidgets.QPushButton('Settings')
        self.button_settings.clicked.connect(self._on_button_settings_clicked)
        self.button_settings.setAutoDefault(False)

        self.button_import = QtWidgets.QPushButton('Import')
        self.button_import.clicked.connect(self._on_button_import_clicked)
        self.button_import.setAutoDefault(False)
        self.button_import.setEnabled(False)
     
        glo.addWidget(self.list_count, 0, 0)
        glo.addWidget(self.dragdrop, 1, 0, 1, 3)
        glo.addWidget(self.list, 1, 0, 1, 3)
        glo.addWidget(self.popup, 1, 0, 1, 3)
        glo.addWidget(self.button_settings, 2, 0)
        glo.addWidget(self.button_import, 2, 2)
        glo.setColumnStretch(1, 1)

        QtCore.QTimer.singleShot(1, self._add_base_files)

    def _add_base_files(self):
        if self.session.cmds.Flow.get_value(self.oid+'/paths') != []:
            self.add_files(self.session.cmds.Flow.get_value(self.oid+'/paths'))
            self.session.cmds.Flow.set_value(self.oid+'/paths', [])
            self.session.cmds.Flow.set_value(self.oid+'/source_task', '')

    def add_files(self, paths):
        self.button_import.setEnabled(False)
        self.list.show()
        self.popup.pop('Resolving files', 'Please wait...')
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

        self.session.cmds.Flow.call(self.oid, 'resolve_paths', [paths], {})
        self.list.refresh(True)

        self.popup.hide()

    def remove_file(self, name):
        return self.session.cmds.Flow.call(
            f"{self.oid}/settings/files_map", 'remove', [name], {}
        )

    def clear_map(self):
        return self.session.cmds.Flow.call(
            f"{self.oid}/settings/files_map", 'clear', {}, {}
        )

    def get_files(self):
        return self.session.cmds.Flow.call(
            f"{self.oid}/settings/files_map", 'mapped_items', {}, {}
        )

    def refresh_list_count(self):
        count = self.list.get_count()
        self.list_count.setText(str(count) + (' file' if count == 1 else ' files'))
        return count

    def get_project_oid(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_project_oid', {}, {}
        )

    def get_entity_object(self, oid):
        return self.session.cmds.Flow.call(
            self.oid, 'get_entity_object', [oid], {}
        )

    def check_default_task(self, name):
        return self.session.cmds.Flow.call(
            self.oid, 'check_default_task', [name], {}
        )

    def get_project_type(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_project_type', [], {}
        )

    def lowercase_for_task(self):
        return self.session.cmds.Flow.get_value(self.oid+'/settings/lowercase_for_task')

    def is_source_task_mode(self):
        return True if self.session.cmds.Flow.get_value(self.oid+'/paths') != [] else False

    def _on_button_settings_clicked(self):
        self.page.goto(self.oid + '/settings')

    def _on_button_import_clicked(self):  
        self.button_import.setEnabled(False)
        self.popup.pop('Importing to pipe', 'Please wait...')
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        
        self.session.cmds.Flow.call(
            self.oid, 'import_files', [self.get_files()], {}
        )

        self.list.clear()
        self.list.refresh(True)

        self.popup.hide()