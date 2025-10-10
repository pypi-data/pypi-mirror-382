import os
import re
from kabaret.app.ui.gui.widgets.flow.flow_view import QtCore, QtGui, QtWidgets, CustomPageWidget
from kabaret.app import resources

from libreflow.baseflow.runners import FILE_EXTENSION_ICONS


STYLESHEET = '''
    QLineEdit {
        padding: 0px;
    }
'''

class EntityItemDelegate(QtWidgets.QStyledItemDelegate):

    '''
    ItemDelegate for handle differently the QRegExpValidator.
    With visual feedback and if item already exists.
    '''

    def __init__(self, tree):
        QtWidgets.QStyledItemDelegate.__init__(self)
        self.tree = tree

    def createEditor(self, parent, option, index):
        self.editor = QtWidgets.QLineEdit(parent)
        self.item = self.tree.itemFromIndex(index)
        self.editor.setValidator(self.item.validator)
        self.editor.installEventFilter(self)
        return self.editor

    def eventFilter(self, source, event):
        if source is self.editor:
            if event.type() == QtCore.QEvent.KeyPress:
                if (
                    event.key() == QtCore.Qt.Key_Enter or
                    event.key() == QtCore.Qt.Key_Return
                ):
                    checked = self.validate()
                    if not checked:
                        return False
                else:
                    self.editor.setToolTip('')
                    self.editor.setProperty('error', False)
                    self.editor.style().polish(self.editor)
            
            if event.type() == QtCore.QEvent.FocusOut:
                checked = self.validate()
                if not checked:
                    return False
        
        return super().eventFilter(source, event)

    def validate(self):
        exist = self.tree.get_item(
            self.editor.text(),
            'name' if self.tree.header_text != 'Files' else 'display_name'
        )
        if self.editor.hasAcceptableInput() is False or exist:
            if exist is self.item:
                pass
            else:
                self.editor.setToolTip('ERROR: Invalid item name format or already exist')
                self.editor.setProperty('error', True)
                self.editor.style().polish(self.editor)
                return False

        self.editor.setToolTip('')
        self.editor.setProperty('error', False)
        self.editor.style().polish(self.editor)
        return True


class EntityItem(QtWidgets.QTreeWidgetItem):

    DEFAULT_ICONS = {
        "Films": ("icons.flow", "film"),
        "Sequences": ("icons.flow", "sequence"),
        "Shots": ("icons.flow", "shot"),
        "Tasks": ("icons.gui", "cog-wheel-silhouette"),
        "Asset Libs": ("icons.gui", "cog-wheel-silhouette"),
        "Asset Types": ("icons.flow", "asset_family"),
        "Asset Families": ("icons.flow", "asset_family"),
        "Assets": ("icons.flow", "asset")
    }

    def __init__(self, tree, data=None, display_name=None, editable=False):
        super(EntityItem, self).__init__(tree)
        self.tree = tree
        self.page_widget = tree.page_widget
        
        self.editable = editable

        self.display_name = display_name
        self.name = data['name'] if data else re.sub('[\s.-]', '_', display_name)
        self.oid = data['oid'] if data else None
        self.icon = data['icon'] if data else None
        
        if editable:
            self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)
            self.tree.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
            
            rx = '[A-Za-z_\s][A-Za-z0-9_\s]*'
            if self.tree.header_text == 'Files' and self.tree.dialog.item.file_extension.get():
                rx += self.tree.dialog.item.file_extension.get()

            self.validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(rx))

            if self.tree.header_text == 'Asset Families':
                self.display_name += f' asset family'
            else:
                self.display_name += f' {self.tree.header_text[:-1].lower()}'
            self.icon = ('icons.gui', 'plus-sign-in-a-black-circle')

        self.refresh()
    
    def refresh(self):          
        if self.tree.header_text == 'Files' and self.display_name != "Create file":
            file_name, ext = os.path.splitext(self.display_name)
            if ext:
                self.icon = FILE_EXTENSION_ICONS.get(ext[1:], ('icons.gui', 'text-file-1'))
            else:
                self.icon = ('icons.gui', 'folder-white-shape')
        
        elif (
            self.editable and 'Create' not in self.display_name
            and self.icon == ('icons.gui', 'plus-sign-in-a-black-circle')
        ):
            self.icon = self.DEFAULT_ICONS.get(self.tree.header_text)
        
        self.setIcon(0, self.get_icon(self.icon)) if self.oid or self.editable else None
        self.setText(0, self.display_name)
    
    @staticmethod
    def get_icon(icon_ref):
        return QtGui.QIcon(resources.get_icon(icon_ref))


