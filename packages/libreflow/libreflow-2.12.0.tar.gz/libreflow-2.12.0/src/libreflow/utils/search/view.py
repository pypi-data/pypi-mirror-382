from kabaret.app import plugin
from kabaret.app.ui.gui.widgets.flow.flow_view import FlowView
from kabaret.app.ui.gui.widgets.widget_view import QtWidgets, QtGui, QtCore
from kabaret.app.ui.gui.icons import flow as _
from kabaret.app import resources

from .data import icons as _


def clear_layout(layout):
    if layout is None:
        return
    
    item = layout.takeAt(0)

    while item is not None:
        if item.layout() is not None:
            item_layout = item.layout()
            clear_layout(item_layout)
            del item_layout
        if item.widget() is not None:
            item_widget = item.widget()
            item_widget.setParent(None)
            del item_widget
        
        del item
        item = layout.takeAt(0)


class AutoIndexingTargetItem(QtWidgets.QWidget):
    '''
    Widget representing a filter target.
    '''

    def __init__(self, targets_widget, pattern, depth):
        super(AutoIndexingTargetItem, self).__init__()
        self.targets_widget = targets_widget

        self.pattern_lineedit = QtWidgets.QLineEdit(pattern)
        self.depth_lineedit = QtWidgets.QLineEdit(str(depth))
        self.depth_lineedit.setValidator(QtGui.QIntValidator(1, 500))
        self.depth_lineedit.setMaximumWidth(40)
        self.depth_lineedit.setAlignment(QtCore.Qt.AlignRight)
        self.remove_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'remove')), '')
        self.remove_button.setFixedSize(28, 28)
        self.remove_button.setFocusPolicy(QtCore.Qt.NoFocus)

        lo = QtWidgets.QHBoxLayout()
        lo.setSpacing(1)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.addWidget(self.pattern_lineedit)
        lo.addWidget(self.depth_lineedit)
        lo.addWidget(self.remove_button)
        self.setLayout(lo)

        self.pattern_lineedit.editingFinished.connect(self._on_field_editing_finished)
        self.depth_lineedit.editingFinished.connect(self._on_field_editing_finished)
        self.remove_button.clicked.connect(self._on_remove_button_clicked)
    
    def target(self):
        return (self.pattern_lineedit.text(), self.depth_lineedit.text())
    
    def _on_field_editing_finished(self):
        self.targets_widget.filter_item.update_targets()
    
    def _on_remove_button_clicked(self, checked=False):
        self.targets_widget.remove_target_item(self)


class AutoIndexingTargetsWidget(QtWidgets.QWidget):

    def __init__(self, filter_item, oid_targets):
        super(AutoIndexingTargetsWidget, self).__init__()

        self.filter_item = filter_item
        self.target_items = []

        self.add_target_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'plus-button')), '')
        self.add_target_button.setFocusPolicy(QtCore.Qt.NoFocus)

        lo = QtWidgets.QVBoxLayout()
        lo.setSpacing(1)
        lo.setContentsMargins(0, 2, 0, 2)
        self.setLayout(lo)

        for target in oid_targets:
            if target is not None:
                self.add_target_item(target[0], target[1])
        
        self.layout().addWidget(self.add_target_button)

        self.add_target_button.clicked.connect(self._on_add_target_button_clicked)
    
    def targets(self):
        return [ i.target() for i in self.target_items ]
    
    def add_target_item(self, pattern, depth):
        item = AutoIndexingTargetItem(self, pattern, depth)
        self.layout().insertWidget(self.layout().count() - 1, item)
        self.target_items.append(item)

        return item
    
    def remove_target_item(self, item):
        self.layout().removeWidget(item)
        item.setParent(None)
        self.target_items.remove(item)
        del item

        self.filter_item.update_targets()
    
    def _on_add_target_button_clicked(self, checked=False):
        item = self.add_target_item('', 1)
        item.pattern_lineedit.setFocus()
        self.filter_item.update_targets()


