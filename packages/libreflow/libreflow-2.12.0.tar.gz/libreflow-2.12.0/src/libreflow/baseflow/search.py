import os

from kabaret import flow
from kabaret.app import resources

from kabaret.app.ui.gui.widgets.flow.flow_view import (
    QtWidgets, 
    QtCore, 
    QtGui, 
    CustomPageWidget,
    )
from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager

from libreflow.baseflow.runners import FILE_EXTENSION_ICONS


class SearchHeader(QtWidgets.QWidget):
    def __init__(self, content_widget):
        super(SearchHeader,self).__init__(content_widget)
        self.content_widget = content_widget
        self.page_widget = self.content_widget.page_widget
        self.build()

    def build(self):

        combobox_stylesheet = '''
        QComboBox {
            background-color: palette(dark);
            border: 2px solid palette(button);
            border-radius: 7px;
        }
        QComboBox::drop-down {
            background-color: palette(button);
            border-radius: 4px;
        }
        QComboBox QAbstractItemView::item {
            min-height: 20px;
        }'''

        self.filter_label = QtWidgets.QLabel('Filter by:')

        current_filter = self.page_widget.session.cmds.Flow.get_value(self.page_widget.oid + '/type_filter')

        # self.filter_status_label = QtWidgets.QLabel('Status:')

        self.filter_status_combobox = QtWidgets.QComboBox()
        self.filter_status_combobox.addItems(['All Types', 'File', 'Folder', 'Task', 'Shot', 'Sequence', 'Film', 'Asset', 'AssetType'])
        self.filter_status_combobox.setCurrentText(current_filter[0] if current_filter else 'All Types')
        self.filter_status_combobox.currentTextChanged.connect(self._on_filter_changed)
        self.filter_status_combobox.setView(QtWidgets.QListView())
        self.filter_status_combobox.setStyleSheet(combobox_stylesheet)

        query = self.page_widget.session.cmds.Flow.get_value(self.page_widget.oid + '/query')
        self.results_label = QtWidgets.QLabel(f'Results for: <b>{query}</b>')

        hlo = QtWidgets.QHBoxLayout(self)
        hlo.addWidget(self.results_label)
        hlo.addStretch()
        hlo.addWidget(self.filter_label)
        hlo.addWidget(self.filter_status_combobox)

        probe = self.page_widget.probe

        self.filter_label.setVisible(probe)
        self.filter_status_combobox.setVisible(probe)
        # self._on_filter_changed(current_filter)
    
    def _on_filter_changed(self, value):

        if value == 'File':
            self.content_widget.list.list.type_filters = ['TrackedFile']
            self.page_widget.session.cmds.Flow.set_value(self.page_widget.oid + '/type_filter', ['TrackedFile'])
            self.filter_label.setText('<b>Filter by:</b>')
        elif value == 'Folder':
            self.content_widget.list.list.type_filters = ['TrackedFolder']
            self.page_widget.session.cmds.Flow.set_value(self.page_widget.oid + '/type_filter', ['TrackedFolder'])
            self.filter_label.setText('<b>Filter by:</b>')
        elif value == 'All Types':
            self.content_widget.list.list.type_filters = None
            self.page_widget.session.cmds.Flow.set_value(self.page_widget.oid + '/type_filter', None)
            self.filter_label.setText('Filter by:')
        else:
            self.content_widget.list.list.type_filters = [value]
            self.page_widget.session.cmds.Flow.set_value(self.page_widget.oid + '/type_filter', [value])
            self.filter_label.setText('<b>Filter by:</b>')
        
        self.content_widget.list.list.full_refresh()