class EntityList(QtWidgets.QTreeWidget):

    def __init__(self, dialog, header_text, map_oid=None, default_value=None):
        super(EntityList, self).__init__()
        self.dialog = dialog
        self.page_widget = dialog.page_widget
        self.header_text = header_text
        self.map_oid = map_oid
        self.default_value = default_value

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setRootIsDecorated(False)

        self.setHeaderLabel(self.header_text)
        self.header().setDefaultAlignment(QtCore.Qt.AlignCenter)
        self.header().setStretchLastSection(True)

        self.setItemDelegate(EntityItemDelegate(self))

        self.setStyleSheet('''
            QTreeView::item:selected {
                background-color: palette(highlight);
                color: white;
            }'''
        )

        self.refresh()
        
        self.currentItemChanged.connect(self.on_item_select)
        self.itemChanged.connect(self.on_item_changed)
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)

    def refresh(self):
        self.blockSignals(True)
        self.clear()

        # For main list
        if self.header_text == "Type":
            EntityItem(self, display_name='Films')
            EntityItem(self, display_name='Assets')

        # Show map items if we have oid
        if self.map_oid is not None:
            try:
                items = self.dialog.get_mapped_items(self.map_oid, self.header_text)

                # Check if asset families are used
                list_index = self.dialog.content_layout.indexOf(self)
                if len(items) == 0 and list_index == 2:
                    if self.header_text in ('Asset Families', 'Assets'):
                        map_oid = self.map_oid.replace('asset_families', 'assets') if self.header_text == 'Asset Families' \
                            else self.map_oid.replace('assets', 'asset_families')
                        
                        items = self.dialog.get_mapped_items(map_oid, self.header_text)
                        if items:
                            self.dialog.build_flow('Assets', asset_rebuild=self.header_text)
                            return

                for item_data in items:
                    # For files, show only ones with same extension
                    if self.header_text == 'Files':
                        name, ext = os.path.splitext(item_data['display_name'])
                        ext = None if ext == '' else ext
                        if ext != self.dialog.item.file_extension.get():
                            continue
                    
                    item = EntityItem(self, data=item_data, display_name=item_data['display_name'])
                    
                    # Set current item if there is the default value
                    if self.header_text == 'Films' or self.page_widget.is_source_task_mode():
                        if self.default_value and self.default_value == item_data['name']:
                            self.setCurrentItem(item)
                    elif self.default_value and self.default_value in item_data['name']:
                        self.setCurrentItem(item)
            except KeyError:
                None

            # Add create new entity option at the end of the list
            if self.header_text != "Type":
                EntityItem(self, display_name='Create', editable=True)
        
        # Set current item if there is only one
        if self.topLevelItemCount()-1 == 1 and any(x in self.header_text for x in ['Type', 'Files']) is False:
            self.setCurrentItem(self.topLevelItem(0))
        else:
            # For specific cases
            if self.header_text == 'Files':
                if self.dialog.item.file_match_name.get():
                    self.setCurrentItem(self.get_item(self.dialog.item.file_match_name.get(), 'display_name'))
                
                self.dialog.button_add.setEnabled(
                    True if self.currentItem() else False
                )

            if self.header_text == 'Tasks':
                if type(self.dialog.item.task_name.get()) is str:
                    self.setCurrentItem(self.get_item(self.dialog.item.task_name.get(), 'name'))
                elif type(self.dialog.item.task_name.get()) is list:
                    for task_name in self.dialog.item.task_name.get():
                        matching_task = self.get_item(task_name, 'name')
                        matching_task.setForeground(0, QtGui.QBrush(QtGui.Qt.green)) if matching_task else None

        self.blockSignals(False)

    def get_item(self, value, attr):
        match_index = [
            i for i in range(self.topLevelItemCount())
            if getattr(self.topLevelItem(i), attr).lower() == value.lower()
        ]

        return self.topLevelItem(match_index[0]) if len(match_index) > 0 else None

    def on_item_select(self, current_item, previous_item):
        if current_item:
            if current_item.editable and 'Create' in current_item.display_name:
                focus_widget = QtWidgets.QApplication.focusWidget()
                if isinstance(focus_widget, QtWidgets.QLineEdit):
                    if self.header_text == "Files" and self.dialog.item.file_extension.get():
                        focus_widget.setText(self.dialog.item.file_extension.get())
                        focus_widget.setSelection(0, 0)
                        return
                    focus_widget.clear()
                    return

        if self.header_text == 'Files':
            self.dialog.button_add.setEnabled(True)
        
        if self.header_text == "Type":
            return self.dialog.build_flow(current_item.display_name)

        if current_item:
            return self.dialog.refresh(self)

    def on_item_changed(self, item, column):
        if item.flags() & QtCore.Qt.ItemIsEditable:
            self.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
            item.setForeground(0, QtGui.QBrush(QtGui.Qt.green))
            item.display_name = item.text(0)
            
            item.name = re.sub('[\s.-]', '_', item.text(0))
            if self.header_text == 'Tasks':
                if self.page_widget.lowercase_for_task() is True:
                    item.name = item.name.lower()
                
                dft_task = self.page_widget.check_default_task(item.name)
                if dft_task:
                    item.display_name = dft_task.display_name.get()
                    item.icon = dft_task.get_icon()

            item.oid = f"{self.map_oid}/{item.name}"
            item.refresh()
            if self.header_text != 'Files':
                self.dialog.refresh(self)
            else:
                self.dialog.button_add.setEnabled(True)


