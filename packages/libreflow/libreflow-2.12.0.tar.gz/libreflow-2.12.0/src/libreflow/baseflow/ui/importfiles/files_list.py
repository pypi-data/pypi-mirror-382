import re
from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets
from kabaret.app import resources

from libreflow.baseflow.runners import FILE_EXTENSION_ICONS
from ....resources.icons import gui

from .target_wizard import TargetWizardDialog


class LabelIcon(QtWidgets.QLabel):

    def __init__(self, icon=None):
        QtWidgets.QLabel.__init__(self, '')
        if icon:
            self.setIcon(icon)
    
    def setIcon(self, icon):
        icon = QtGui.QIcon(resources.get_icon(icon))
        pixmap = icon.pixmap(QtCore.QSize(16, 16))
        self.setPixmap(pixmap)
        self.setAlignment(QtCore.Qt.AlignVCenter)


class TargetInput(QtWidgets.QLineEdit):

    def __init__(self, widget):
        QtWidgets.QLineEdit.__init__(self)
        self.widget = widget
        self.page_widget = widget.page_widget
        self.target_original = ''
    
        self.editingFinished.connect(self._on_target_finish_edit)
        self.setDragEnabled(True)

    def checkTarget(self):
        self.blockSignals(True)
        if self.text() == ('' or self.target_original) and self.property('error') is False:
            self.set_source_display()
            self.blockSignals(False)
            return
            
        self.target_original = self.text()

        if re.search('\/tasks\/[A-Za-z_][A-Za-z0-9_]*$', self.text()) is None:
            self.setProperty('error', True)
            self.setStyleSheet('''
                QToolTip {
                    background-color: #ffaaaa;
                    color: black;
                    border-color: red;
                }
            ''')

            error = '!!!\nERROR: You need to specify a task entity.'
            if self.text()[-1] == '/':
                error = '!!!\nERROR: The last character must not be a slash.'

            self.setToolTip(error)
            self.style().polish(self)
            self.widget.refresh()
            self.blockSignals(False)
            return
        
        self.setProperty('error', False)
        self.setStyleSheet('')
        self.setToolTip('')
        self.style().polish(self)
        
        self.widget.item.file_target_oid.set(self.text())
        self.set_source_display()
        self.widget.refresh()
        self.blockSignals(False)

    def set_source_display(self):
        if self.text() == '':
            return

        split = self.text().split('/')
        indices = list(range(len(split) - 1, 2, -2))
        self.setText(' · '.join([split[i] for i in reversed(indices)]))

    def focusInEvent(self, event):
        if event.reason() != QtCore.Qt.PopupFocusReason:
            self.setText(self.target_original)
        super(TargetInput, self).focusInEvent(event)

    def dragEnterEvent(self, event):
        if self.page.session.cmds.Flow.can_handle_mime_formats(event.mimeData().formats()):
            return event.acceptProposedAction()
        return super(TargetInput, self).dragEnterEvent(event)

    def dropEvent(self, event):
        self.setText(event.mimeData().text())
        self.checkTarget()
         
    def _on_target_finish_edit(self):
        self.checkTarget()