class FileActionsButton(QtWidgets.QToolButton):
    """
    Holds the file's action shortcuts displayed in the file list.
    """
    def __init__(self, item):
        super(FileActionsButton, self).__init__()
        self.item = item
        self.build()
    
    def build(self):
        self.setIcon(resources.get_icon(('icons.gui', 'menu')))
        self.setIconSize(QtCore.QSize(16, 16))
        self.setStyleSheet('''
                            QToolButton::menu-indicator { image: none; }
                            QToolButton:pressed {background-color: palette(mid)}''')
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setFixedWidth(30)

        # Add actions
        self.menu = QtWidgets.QMenu('File actions')

        self.goto_oid = QtWidgets.QAction('Go to')
        self.goto_oid.setIcon(resources.get_icon(('icons.libreflow', 'share-option')))
        self.goto_oid.triggered.connect(self._goto_oid)

        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setArrowType(QtCore.Qt.NoArrow)
        self.setMenu(self.menu)
    
    def mousePressEvent(self, event):
        has_actions = self.item.action_manager.update_oid_menu(
            self.item.oid, self.menu, with_submenus=True
        )

        if has_actions :
            self.menu.insertAction(self.menu.actions()[0], self.goto_oid)
        else:
            self.menu.addAction(self.goto_oid)

        super(FileActionsButton, self).mousePressEvent(event)
    
    def _goto_oid(self):
        self.item.page_widget.page.goto(self.item.oid)


class SearchResultItem(QtWidgets.QWidget):
    def __init__(self, results_list, data):
        super(SearchResultItem, self).__init__()
        self.setObjectName('SearchResultItem')
        self.results_list = results_list
        self.page_widget = self.results_list.page_widget

        data.setdefault('type', '')


        self.label = data['label']
        self.oid = data['goto_oid']
        self.type = data['type']

        self.setStyleSheet('''
                            QLabel { font:10pt; }
                            #SearchResultItem: ''')
        
        self.action_manager = ObjectActionMenuManager(
            self.page_widget.session, self.page_widget.page.show_action_dialog, 'Flow.map'
        )

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

        self.build()
    
    def build(self):
        container = QtWidgets.QHBoxLayout(self)
        container.setContentsMargins(0,0,0,0)
        container.setSpacing(30)


        #Create Icon - Label layout

        name_label = QtWidgets.QLabel(self.label)
        name_label.setToolTip('Double-click : open this item')
        icon_label = QtWidgets.QLabel()

        icon_name_widget = QtWidgets.QHBoxLayout()
        icon_name_widget.setContentsMargins(0,0,0,0)
        icon_name_widget.setSpacing(7)

        icon_name_widget.addWidget(icon_label)
        icon_name_widget.addWidget(name_label)

        # try :
        #     icon_loc = self.page_widget.session.cmds.Flow.call(self.oid, 'get_icon', [], {})
        # except AttributeError:
        #     icon_loc = None

        # if icon_loc :
            # icon = QtGui.QIcon(resources.get_icon(icon_loc))
        icon_label.setPixmap(self.get_icon(self.type).pixmap(QtCore.QSize(18, 18)))

        if self.type == 'TrackedFile':
            type_label = QtWidgets.QLabel('<b>File</b>')
        elif self.type ==  'TrackedFolder':
            type_label = QtWidgets.QLabel('<b>Folder</b>')
        else :
            type_label = QtWidgets.QLabel(f'<b>{self.type}</b>')
            
        menu_button = FileActionsButton(self)
        

        # name_label.setIcon(icon)

        # menu_button.triggered.connect(lambda: self._on_menu_button_pressed(QtGui.QMouseEvent.globalPosition().toPoint()))
        container.addLayout(icon_name_widget)
        container.addStretch()
        container.addWidget(type_label)
        container.addWidget(menu_button)

        self.goto_oid = QtWidgets.QAction('Go to')
        self.goto_oid.setIcon(resources.get_icon(('icons.libreflow', 'share-option')))
        self.goto_oid.triggered.connect(self._goto_oid)
    
    def mouseDoubleClickEvent(self, event):
        self.setBackgroundRole(QtGui.QPalette.Midlight)

        if self.type in ['TrackedFile', 'TrackedFolder']:
            self.page_widget.page.show_action_dialog(
                f"{self.oid}/open"
            )
        else:
            self.page_widget.page.goto(self.oid)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtGui.Qt.RightButton :
            self.customContextMenuRequested.emit(event.globalPos())

        super(SearchResultItem, self).mouseReleaseEvent(event)

    def _on_context_menu_requested(self, pos):

        action_menu = QtWidgets.QMenu(self)

        has_actions = self.action_manager.update_oid_menu(
            self.oid, action_menu, with_submenus=True
        )

        if has_actions :
            action_menu.insertAction(action_menu.actions()[0], self.goto_oid)
        else:
            action_menu.addAction(self.goto_oid)

        # if has_actions:
            # action_menu.exec_(self.results_list.viewport().mapToGlobal(pos))
        action_menu.exec_(pos)
    
    def _goto_oid(self):
        self.page_widget.page.goto(self.oid)
    
    def get_icon(self, _type):

        if _type == 'TrackedFile' :
            ext = self.label.split('.')[-1]
            icon_ref = FILE_EXTENSION_ICONS.get(ext, ('icons.gui', 'text-file'))
        elif _type ==  'TrackedFolder':
            icon_ref =('icons.gui', 'folder-white-shape')
        elif _type == 'Asset':
            icon_ref = ('icons.libreflow', '3d-object')
        elif _type == 'Task':
            icon_ref = ('icons.gui', 'cog-wheel-silhouette')
        elif _type == 'Sequence':
            icon_ref = ('icons.flow', 'sequence')
        elif _type == 'Shot':
            icon_ref = ('icons.flow', 'shot')
        elif _type == 'Film':
            icon_ref = ('icons.flow', 'film')
        else :
            icon_ref = ('icons.gui', 'text-file')

        return QtGui.QIcon(resources.get_icon(icon_ref))