class AutoIndexingFilterItem(QtWidgets.QWidget):
    '''
    Widget representing a filter.
    '''

    def __init__(self, filter_list, filter_id, oid_pattern, oid_targets, enabled, index_matches):
        super(AutoIndexingFilterItem, self).__init__()
        self.session = filter_list.session
        self.filter_list = filter_list
        self.id = filter_id

        self.expand_button = QtWidgets.QToolButton()
        self.expand_button.setIcon(resources.get_icon(('icons.flow', 'collapsed')))
        self.expand_button.setFixedSize(28, 28)
        self.expand_button.setCheckable(True)
        self.expand_button.setChecked(False)
        self.enable_checkbox = QtWidgets.QCheckBox()
        self.enable_checkbox.setCheckState(QtCore.Qt.Checked if enabled else QtCore.Qt.Unchecked)
        self.index_matches_button = QtWidgets.QPushButton()
        icon = QtGui.QIcon()
        icon.addFile(
            resources.get('icons.search', 'filter-enabled'),
            state=QtGui.QIcon.On)
        icon.addFile(
            resources.get('icons.search', 'filter-disabled'),
            state=QtGui.QIcon.Off)
        self.index_matches_button.setIcon(icon)
        self.index_matches_button.setFixedSize(28, 28)
        self.index_matches_button.setCheckable(True)
        self.index_matches_button.setChecked(index_matches)
        self.index_matches_button.setToolTip('Enable indexing of objects matching this filter')
        self.pattern_lineedit = QtWidgets.QLineEdit(oid_pattern)
        self.remove_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'remove')), '')
        self.remove_button.setFixedSize(28, 28)
        self.remove_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.targets_widget = AutoIndexingTargetsWidget(self, oid_targets)
        self.targets_widget.hide()

        lo = QtWidgets.QGridLayout()
        lo.setSpacing(1)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.addWidget(self.expand_button, 0, 0)
        lo.addWidget(self.enable_checkbox, 0, 1)
        lo.addWidget(self.index_matches_button, 0, 2)
        lo.addWidget(self.pattern_lineedit, 0, 3)
        lo.addWidget(self.remove_button, 0, 4)
        lo.addWidget(self.targets_widget, 1, 3)
        self.setLayout(lo)

        self.enable_checkbox.stateChanged.connect(self._on_enable_checkbox_state_changed)
        self.index_matches_button.toggled.connect(self._on_filter_button_toggled)
        self.pattern_lineedit.editingFinished.connect(self._on_pattern_editing_finished)
        self.expand_button.clicked.connect(self._on_expand_button_clicked)
        self.remove_button.clicked.connect(self._on_remove_button_clicked)
    
    def update_targets(self):
        self.session.cmds.Search.update_filter_targets(self.id, self.targets_widget.targets())
    
    def _on_enable_checkbox_state_changed(self, state):
        self.session.cmds.Search.update_filter(self.id, self.pattern_lineedit.text(), state == QtCore.Qt.Checked, self.index_matches_button.isChecked())
    
    def _on_pattern_editing_finished(self):
        self.session.cmds.Search.update_filter(self.id, self.pattern_lineedit.text(), self.enable_checkbox.checkState() == QtCore.Qt.Checked, self.index_matches_button.isChecked())
    
    def _on_filter_button_toggled(self, checked):
        self.session.cmds.Search.update_filter(self.id, self.pattern_lineedit.text(), self.enable_checkbox.checkState() == QtCore.Qt.Checked, checked)
    
    def _on_expand_button_clicked(self, checked=False):
        self.expand_button.setIcon(resources.get_icon(('icons.flow', 'expanded' if checked else 'collapsed')))
        self.targets_widget.setVisible(checked)
    
    def _on_remove_button_clicked(self, checked=False):
        self.filter_list.remove_filter_item(self.id)
        self.session.cmds.Search.remove_indexing_filter(self.id)


