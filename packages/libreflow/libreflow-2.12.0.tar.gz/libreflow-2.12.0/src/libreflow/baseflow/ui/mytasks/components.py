import pprint
import functools
from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
    QtGui,
)
from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager
from kabaret.app.ui.gui.widgets.popup_menu import PopupMenu
from kabaret.app import resources
from kabaret.app.ui.gui.icons import flow as _

from ....resources.icons import gui as _


class LabelIcon(QtWidgets.QLabel):

    def __init__(self, icon=None, size=None):
        QtWidgets.QLabel.__init__(self, '')
        self.size = size
        if icon:
            self.setIcon(icon)
    
    def setIcon(self, icon):
        icon = QtGui.QIcon(resources.get_icon(icon))
        if self.size: 
            pixmap = icon.pixmap(QtCore.QSize(self.size, self.size))
        else:
            pixmap = icon.pixmap(QtCore.QSize(16, 16))
        self.setPixmap(pixmap)
        self.setAlignment(QtCore.Qt.AlignVCenter)


class WarningFrame(QtWidgets.QWidget):

    # If default task or kitsu entity is not found

    def __init__(self, custom_widget, text):
        super(WarningFrame, self).__init__()
        self.custom_widget = custom_widget

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.frame = QtWidgets.QFrame()
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setStyleSheet('background-color: transparent; border: none;')

        self.asset = QtWidgets.QWidget()
        asset_lo = QtWidgets.QVBoxLayout()
        icon = QtGui.QIcon(resources.get_icon(('icons.gui', 'exclamation-sign')))
        pixmap = icon.pixmap(QtCore.QSize(128, 128))
        self.icon_lbl = QtWidgets.QLabel('')
        self.icon_lbl.setPixmap(pixmap)
        self.label = QtWidgets.QLabel(text)

        asset_lo.addWidget(self.icon_lbl, 0, QtCore.Qt.AlignCenter)
        asset_lo.addWidget(self.label, 1, QtCore.Qt.AlignCenter)
        self.asset.setLayout(asset_lo)
        
        glo = QtWidgets.QGridLayout()
        glo.setContentsMargins(0,0,0,0)
        glo.addWidget(self.frame, 0, 0, 3, 0)
        glo.addWidget(self.asset, 1, 0, QtCore.Qt.AlignCenter)
        self.setLayout(glo)


class TaskStatusCapsule(QtWidgets.QWidget):

    # Show kitsu task status

    def __init__(self, custom_widget):
        super(TaskStatusCapsule, self).__init__()
        self.custom_widget = custom_widget

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.build()
        self.refresh()
    
    def build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(9,0,9,0)

        self.label = QtWidgets.QLabel('')
        lo.addWidget(self.label)

    def refresh(self):
        text = self.custom_widget.data.task_status.get().upper()
        self.label.setText(text)

        color = self.custom_widget.data.task_status_color.get()

        if text == "TODO":
            color = "#3D3F40"

        self.setStyleSheet(
            f'''
            background-color: {color};
            border-radius: {self.sizeHint().height()-6}px;
            color: white;
            font-weight: bold;
            '''
        )


class NavigationSeparator(QtWidgets.QToolButton):

    def __init__(self, related_navigation_button, task_oid):
        super(NavigationSeparator, self).__init__(related_navigation_button)
        self.related_navigation_button = related_navigation_button
        self.task_oid = task_oid

        if task_oid is None:
            self.setEnabled(False)

        self.setText('>')

        self.setStyleSheet('padding: 0;')
    
    def mousePressEvent(self, e):
        if self.task_oid:
            self.related_navigation_button._show_navigables_menu(self.task_oid)
        super(NavigationSeparator, self).mousePressEvent(e)

    def sizeHint(self):
        return QtCore.QSize(18, 24)