class SearchResultsList(QtWidgets.QTableWidget):
    def __init__(self, content_widget):
        super(SearchResultsList, self).__init__(content_widget)
        self.content_widget = content_widget
        self.page_widget = self.content_widget.page_widget

        self.query=''

        self.page_count = 1
        self.results_count = 0
        self.cellsContent = []

        self.type_filters = None

        self.setColumnCount(1)
        self.setShowGrid(False)

        self.verticalScrollBar().valueChanged.connect(self.scroll_value_changed)

        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)

        self.setStyleSheet(
            '''
            QTableWidget {
                border: none;
                background-color: transparent;
            }
            '''
        )

        # self.cellClicked.connect(self.cell_click_filter)
        # self.cellDoubleClicked.connect(self.on_item_doubleclicked)
    
    def refresh(self):
        self.query = self.page_widget.session.cmds.Flow.get_value(self.page_widget.oid + '/query')
        self.type_filters = self.page_widget.session.cmds.Flow.get_value(self.page_widget.oid + '/type_filter')
        results,count = self.search_results(self.query, page=self.page_count)
        for r in results:

            start_r, start_c = self.get_last_idx()
            if start_c == 0:
                self.setRowCount(start_r + 1)

            item = SearchResultItem(self,r)
            lo = QtWidgets.QHBoxLayout()
            lo.addWidget(item)
            lo.setContentsMargins(3,3,3,3)

            widget = QtWidgets.QWidget()
            widget.setLayout(lo)
            self.setCellWidget(start_r, start_c, widget)
            self.setRowHeight(start_r, 30)

            self.cellsContent.append((start_r, start_c, widget))

        self.page_widget.footer.update_count(count, len(self.cellsContent))

        # if len(self.cellsContent) < count:
        #     # Add show more button
        #     start_r, start_c = self.get_last_idx()
        #     if start_c == 0:
        #         self.setRowCount(start_r + 1)
        #     button = QtWidgets.QPushButton('Show more')
        #     button.setMaximumWidth(200)
        #     button.clicked.connect(self.on_show_more_clicked)
        #     lo = QtWidgets.QHBoxLayout()
        #     lo.addWidget(button)
        #     lo.setContentsMargins(3,3,3,3)

        #     widget = QtWidgets.QWidget()
        #     widget.setLayout(lo)
        #     self.setCellWidget(start_r, start_c, widget)
        #     self.setRowHeight(start_r, 50)

        #     self.cellsContent.append((start_r, start_c, widget))

        self.resizeColumnsToContents()

    def get_last_idx(self):
        last_r, last_c = divmod(len(self.cellsContent), self.columnCount())
        return last_r, last_c
    
    def search_results(self, text, page=1):
        project_name = self.page_widget.get_project_name()
        exclude_types = None
        if "." in text:
            exclude_types = ['Sequence','Shot','Task','Film','Asset','AssetType','TrackedFolder']
        results,count = self.page_widget.session.cmds.Search.query_project_index(
            project_name, text, limit=50, page=page, exclude_types=exclude_types, include_types = self.type_filters)
        return results,count

    def on_show_more_clicked(self):
        bar_value = self.verticalScrollBar().value()
        # row, column, widget = self.cellsContent[-1]
        # widget.deleteLater()
        # self.cellsContent.pop(-1)
        # self.removeRow(row)

        self.page_count += 1
        self.refresh()
        self.verticalScrollBar().setValue(bar_value)
    
    def full_refresh(self):
        self.page_count = 1
        self.results_count = 0
        self.cellsContent = []
        self.clear()
        self.refresh()
    
    def cell_click_filter(self,r,c):
        widget = self.cellWidget(r,c)
    
    def scroll_value_changed(self, value):
        if value >= self.verticalScrollBar().maximum():
            self.on_show_more_clicked()
            


