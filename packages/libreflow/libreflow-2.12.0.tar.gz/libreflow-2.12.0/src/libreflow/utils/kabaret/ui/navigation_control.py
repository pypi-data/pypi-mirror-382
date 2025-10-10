import six
import qtpy
import functools
import logging

from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtGui, QtCore
from kabaret.app.ui.gui.widgets.flow_layout import FlowLayout
from kabaret.app.ui.gui.widgets.popup_menu import PopupMenu
from kabaret.app import resources


class Separator(QtWidgets.QToolButton):
    def __init__(self, related_navigation_button):
        super(Separator, self).__init__(related_navigation_button)
        self.setProperty("class", "nav_separator")
        self.related_navigation_button = related_navigation_button
        self.setText('>')
    
    def mousePressEvent(self, e):
        self.related_navigation_button._show_navigables_menu(self.related_navigation_button.nav_widget.current_oid())
        super(Separator, self).mousePressEvent(e)


class NavigationButton(QtWidgets.QToolButton):

    def __init__(self, name, oid, nav_widget, is_last=False):
        super(NavigationButton, self).__init__(nav_widget)
        self.name = name
        self.oid = oid
        self.nav_widget = nav_widget
        self._last_click_pos = QtCore.QPoint()

        self.setFont(self.nav_widget.bt_font)
        self.setProperty('tight_layout', True)
        self.setProperty('hide_arrow', True)
        self.setProperty('no_border', True)
        self.setProperty('square', True)
        self.setArrowType(QtCore.Qt.NoArrow)
        self.setProperty('last', is_last)

        # Removed the map name before the ":"
        # Not changing it 
        self.setText('%s' % (self.name.split(":")[-1],))

        self.clicked.connect(self._goto)

        self._menu = PopupMenu(self)

    def _goto_oid(self, oid):
        self.nav_widget._goto(oid)
    
    def _goto(self, b=None):
        self.nav_widget._goto(self.oid)

    def _show_navigables_menu(self, full_oid):
        self._menu.clear()

        m = self._menu

        m.addAction('Loading...')
        # self.setMenu(m)
        # self.showMenu()

        session = self.nav_widget._navigator.session
        try:
            navigatable_entries = session.cmds.Flow.get_navigable_oids(
                self.oid, full_oid
            )
        except Exception as err:
            m.clear()
            m.addAction('ERROR: ' + str(err))
            raise
        m.clear()
        root = m
        for i, entry in enumerate(navigatable_entries, 1):
            if entry is None:
                m.addMenu()
            else:
                label, oid = entry
                if oid == self.oid:
                    item = m.addItem(
                        '> %s <' % label
                    )
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                else:
                    m.addAction(label, callback=functools.partial(self._goto_oid, oid))

        root.addMenu()
        root.addAction("Copy", icon=resources.get_icon(('icons.gui', 'copy-document')),
                       callback=lambda: QtWidgets.QApplication.clipboard().setText(self.oid))
        root.addAction("Paste", icon=resources.get_icon(('icons.gui', 'paste-from-clipboard')),
                       callback=lambda: self._goto_oid(QtWidgets.QApplication.clipboard().text()))
        m.popup(QtGui.QCursor.pos())

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self._show_navigables_menu(self.nav_widget.current_oid())
        else:
            self._last_click_pos = e.pos()
        super(NavigationButton, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        super(NavigationButton, self).mouseMoveEvent(e)

        if self._last_click_pos.isNull():
            return
        drag_distance = (e.pos() - self._last_click_pos).manhattanLength()
        if drag_distance < QtWidgets.QApplication.startDragDistance():
            return

        oids = [self.oid]
        mime_data = QtCore.QMimeData()
        md = self.nav_widget._navigator.session.cmds.Flow.to_mime_data(oids)
        for data_type, data in six.iteritems(md):
            mime_data.setData(data_type, data)

        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)

        # below makes the pixmap half transparent
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()

        # make a QDrag
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)

        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(self._last_click_pos)

        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        drag_result = drag.exec_(QtCore.Qt.CopyAction)

    def mouseReleaseEvent(self, e):
        self._last_click_pos = QtCore.QPoint()
        super(NavigationButton, self).mouseReleaseEvent(e)