class NavigationButton(QtWidgets.QToolButton):

    # Represents an entity in the task oid

    def __init__(self, name, oid, custom_widget):
        super(NavigationButton, self).__init__()
        self.name = name.split(':')[1] if ':' in name else name
        self.oid = oid
        
        self.custom_widget = custom_widget
        self.page_widget = custom_widget.page_widget
        self._last_click_pos = QtCore.QPoint()

        self.setText(self.name)

        if self.oid:
            self.clicked.connect(self._goto)
        else:
            self.setEnabled(False)

        self._menu = PopupMenu(self)

        self.setStyleSheet('padding: 0;')

    def _goto_oid(self, oid):
        self.page_widget.page.goto(oid)

    def _goto(self, b=None):
        self.page_widget.page.goto(self.oid)

    def _show_navigables_menu(self, full_oid):
        self._menu.clear()

        m = self._menu

        m.addAction('Loading...')

        session = self.page_widget.session
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
        if e.button() == QtCore.Qt.RightButton and self.oid:
            self._show_navigables_menu(self.oid)
        else:
            self._last_click_pos = e.pos()
        super(NavigationButton, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._last_click_pos = QtCore.QPoint()
        super(NavigationButton, self).mouseReleaseEvent(e)


class TaskStatusItem(QtWidgets.QWidget):

    # Custom item for FilterStatusComboBox

    def __init__(self, combobox, text, preset=None):
        super().__init__()
        self.combobox = combobox
        self.text = text
        self.preset = preset
        
        self.presetData = []
        self.checked = False

        self.build()

    def build(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        if self.text == '-':
            separator = QtWidgets.QFrame()
            separator.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Plain)
        
            layout.addWidget(separator, QtCore.Qt.AlignVCenter)
            return

        name = QtWidgets.QLabel(self.text)

        self.checkbox = QtWidgets.QToolButton(self)
        self.checkbox.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'check-box-empty'))))
        self.checkbox.setFixedSize(20,20)
        self.checkbox.setIconSize(QtCore.QSize(10,10))
        self.checkbox.clicked.connect(self._on_checkbox_clicked)
        
        layout.addWidget(self.checkbox)
        layout.addWidget(name, QtCore.Qt.AlignVCenter)
        layout.addStretch()

        self.installEventFilter(self)
    
    def setChecked(self, state, disablePreset=None):
        if state:
            self.checked = True
            self.checkbox.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'check'))))
        else:
            self.checked = False
            self.checkbox.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'check-box-empty'))))
        
        if self.preset and disablePreset is None:
            self.combobox.setChecked(self.presetData, self.checked, presetMode=True)
        
        if disablePreset is None:
            self.combobox.checkPreset()
        self.combobox.setTopText()
        
    def _on_checkbox_clicked(self):
        if self.checked:
            self.setChecked(False)
        else:
            self.setChecked(True)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                self._on_checkbox_clicked()
                return True
        
        return False