class FileItem(QtWidgets.QWidget):

    ICON_BY_STATUS = {
        True: ('icons.libreflow', 'available'),
        False: ('icons.libreflow', 'warning'),
    }

    def __init__(self, files_list, item):
        super(FileItem, self).__init__()
        self.setObjectName('FileItem')
        self.list = files_list
        self.page_widget = files_list.page_widget
        
        self.item = item
        self.oid = item.oid()
       
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            '''
            #FileItem {
                background-color: palette(window);
                border: palette(dark);
                border-radius: 5px;
            }
            '''
        )
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

        self.build()
        self.refresh(True)

    def build(self):
        container = QtWidgets.QVBoxLayout()
        container.setContentsMargins(10,10,10,10)

        header_lo = QtWidgets.QHBoxLayout()
        self.file_icon = LabelIcon()
        self.file_name = QtWidgets.QLabel()
        self.arrow = QtWidgets.QLabel('➜')
        self.file_match_name = QtWidgets.QLineEdit()
        self.file_match_name.setMaximumWidth(150)
        self.file_revision = QtWidgets.QLabel()
        self.status_icon = LabelIcon()

        header_lo.addWidget(self.file_icon)
        header_lo.addWidget(self.file_name)
        header_lo.addWidget(self.arrow)
        header_lo.addWidget(self.file_match_name)
        header_lo.addStretch()
        header_lo.addWidget(self.file_revision)
        header_lo.addWidget(self.status_icon)

        settings_lo = QtWidgets.QHBoxLayout()
        target_label = QtWidgets.QLabel('Target')
        self.target_input = TargetInput(self)
        comment_label = QtWidgets.QLabel('Comment')
        self.comment_input = QtWidgets.QLineEdit()
        self.comment_input.editingFinished.connect(self._on_comment_finish_edit)

        settings_lo.addWidget(target_label)
        settings_lo.addWidget(self.target_input)
        settings_lo.addWidget(comment_label)
        settings_lo.addWidget(self.comment_input)

        container.addLayout(header_lo)
        container.addLayout(settings_lo)
        self.setLayout(container)

    def refresh(self, init=False):       
        if init:
            if self.item.file_extension.get():
                self.file_icon.setIcon(FILE_EXTENSION_ICONS.get(self.item.file_extension.get()[1:], ('icons.gui', 'text-file-1')))
            else:
                self.file_icon.setIcon(('icons.gui', 'folder-white-shape'))

            self.file_name.setText(self.item.file_name.get())
            self.file_match_name.setText(self.item.file_match_name.get())

            rx = '[A-Za-z_\s][A-Za-z0-9_\s]*'
            if self.item.file_extension.get():
                rx += self.item.file_extension.get()

            self.file_match_name.setValidator(
                QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(rx))
            )
            self.file_match_name.installEventFilter(self)

            self.target_input.setText(self.item.file_target_oid.get())
            self.target_input.set_source_display()
            self.target_input.target_original = self.item.file_target_oid.get()
        
        if self.file_match_name.property('error') or self.target_input.property('error'):
            self.item.file_status.set(False)
        else:
            self.item.file_status.set(True)
            self.page_widget.session.cmds.Flow.call(self.oid, 'check_revision', {}, {})
            self.page_widget.session.cmds.Flow.call(
                self.page_widget.oid, 'set_path_format', [
                    self.item,
                    re.search(f'(?<=tasks\/)[^\/]*', self.item.file_target_oid.get()).group(0),
                    self.item.file_match_name.get()
                ], {}
            )

        self.status_icon.setIcon(self.ICON_BY_STATUS[self.item.file_status.get()])
        self.page_widget.button_import.setEnabled(self.item.file_status.get())
        self.file_revision.setText(self.item.file_version.get())

    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            widget = QtWidgets.QApplication.focusWidget()
            if isinstance(widget, TargetInput) and widget.property('error') is False:
                widget.blockSignals(True)
                widget.focusNextPrevChild(True)
                widget.blockSignals(False)
        return super().event(event)

    def eventFilter(self, source, event):
        if source is self.file_match_name and event.type() == QtCore.QEvent.KeyPress:
            if (
                event.key() == QtCore.Qt.Key_Enter or
                event.key() == QtCore.Qt.Key_Return
            ):
                checked = self.validate_match_name()
                if not checked:
                    return False
            else:
                self.file_match_name.setToolTip('')
                self.file_match_name.setProperty('error', False)
                self.file_match_name.style().polish(self.file_match_name)
            
        if (
            source is self.file_match_name
            and event.type() == QtCore.QEvent.FocusOut
            and self.page_widget.button_import.isEnabled()
        ):
            checked = self.validate_match_name()
            if not checked:
                return False
        
        return super().eventFilter(source, event)

    def validate_match_name(self):
        if self.file_match_name.hasAcceptableInput() is False:
            self.file_match_name.setToolTip('ERROR: Invalid file name format')
            self.file_match_name.setProperty('error', True)
            self.file_match_name.style().polish(self.file_match_name)
            self.refresh()
            return False

        self.file_match_name.setToolTip('')
        self.file_match_name.setProperty('error', False)
        self.file_match_name.style().polish(self.file_match_name)
        
        self.item.file_match_name.set(self.file_match_name.text())
        self.refresh()
        return True

    def _on_comment_finish_edit(self):
        self.item.file_comment.set(self.comment_input.text())

    def _on_remove_file_action_clicked(self):
        self.page_widget.remove_file(self.item.name())
        self.deleteLater()
        self.list.refresh()

    def _on_context_menu(self, event):
        context_menu = QtWidgets.QMenu(self)
        remove_file = context_menu.addAction(QtGui.QIcon(resources.get_icon(('icons.gui', 'remove-symbol'))), 'Remove File')
        remove_file.triggered.connect(self._on_remove_file_action_clicked)

        context_menu.exec_(self.mapToGlobal(event))


class FilesList(QtWidgets.QScrollArea):

    def __init__(self, page_widget):
        super(FilesList, self).__init__()
        self.page_widget = page_widget
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)

        self.setStyleSheet(
            '''
            QScrollArea {
                border: palette(dark);
                border-radius: 5px;
            }
            #ScrollAreaContainer {
                background-color: palette(base);
                border: palette(dark);
                border-radius: 5px;
            }
            '''
        )

        self.build()

    def build(self):
        container = QtWidgets.QWidget()
        container.setObjectName('ScrollAreaContainer')

        self.layout = QtWidgets.QVBoxLayout(container)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10,10,10,10)
        self.setWidget(container)

    def refresh(self, force_update=False):
        if force_update:
            # Fetch map
            items = self.page_widget.get_files()
        
            for item in items:
                # Check if already exist
                exist = False
                for i in reversed(range(self.layout.count())):
                    if self.layout.itemAt(i).widget().oid == item.oid():
                        exist = True
                
                if not exist:
                    # Start target wizard if there are some unknown values
                    if not item.file_status.get():
                        dialog = TargetWizardDialog(self, item)
                        if dialog.exec() == 0:
                            self.page_widget.remove_file(item.name())
                            continue

                    # Create item
                    item = FileItem(self, item)
                    self.layout.addWidget(item)

        # Show list
        if self.page_widget.refresh_list_count() > 0:
            self.page_widget.button_import.setEnabled(True)
        else:
            self.page_widget.button_import.setEnabled(False)
            self.page_widget.list.hide()
            self.page_widget.dragdrop.show()
    
    def clear(self):
        for i in reversed(range(self.layout.count())):
            if self.layout.itemAt(i).widget():
                self.layout.itemAt(i).widget().deleteLater()

    def get_count(self):
        return len(self.page_widget.get_files())

    def dragEnterEvent(self, event):
        event.accept() if event.mimeData().hasUrls else event.ignore()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            paths.append(str(url.toLocalFile()))
        
        self.page_widget.add_files(paths)