class SearchResultsBox(QtWidgets.QWidget):
    def __init__(self, content_widget):
        super(SearchResultsBox, self).__init__(content_widget)
        self.setObjectName('SearchResultsBox')
        self.content_widget = content_widget
        self.page_widget = self.content_widget.page_widget

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('#SearchResultsBox { background-color: palette(window); border-radius: 5px; }')

        self.build()

    def build(self):
        box = QtWidgets.QVBoxLayout(self)
        self.list = SearchResultsList(self)
        box.addWidget(self.list)


class SearchFooter(QtWidgets.QWidget):
    def __init__(self, page_widget):
        super(SearchFooter, self).__init__(page_widget)
        self.page_widget = page_widget
        self.build()
    
    def build(self):
        self.left_text = QtWidgets.QLabel()
        self.left_text.setText('0 Items found')

        self.right_text = QtWidgets.QLabel()
        self.right_text.setText('<font color = red><b>Project indexation not up to date</b></font>')

        flo = QtWidgets.QHBoxLayout(self)
        flo.addWidget(self.left_text)
        flo.addStretch()
        flo.addWidget(self.right_text)

        self.right_text.setVisible(not self.page_widget.probe)
    
    def update_count(self, total, loaded):
        self.left_text.setText(f'{total} items found ({loaded} loaded)')
    


class SearchContent(QtWidgets.QWidget):
    def __init__(self, page_widget):
        super(SearchContent, self).__init__(page_widget)
        self.setObjectName('SearchContent')
        self.page_widget = page_widget

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('#SearchContent { background-color: palette(dark); border-radius: 5px; }')

        self.build()

    def build(self):
        grid = QtWidgets.QGridLayout(self)

        self.header = SearchHeader(self)
        self.list = SearchResultsBox(self)
        grid.addWidget(self.header, 0, 0)
        grid.addWidget(self.list, 1, 0)

class SearchPageWidget(CustomPageWidget):
    def build(self):

        self.probe = self.probe()

        self.content = SearchContent(self)
        self.footer = SearchFooter(self)


        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(0,0,0,0)
        vlo.setSpacing(1)
        vlo.addWidget(self.content)
        vlo.addWidget(self.footer)

        self.content.list.list.refresh()

    def get_project_name(self):
        return self.session.cmds.Flow.call(
            self.get_project_oid(), 'name', {}, {}
        )
    
    def get_project_oid(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_project_oid', {}, {}
        )
    
    def probe(self):
        project_name = self.get_project_name()
        result,count = self.session.cmds.Search.query_project_index(
            project_name, project_name, limit=1, page=1,)

        return 'type' in result[0]
        # return result


class Search(flow.Object):

    _project = flow.Parent()

    query = flow.SessionParam('')

    type_filter = flow.SessionParam(None)


    def _fill_ui(self, ui):
        ui["custom_page"] = "libreflow.baseflow.search.SearchPageWidget"
    
    def get_project_oid(self):
        return self.root().project().oid()