class NavigationOIDControls(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(NavigationOIDControls, self).__init__(parent)

        self._navigator = navigator

        self.nav_oid_bar = parent
        self.bt_font = self.font()
        self.bt_font.setPointSize(int(self.bt_font.pointSize()))

        self._flow_lo = FlowLayout()
        self.setLayout(self._flow_lo)
        self._flow_lo.setContentsMargins(2, 0, 2, 0)
        self._flow_lo.setSpacing(0)

    def update_controls(self):
        self._flow_lo.clear()

        label_to_oid = self._navigator.split_current_oid()
        i = 1
        
        for label, goto_oid in label_to_oid:
            if i>1 :
                self._flow_lo.addWidget(Separator(tb))
            tb = NavigationButton(label, goto_oid, self, i == len(label_to_oid))
            tb.adjustSize()
            self._flow_lo.addWidget(tb)
            i += 1
        if not self.isVisible():
            self.show()

    def _goto_home(self):
        self._navigator.goto_root()

    def _goto(self, oid):
        in_new_view = (
            QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
        )
        self._navigator.goto(oid, in_new_view)

    def current_oid(self):
        return self._navigator.current_oid()


class SearchEntriesStringListModel(QtCore.QStringListModel):

    def __init__(self, line_edit):
        super(SearchEntriesStringListModel, self).__init__()
        self.line_edit = line_edit

    def data(self, index, role):
        if self.line_edit.search_enabled():
            res = self.line_edit.get_search_result(index.row())
            if role == QtCore.Qt.EditRole:
                return res['goto_oid']
            elif role == QtCore.Qt.DisplayRole:
                return res['label']
        else:
            if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
                return self.line_edit.get_completion(index.row())


class CustomListView(QtWidgets.QListView):
    '''
    List view used by the OID field's completer to validate
    instantly a clicked result.
    '''
    def __init__(self, oid_field):
        super(CustomListView, self).__init__()
        self._oid_field = oid_field
        
    def mouseReleaseEvent(self, e):
        self._oid_field.accept()
        super(CustomListView, self).mouseReleaseEvent(e)
        self.hide()


class NavigationOIDField(QtWidgets.QLineEdit):
    def __init__(self, parent, navigator):
        super(NavigationOIDField, self).__init__(parent)
        self._navigator = navigator
        self.session = navigator.session
        self.nav_oid_bar = parent
        
        field_font = self.font()
        field_font.setPointSize(int(field_font.pointSize()))
        self.setFont(field_font)

        self._completions = None
        self._search_results = None
        self.completer_view = CustomListView(self)
        self.completer = QtWidgets.QCompleter([], self)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setModel(SearchEntriesStringListModel(self))
        self.completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.completer.setPopup(self.completer_view)
        self.setCompleter(self.completer)

        self.textEdited.connect(self.on_text_edited)

    def on_text_edited(self, text):
        # self.completer.model().beginResetModel()

        if text.startswith('/'):
            self.set_search_enabled(False)
            self._completions = self.update_completion(text)
            self.completer.model().setStringList(self._completions)
        else:
            self.set_search_enabled(True)
            self._search_results = self.update_search_results(text)
            self.completer.model().setStringList([r['goto_oid'] for r in self._search_results])
        
        # self.completer.model().endResetModel()
    
    def get_search_result(self, index):
        return self._search_results[index]
    
    def get_completion(self, index):
        return self._completions[index]

    def get_completion_current_oid(self, text):
        if text.endswith("/"):
            return text
        else:
            return text.rpartition("/")[0] + "/"

    def update_completion(self, text):
        current_oid = self.get_completion_current_oid(text)
        completion_oid_list = []

        def exists(oid):
            ret = False
            try:
                ret = self.session.cmds.Flow.exists(oid)
            except:
                pass
            return ret

        if not current_oid or current_oid == "/":
            # Get list of project
            projects = self.session.get_actor("Flow").get_projects_info()
            completion_oid_list = list(map(lambda p: "/" + p[0], projects))
            # Add the Home Oid to the autocompletion list
            completion_oid_list.append(self.session.get_actor("Flow").home_root().Home.oid())
        elif exists(current_oid):
            # get list of children of current oid
            navigatable_entries =  self.session.cmds.Flow.get_navigable_oids(
                current_oid.rpartition("/")[0], current_oid.rpartition("/")[0]
            )
            completion_oid_list = list(map(lambda navigatable_entry: navigatable_entry[1] ,navigatable_entries[navigatable_entries.index(None)+1:]))
        else:
            # TODO : RAISE ERROR ?
            logging.getLogger('kabaret').log(logging.DEBUG, f"INVALID OID : {current_oid}")
            self.setProperty('error', True)

        return completion_oid_list
    
    def update_search_results(self, text): 
        results,count = self.session.cmds.Search.query_project_index(
            self.nav_oid_bar.selected_project(), text, exclude_types=["TrackedFile", "TrackedFolder"])
        return results
    
    def search_enabled(self):
        return self.nav_oid_bar.search_enabled()
    
    def set_search_enabled(self, b):
        self.nav_oid_bar.set_search_enabled(b)

    def reset(self):
        self.setText(self._navigator.current_oid())
        self.setProperty('edited', False)

    def edit(self):
        self.reset()
        self.show()
        self.selectAll()
        self.setFocus()
        self.nav_oid_bar.nav_oid.hide()

    def accept(self):
        oid = self.text().strip()
        # HACK to remove a final '/' as user might forget it in manual editing of OIDs
        if len(oid) > 0:
            if oid[-1] == "/":
                oid = oid[:-1]
        try:
            exists = self._navigator.session.cmds.Flow.exists(oid)
        except:
            exists = False
        if not exists:

            # redirection vers la page de recherche

            in_new_view = (
            QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
            )
            oid = self._navigator._current_oid
            project = oid.split("/")[1]
            search_oid = "/%s/search" % project
            self._navigator.session.cmds.Flow.set_value(search_oid + "/query", self.text())
            self._navigator.goto(search_oid, in_new_view)
            self.nav_oid_bar.nav_oid.hide()
            # self.end_edit()
            # self.set_search_enabled(False)
            return
        self.end_edit()
        self.set_search_enabled(False)
        in_new_view = (
            QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
        )
        self._navigator.goto(oid, in_new_view)

    def reject(self):
        oid = self._navigator._current_oid
        if oid.endswith('/search'):
            return

        self.reset()
        self.end_edit()
        self.set_search_enabled(False)

    def end_edit(self):
        # self.completer.model().beginResetModel()
        self.completer.model().setStringList([])
        # self.completer.model().endResetModel()
        self.hide()
        self.nav_oid_bar.nav_oid.show()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)       
        self.reject()  # if focus lost, hide automatically
    
    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.accept()
        if e.key() == QtCore.Qt.Key_Escape:
            self.reject()
        else:
            self.setProperty('error', False)
            self.setProperty('edited', True)
        self.style().polish(self)
        return super().keyPressEvent(e)