class FileHeader(QtWidgets.QWidget):

    def __init__(self, dialog, item):
        super(FileHeader, self).__init__()
        self.dialog = dialog
        self.page_widget = dialog.page_widget
        self.item = item

        self.setAutoFillBackground(True)

        self.build()
        self.refresh()
    
    def build(self):
        hlo = QtWidgets.QHBoxLayout(self)

        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, pal.color(QtGui.QPalette.Mid))
        self.setPalette(pal)

        font = QtGui.QFont()
        font.setBold(True)

        self.label_icon = QtWidgets.QLabel()
        self.label_icon.setAlignment(QtCore.Qt.AlignCenter)

        self.label_name = QtWidgets.QLabel('Choose target for\n')
        self.label_name.setFont(font)
        self.label_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        hlo.addWidget(self.label_icon)
        hlo.addWidget(self.label_name)
        hlo.addStretch()

    def refresh(self):
        if self.item.file_extension.get():
            folder, pixmap = FILE_EXTENSION_ICONS.get(self.item.file_extension.get()[1:])
            pm = resources.get_pixmap(folder, pixmap)
        else:
            pm = resources.get_pixmap('icons.gui', 'folder-white-shape')
        
        self.label_icon.setPixmap(pm.scaled(20, 20, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.label_name.setText(self.label_name.text()+self.item.file_name.get())


class TargetWizardDialog(QtWidgets.QDialog):

    def __init__(self, files_list, item):
        super(TargetWizardDialog, self).__init__(files_list.page_widget)
        self.list = files_list
        self.page_widget = files_list.page_widget
        self.item = item

        self.setStyleSheet(STYLESHEET)

        self.film_flow = ['Films', 'Sequences', 'Shots', 'Tasks', 'Files']
        if self.page_widget.get_project_type() == 'tvshow':
            self.asset_flow = ['Asset Libs', 'Asset Types', 'Assets', 'Tasks', 'Files']
        else:
            self.asset_flow = ['Asset Types', 'Asset Families', 'Assets', 'Tasks', 'Files']

        self.split_oid = self.page_widget.session.cmds.Flow.split_oid(
            self.item.file_target_oid.get(), True, self.page_widget.get_project_oid()
        )

        self.build()
    
    def build(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(20,20,20,20)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Window))
        self.setPalette(palette)

        # File Header
        self.header = FileHeader(self, self.item)
        self.layout.addWidget(self.header)

        # Buttons
        self.button_layout = QtWidgets.QHBoxLayout()

        self.button_add = QtWidgets.QPushButton('Add')
        self.button_cancel = QtWidgets.QPushButton('Cancel')

        self.button_add.clicked.connect(self._on_add_button_clicked)
        self.button_cancel.clicked.connect(self._on_cancel_button_clicked)

        self.button_add.setAutoDefault(False)
        self.button_cancel.setAutoDefault(False)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.button_add)
        self.button_layout.addWidget(self.button_cancel)

        # Entity View
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(2)

        self.main_list = EntityList(self, 'Type')
        self.content_layout.addWidget(self.main_list)

        index = 0
        if self.split_oid:
            index = 0 if ('films' or 'Home') in self.split_oid[0][1] else 1
        else:
            if any(value is not None for value in [
                self.item.sequence_name.get(),
                self.item.shot_name.get()
            ]):
                index = 0
            elif any(value is not None for value in [
                self.item.asset_type_name.get(),
                self.item.asset_family_name.get(),
                self.item.asset_name.get()
            ]):
                index = 1
        self.main_list.setCurrentItem(self.main_list.topLevelItem(index))

        self.layout.addLayout(self.content_layout)
        self.layout.addLayout(self.button_layout)

    def build_flow(self, entity_type, asset_rebuild=None):
        # Rebuild after 2nd asset flow level
        if asset_rebuild:
            flow = self.asset_flow[1:]
            if asset_rebuild == 'Asset Families':
                flow.remove(asset_rebuild)
            
            for i in reversed(range(self.content_layout.count())[2:]):
                self.content_layout.itemAt(i).widget().deleteLater()
        else:
            # Clear current flow
            if self.content_layout.count() > 1:
                self.clear()

            # Use the correct one (for film or asset)
            flow = self.film_flow if entity_type == 'Films' else self.asset_flow
        
        latest_list = None
        for i, entity_display_name in enumerate(flow):
            entity_name = entity_display_name.lower().replace(" ", "_")

            map_oid = None
            default_value = None

            # Find map oid for entity
            for label, goto_oid in self.split_oid:
                map_oid = None
                default_value = None

                if label == 'Home':
                    break

                map_type = label.split(':')[0]
                if map_type == entity_name:
                    map_oid = '/'.join(goto_oid.split('/')[:-1])
                    default_value = label.split(':')[1]
                    break

            # Get matching value
            if not default_value and entity_display_name != 'Files':
                if entity_name == 'asset_families':
                    object_name = 'asset_family'
                    attr = f"{object_name}_name"
                else:
                    attr = f"{entity_name[:-1]}_name"
                
                if getattr(self.item, attr).get() is not None:
                    default_value = getattr(self.item, attr).get()

            # Re-set map oid if asset rebuild
            if asset_rebuild and i == 0:
                previous_list = self.content_layout.itemAt(1).widget()
                map_oid = f"{previous_list.currentItem().oid}/{entity_name}"

            # If no base entity
            elif map_oid is None and i == 0:
                map_oid = f'{self.page_widget.get_project_oid()}/{entity_name}'
            
            entity_list = EntityList(self, entity_display_name, map_oid, default_value)
            self.content_layout.addWidget(entity_list)

            if map_oid:
                latest_list = entity_list
        
        if latest_list and latest_list.currentItem():
            self.refresh(latest_list)

    def refresh(self, source_list):
        source_index = self.content_layout.indexOf(source_list)

        for i in range(self.content_layout.count())[source_index+1:]:
            entity_list = self.content_layout.itemAt(i).widget()
            previous_list = self.content_layout.itemAt(i-1).widget()
            
            if previous_list.currentItem():
                entity_name = re.sub('[\s.-]', '_', entity_list.header_text.lower())
                entity_list.map_oid = f"{previous_list.currentItem().oid}/{entity_name}"
                entity_list.refresh()
            else:
                entity_list.clear()
    
    def clear(self):
        for i in reversed(range(self.content_layout.count())[1:]):
            self.content_layout.itemAt(i).widget().deleteLater()

    def define_new_entities(self):
        new_entities = dict()

        for i in range(self.content_layout.count())[:-1]:
            entity_list = self.content_layout.itemAt(i).widget()

            if entity_list.currentItem().editable:
                new_entities[re.sub('[\s.-]', '_', entity_list.header_text.lower())] = dict(
                    display_name=entity_list.currentItem().display_name,
                    name=entity_list.currentItem().name
                )
        
        return new_entities if new_entities.items() else None

    def sizeHint(self):
        return QtCore.QSize(1100, 600)

    def get_mapped_items(self, map_oid, entity_type):
        items = []

        item_oids = self.page_widget.session.cmds.Flow.get_mapped_oids(map_oid)
        for oid in item_oids:
            # Get Icon
            o = self.page_widget.session.get_actor('Flow').get_object(oid)
            if o.ICON == 'object' or o.ICON is None or entity_type in ['Tasks, Files']:
                if getattr(o, 'get_icon'):
                    icon = o.get_icon()
            else:
                icon = o.ICON
            
            items.append(dict(
                oid=oid,
                display_name=o.name() if entity_type != 'Files' else o.display_name.get(),
                name=o.name(),
                icon=icon
            ))
        
        return items

    def _on_add_button_clicked(self):
        task_list = self.content_layout.itemAt(self.content_layout.count()-2).widget()
        files_list = self.content_layout.itemAt(self.content_layout.count()-1).widget()

        self.item.file_match_name.set(files_list.currentItem().display_name)
        self.item.file_target_oid.set(task_list.currentItem().oid)
        self.item.entities_to_create.set(self.define_new_entities())

        self.accept()

    def _on_cancel_button_clicked(self):
        self.close()