class IndexingFilterList(QtWidgets.QWidget):
    '''
    Widget representing the list of filters.
    '''

    def __init__(self, session):
        super(IndexingFilterList, self).__init__()
        self.session = session

        self._filters_by_id = {}
        
        lo = QtWidgets.QVBoxLayout()
        lo.setSpacing(2)
        lo.setContentsMargins(1, 1, 1, 1)
        self.setLayout(lo)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    
    def reload_filters(self):
        clear_layout(self.layout())

        for _id, pattern, targets, enabled, index_matches in self.session.cmds.Search.list_indexing_filters():
            self.add_filter_item(_id, pattern, targets, enabled, index_matches)
    
    def add_filter_item(self, _id, pattern, targets, enabled, index_matches):
        if targets is None:
            targets = []
        
        item = AutoIndexingFilterItem(self, _id, pattern, targets, enabled, index_matches)
        self.layout().addWidget(item)
        self._filters_by_id[_id] = item

        return item
    
    def remove_filter_item(self, _id):
        item = self._filters_by_id[_id]
        self.layout().removeWidget(item)
        item.setParent(None)
        del item


class SearchSettingsDialog(QtWidgets.QDialog):

    def __init__(self, parent, session):
        super(SearchSettingsDialog, self).__init__(parent)
        self.session = session
        self.setWindowTitle('Search settings')
        self.setWindowIcon(resources.get_icon(('icons.search', 'magn-glass')))
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.build_index_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'run-button')), 'Rebuild project index')
        self.project_combobox = QtWidgets.QComboBox()
        self.scroll_area = QtWidgets.QScrollArea()
        self.filter_list = IndexingFilterList(session)
        self.add_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'plus-button')), '')
        self.add_button.setToolTip('Add new filter')
        self.add_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.add_button.setMinimumWidth(200)
        self.import_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'import')), '')
        self.import_button.setToolTip('Import template')
        self.import_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.export_button = QtWidgets.QPushButton(resources.get_icon(('icons.search', 'export')), '')
        self.export_button.setToolTip('Export filters as template')
        self.export_button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.scroll_area.setWidget(self.filter_list)
        self.scroll_area.setWidgetResizable(True)

        # Confirmation dialog for index building
        self.confirm_dialog = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Information,
            'Rebuild search index',
            '<h2>This will take some time</h2>',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            self
        )
        self.confirm_dialog.setTextFormat(QtCore.Qt.RichText)
        self.confirm_dialog.setInformativeText((
            'You are using an early version of this indexing feature, which is not optimised '
            'yet (the whole project is scanned once per each indexing filter).\n\nDo you '
            'want to continue ?'
        ))
        self.confirm_dialog.resize(300, 200)

        # Import/export dialogs
        self.import_dialog = QtWidgets.QFileDialog()
        self.import_dialog.setWindowTitle('Select filter template')
        self.import_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        self.import_dialog.setNameFilter('JSON file (*.json, *.JSON)')
        self.import_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
        self.export_dialog = QtWidgets.QFileDialog()
        self.export_dialog.setWindowTitle('Save filter template')
        self.export_dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        self.export_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        self.export_dialog.setNameFilter('JSON file (*.json, *.JSON)')
        self.export_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
        self.export_dialog.setDefaultSuffix('json')

        lo = QtWidgets.QGridLayout()
        lo.setSpacing(0)
        lo.setContentsMargins(0, 0, 0, 0)

        index_lo = QtWidgets.QGridLayout()
        index_lo.setSpacing(0)
        index_lo.setContentsMargins(0, 0, 0, 0)
        index_lo.addWidget(self.build_index_button, 0, 0)
        index_lo.addWidget(self.project_combobox, 0, 1, 1, 4)
        
        filters_lo = QtWidgets.QGridLayout()
        filters_lo.setSpacing(2)
        filters_lo.setContentsMargins(0, 10, 0, 0)
        filters_lo.addWidget(QtWidgets.QLabel('<b>Indexing filters</b>'), 0, 0)
        filters_lo.addWidget(self.scroll_area, 1, 0, 1, 5)

        button_lo = QtWidgets.QHBoxLayout()
        button_lo.setSpacing(0)
        button_lo.setContentsMargins(0, 0, 0, 0)
        button_lo.addWidget(self.import_button)
        button_lo.addWidget(self.export_button)

        lo.addLayout(index_lo, 0, 0, 1, 5)
        lo.addLayout(filters_lo, 1, 0, 1, 5)
        lo.addWidget(self.add_button, 2, 2, QtCore.Qt.AlignCenter)
        lo.addLayout(button_lo, 2, 4, QtCore.Qt.AlignRight)
        self.setLayout(lo)

        self.build_index_button.clicked.connect(self._on_build_index_button_clicked)
        self.add_button.clicked.connect(self._on_add_button_clicked)
        self.import_button.clicked.connect(self._on_import_button_clicked)
        self.export_button.clicked.connect(self._on_export_button_clicked)

        self.resize(600, 400)
    
    def show(self):
        self.reload_project_names()
        self.filter_list.reload_filters()
        super(SearchSettingsDialog, self).show()
    
    def reload_project_names(self):
        self.project_combobox.clear()
        self.project_combobox.addItems(self.session.cmds.Search.list_project_names())
    
    def _on_build_index_button_clicked(self, checked=False):
        if self.confirm_dialog.exec_() == QtWidgets.QMessageBox.Yes:
            self.session.cmds.Search.rebuild_project_index(
                self.project_combobox.currentText(),
                f'/{self.project_combobox.currentText()}/films',
                max_depth=9
            )
            self.session.cmds.Search.rebuild_project_index(
                self.project_combobox.currentText(),
                f'/{self.project_combobox.currentText()}/asset_types',
                max_depth=9
            )
    
    def _on_add_button_clicked(self, checked=False):
        _id = self.session.cmds.Search.add_indexing_filter('', [], True, False)
        item = self.filter_list.add_filter_item(_id, '', [], True, False)
        item.pattern_lineedit.setFocus()
    
    def _on_import_button_clicked(self, checked=False):
        if(self.import_dialog.exec_()):
            path = self.import_dialog.selectedFiles()[0]
            self.session.cmds.Search.load_filter_template(path)
            self.filter_list.reload_filters()
    
    def _on_export_button_clicked(self, checked=False):
        if(self.export_dialog.exec_()):
            path = self.export_dialog.selectedFiles()[0]
            self.session.cmds.Search.dump_filter_template(path)


class SearchFlowView(FlowView):

    def __init__(self, session, view_id=None, hidden=False, area=None, oid=None, root_oid=None):
        self.search_bar = None
        super(SearchFlowView, self).__init__(session, view_id=view_id, hidden=hidden, area=area, oid=oid, root_oid=root_oid)

    def build_top(self, top_parent, top_layout, header_parent, header_layout):
        super(SearchFlowView, self).build_top(top_parent, top_layout, header_parent, header_layout)
        self.search_bar = SearchBar(top_parent, self, self.session)
        top_layout.addWidget(self.search_bar)


class SearchFlowViewPlugin:
    """
    Custom Flow view.

    Will only be installed if no other view
    is registered under the "Flow" view type name.
    """

    @plugin(trylast=True)
    def install_views(session):
        if not session.is_gui():
            return

        type_name = SearchFlowView.view_type_name()
        if not session.has_view_type(type_name):
            session.register_view_type(SearchFlowView)
            session.add_view(type_name)
        
        # Touch all the projects existing on the current cluster
        projects_info = session.get_actor('Flow').get_projects_info()
        for project_name, _ in projects_info:
            session.cmds.Flow.call(
                f'/{project_name}', 'touch', args=[], kwargs={}
            )