class ProjectSelectionWidget(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(ProjectSelectionWidget, self).__init__(parent)

        icon = resources.get_icon(('icons.search', 'magn-glass'))
        self.nav_mode_icon = QtWidgets.QLabel('')
        self.nav_mode_icon.setPixmap(icon.pixmap(QtCore.QSize(16, 16)))
        self.nav_project_cbb = QtWidgets.QComboBox()
        self.nav_project_cbb.addItems(navigator.session.cmds.Search.list_project_names())
        self.nav_project_cbb.setVisible(self.nav_project_cbb.count() > 1)
        col = QtWidgets.QApplication.instance().palette().button().color().name(QtGui.QColor.HexRgb)
        self.nav_project_cbb.setStyleSheet(f'background-color: {col};')

        lo = QtWidgets.QHBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.addWidget(self.nav_mode_icon)
        lo.addWidget(self.nav_project_cbb)
        self.setLayout(lo)


class NavigationOIDBar(QtWidgets.QWidget):
    def __init__(self, parent, navigator):
        super(NavigationOIDBar, self).__init__(parent)

        self._navigator = navigator
        self._search_enabled = False

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setMinimumHeight(32)
        layout = QtWidgets.QHBoxLayout(self)

        self.nav_oid_field = NavigationOIDField(self, navigator)
        self.nav_oid = NavigationOIDControls(self, navigator)
        self.nav_project_select = ProjectSelectionWidget(self, self._navigator)

        self._select_fx = QtWidgets.QGraphicsOpacityEffect(self.nav_project_select)
        self._select_fx.setOpacity(0.5)
        self.nav_project_select.setGraphicsEffect(self._select_fx)
        
        self.nav_oid_field.hide()
        layout.addWidget(self.nav_oid, 100, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.nav_oid_field, 100, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.nav_project_select, 0, alignment=QtCore.Qt.AlignVCenter)

        layout.setContentsMargins(5, 0, 5, 0)
        self.setLayout(layout)

    def setFocusOnOidField(self):
        self.nav_oid_field.edit()

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self.set_search_enabled(True)
            self.setFocusOnOidField()
        super(NavigationOIDBar, self).mousePressEvent(e)
    
    def search_enabled(self):
        return self._search_enabled
    
    def set_search_enabled(self, b):
        self._search_enabled = b
        self._select_fx.setOpacity(0.5 + 0.5 * float(b))
    
    def selected_project(self):
        return self.nav_project_select.nav_project_cbb.currentText()


class NavigationHistoryControls(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(NavigationHistoryControls, self).__init__(parent)

        self._navigator = navigator

        self.prev_bt = QtWidgets.QPushButton(self)
        self.prev_bt.setFixedSize(QtCore.QSize(36,36))
        self.prev_bt.setIcon(resources.get_icon(
            ('icons.gui', 'nav-arrow-left'),
            disabled_ref=('icons.gui', 'nav-arrow-left-disabled')
        ))
        self.prev_bt.clicked.connect(self._on_prev_bt)

        # self.up_bt = QtWidgets.QPushButton(self)
        # self.up_bt.setProperty('no_border', True)
        # self.up_bt.setProperty('class', ["nav_bt", "up_bt"])
        # self.up_bt.setText('/\\')
        # self.up_bt.setIcon(resources.get_icon(
        #     ('icons.gui', 'chevron-sign-up'),
        #     disabled_ref=('icons.gui', 'chevron-sign-up-disabled')
        # ))
        # self.up_bt.clicked.connect(self._on_up_bt)

        self.next_bt = QtWidgets.QPushButton(self)
        self.next_bt.setFixedSize(QtCore.QSize(36,36))
        self.next_bt.setIcon(resources.get_icon(
            ('icons.gui', 'nav-arrow-right'),
            disabled_ref=('icons.gui', 'nav-arrow-right-disabled')
        ))
        self.next_bt.clicked.connect(self._on_next_bt)

        # self.home_bt = QtWidgets.QPushButton(self)
        # self.home_bt.setProperty('no_border', True)
        # self.home_bt.setProperty('class', ["nav_bt", "home_bt"])
        # self.home_bt.setText('/')
        # self.home_bt.setIcon(resources.get_icon(
        #     ('icons.gui', 'home'),
        #     disabled_ref=('icons.gui', 'home-outline')
        # ))
        # self.home_bt.clicked.connect(self._goto_home)

        self.mytask_bt = QtWidgets.QPushButton(self)
        self.mytask_bt.setFixedSize(QtCore.QSize(36,36))
        self.mytask_bt.setIcon(resources.get_icon(
            ('icons.gui', 'mytasks'),
            disabled_ref=('icons.gui', 'mytasks-disabled')
        ))
        self.mytask_bt.clicked.connect(self._goto_mytasks)

        self.refresh_bt = QtWidgets.QPushButton(self)
        self.refresh_bt.setFixedSize(QtCore.QSize(36,36))
        self.refresh_bt.setIcon(resources.get_icon(
            ('icons.gui', 'nav-arrow-refresh'),
            disabled_ref=('icons.gui', 'nav-arrow-refresh-disabled')
        ))
        self.refresh_bt.clicked.connect(self._refresh)

        bt_lo = QtWidgets.QHBoxLayout()
        bt_lo.setContentsMargins(0, 0, 0, 0)
        bt_lo.setSpacing(0)
        bt_lo.addWidget(self.prev_bt)
        # bt_lo.addWidget(self.up_bt)
        bt_lo.addWidget(self.next_bt)
        # bt_lo.addWidget(self.home_bt)
        bt_lo.addWidget(self.refresh_bt)
        bt_lo.addWidget(self.mytask_bt)

        self.setLayout(bt_lo)

    def _refresh(self):
        self._navigator.refresh()

    def _goto_home(self):
        self._navigator.goto_root()

    def _on_prev_bt(self):
        # TODO: handle optional new view
        self._navigator.goto_prev()

    def _goto_mytasks(self):
        oid = self._navigator._current_oid
        if oid != "/Home":
            project = oid.split("/")[1]
            mytasks_oid = "/%s/mytasks" % project
            self._navigator.goto(mytasks_oid)
        else:
            logging.getLogger('kabaret').log(logging.WARNING, "Cannot open mytasks from /Home ! Implement me")

    def _on_up_bt(self):
        # TODO: handle optional new view
        self._navigator.goto_parent()

    def _on_next_bt(self):
        # TODO: handle optional new view
        self._navigator.goto_next()

    def update_controls(self):
        self.prev_bt.setEnabled(self._navigator.has_prev())
        # self.up_bt.setEnabled(self._navigator.has_parent())
        self.next_bt.setEnabled(self._navigator.has_next())
        # self.home_bt.setEnabled(self._navigator.current_oid is not None and self._navigator.current_oid() != '/Home')
        self.mytask_bt.setEnabled(self._navigator.current_oid is not None and self._navigator.current_oid() != '/Home')


class NavigationBar(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(NavigationBar, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(3)
        self._navigator = navigator
        self.nav_ctrl = NavigationHistoryControls(self, navigator)
        self.nav_oid_bar = NavigationOIDBar(self, navigator)
        layout.addWidget(self.nav_ctrl, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.nav_oid_bar, alignment=QtCore.Qt.AlignVCenter)
        self.setLayout(layout)
        self.setAcceptDrops(True)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

    def dragEnterEvent(self, event):
        source = event.source()
        if source is not None:
            children = self.findChildren(type(source), source.objectName())
            if children and source in children:  # the drop come from one of its children
                return

        if event.mimeData().hasFormat("text/plain"):
            oid = event.mimeData().text()
            try:
                self._navigator.session.cmds.Flow.resolve_path(oid)
            except:
                pass
            else:
                event.acceptProposedAction()

    def dropEvent(self, event):
        oid = event.mimeData().text()
        oid = self._navigator.session.cmds.Flow.resolve_path(oid)
        self._navigator.goto(oid)
        event.acceptProposedAction()