class FilterStatusComboBox(QtWidgets.QComboBox):

    def __init__(self, *args):
        super(FilterStatusComboBox, self).__init__(*args)
        self.listw = QtWidgets.QListWidget(self)
        self.setModel(self.listw.model())
        self.setView(self.listw)
        self.activated.connect(self.setTopText)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Style
        self.setMinimumWidth(120)
        qss = '''
        QComboBox {
            background-color: palette(dark);
            border: 2px solid palette(button);
            border-radius: 7px;
        }
        QComboBox::drop-down {
            background-color: palette(button);
            border-radius: 4px;
        }
        QListView {
            border: 0px;
        }
        QListView::item:selected {
            background: transparent;
        }
        QListView::item:hover {
            background-color: palette(mid);
        }'''
        self.setStyleSheet(qss)
        self.view().window().setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint)
        self.view().window().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

        # Disable right-click
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        # For save user choices
        self.previousData = []

    def addItem(self, text, preset=None):
        item = QtWidgets.QListWidgetItem(self.listw)
        itemWidget = TaskStatusItem(self, text, preset)
        item.setSizeHint(itemWidget.sizeHint())
        self.listw.addItem(item)
        self.listw.setItemWidget(item, itemWidget)
        self.setTopText()
    
    def addItems(self, texts):
        for text in texts:
            exist = False
            for i in range(self.listw.count()):
                item = self.listw.item(i)
                widget = self.listw.itemWidget(item)
                if widget.text == text:
                    exist = True
                    break
            if not exist:
                self.addItem(text)

    def setDefaultPreset(self):
        preset = []
        defaultPresetItem = None
        for i in range(self.listw.count()):
            item = self.listw.item(i)
            widget = self.listw.itemWidget(item)
            if widget.preset and widget.text == 'Default':
                defaultPresetItem = widget
                continue
            if widget.preset or widget.text == 'DONE' or widget.text == '-':
                continue
            preset.append(widget.text)

        defaultPresetItem.presetData = preset
        return preset

    def setChecked(self, texts, state, presetMode=None):
        for i, text in enumerate(texts):
            for i in range(self.listw.count()):
                item = self.listw.item(i)
                widget = self.listw.itemWidget(item)
                if widget.text == text:
                    widget.setChecked(True if state else False)
                if presetMode:
                    if not widget.preset and widget.text not in texts:
                        if widget.checked:
                            widget.setChecked(False)

    def setTopText(self):
        list_text = self.fetchNames()
        text = ", ".join(list_text)
        
        metrics = QtGui.QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, QtCore.Qt.ElideRight, self.lineEdit().width())
        if '…' in elidedText:
            elidedText = 'Status (' + str(len(list_text)) + ')'
        self.setEditText(elidedText)

    def checkPreset(self):
        currentData = self.fetchNames()
        for i in range(self.listw.count()):
            item = self.listw.item(i)
            widget = self.listw.itemWidget(item)
            if widget.preset:
                if widget.presetData == currentData:
                    widget.setChecked(True, disablePreset=True)
                else:
                    widget.setChecked(False, disablePreset=True)

    def fetchNames(self):
        return [
            self.listw.itemWidget(self.listw.item(i)).text
            for i in range(self.listw.count())
            if self.listw.itemWidget(self.listw.item(i)).preset is None
            if self.listw.itemWidget(self.listw.item(i)).checked
        ]

    def fetchItems(self):
        return [
            self.listw.itemWidget(self.listw.item(i))
            for i in range(self.listw.count())
            if self.listw.itemWidget(self.listw.item(i)).preset is None
            if self.listw.itemWidget(self.listw.item(i)).checked
        ]

    def count(self):
        return len([
            self.listw.itemWidget(self.listw.item(i))
            for i in range(self.listw.count())
            if self.listw.itemWidget(self.listw.item(i)).preset is None
        ])

    # Methods for make combobox less buggy
    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if (
                event.type() == QtCore.QEvent.MouseButtonRelease
                and event.button() == QtCore.Qt.LeftButton
            ):
                self.hidePopup() if self.closeOnLineEditClick else self.showPopup()
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
        # Refresh the display text when closing
        self.setTopText()
        # Check if there are any changes
        newRes = self.fetchNames()
        if self.previousData != newRes:
            self.previousData = newRes
            self.parent().page_widget.update_presets(filter_data=self.previousData)

            self.parent().page_widget.content.list.refresh(True)

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False


class MyTasksSearch(QtWidgets.QLineEdit):

    def __init__(self, overlay):
        super(MyTasksSearch, self).__init__()
        self.overlay = overlay
        self.page_widget = overlay.page_widget

        self.setStyleSheet('''
        QLineEdit {
            background-color: palette(dark);
            border: 2px solid palette(button);
            border-radius: 7px;
            padding-left: 30px;
        }''')

        self.setMaximumWidth(36)
        self.setMaximumHeight(32)

        self.build()

    def build(self):
        self.search_icon = LabelIcon(('icons.search', 'magn-glass'), 18)

        lo = QtWidgets.QHBoxLayout(self)
        lo.setContentsMargins(9,0,0,0)
        lo.addWidget(self.search_icon, 0, QtCore.Qt.AlignLeft)

        self.setClearButtonEnabled(True)

        self.anim = QtCore.QPropertyAnimation(self, b'maximumWidth')
        self.anim.setEasingCurve(QtCore.QEasingCurve.OutQuint)
        self.anim.setDuration(400)
    
    def focusInEvent(self, event):
        if self.text() == '':
            self.anim.setStartValue(36)
            self.anim.setEndValue(225 if self.page_widget.content.header.update_label.isVisible() is False else 240)
            self.anim.start()
            self.overlay.settingMask()
            self.page_widget.content.header.toggle_filter(True)
        
        super(MyTasksSearch, self).focusInEvent(event)

    def focusOutEvent(self, event):
        if self.text() == '':
            self.setText('')
            self.anim.setStartValue(225 if self.page_widget.content.header.update_label.isVisible() is False else 240)
            self.anim.setEndValue(36)
            self.anim.finished.connect(self.overlay.settingMask)
            self.anim.start()
            self.page_widget.content.header.toggle_filter(False)

        super(MyTasksSearch, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Escape) or (event.key() == QtCore.Qt.Key_Return):
            self.clearFocus()
        else:
            super(MyTasksSearch, self).keyPressEvent(event)
