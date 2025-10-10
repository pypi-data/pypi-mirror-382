import six
import time
import timeago
from datetime import datetime

from pprint import pprint

from kabaret import flow
from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui, CustomPageWidget
from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager
from kabaret.app import resources
from kabaret.app.ui.gui.icons import flow as _

from .mytasks.components import LabelIcon


def get_icon_ref(icon_name, resource_folder='icons.flow'):
    if isinstance(icon_name, six.string_types):
        icon_ref = (resource_folder, icon_name)
    else:
        icon_ref = icon_name

    return icon_ref


class JobQueueFooter(QtWidgets.QWidget):
    def __init__(self, page_widget):
        super(JobQueueFooter,self).__init__(page_widget)
        self.page_widget = page_widget
        self.list = page_widget.content.listbox.list
        self.build()
        self.refresh()

    def build(self):
        self.stats_label = QtWidgets.QLabel()
        self.loading_label = QtWidgets.QLabel()
        self.last_auto_sync_label = QtWidgets.QLabel()
        self.last_manual_sync_label = QtWidgets.QLabel()

        self.loading_label.setText('Loading queue...')
        self.loading_label.hide()

        flo = QtWidgets.QGridLayout()
        flo.addWidget(self.stats_label, 0, 0)
        flo.addWidget(self.loading_label, 1, 0)
        flo.addWidget(self.last_auto_sync_label, 0, 1, alignment=QtCore.Qt.AlignRight)
        flo.addWidget(self.last_manual_sync_label, 1, 1, alignment=QtCore.Qt.AlignRight)

        self.setLayout(flo)

    def refresh(self):
        all_count = self.page_widget.get_jobs_count()
        loaded_count = self.list.count_jobs()
        all_count = f'{all_count} jobs in queue ({loaded_count} loaded)'

        processed_count = self.page_widget.get_jobs_count(status="PROCESSED")
        processed_count = f'<font color="#61f791">{processed_count} PROCESSED</font>'

        error_count = self.page_widget.get_jobs_count(status="ERROR")
        error_count = f'<font color="#ff5842">{error_count} ERROR</font>'

        waiting_count = self.page_widget.get_jobs_count(status="WAITING")
        waiting_count = f'<font color="#EFDD5B">{waiting_count} WAITING</font>'

        last_auto_sync = self.page_widget.session.cmds.Flow.get_value(
            self.page_widget.oid + "/last_auto_sync"
        )
        if last_auto_sync is not None :
            date = datetime.fromtimestamp(last_auto_sync)
            full_date = date.strftime('%Y-%m-%d %H:%M:%S')
            nice_date = timeago.format(full_date, datetime.now())
            self.last_auto_sync_label.setText(f'Last auto sync: {full_date} ({nice_date})')

        last_manual_sync = self.page_widget.session.cmds.Flow.get_value(
            self.page_widget.oid + "/last_manual_sync"
        )
        if last_manual_sync is not None :
            date = datetime.fromtimestamp(last_manual_sync)
            full_date = date.strftime('%Y-%m-%d %H:%M:%S')
            nice_date = timeago.format(full_date, datetime.now())
            self.last_manual_sync_label.setText(f'Last manual sync: {full_date} ({nice_date})')

        if all_count == "0 Jobs in queue" :
            self.stats_label.setText("No jobs in queue")
        else:
            self.stats_label.setText(f'{all_count} / {processed_count} - {waiting_count} - {error_count}')


class FilterItem(QtWidgets.QWidget):

    # Custom item for FilterComboBox

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


class FilterComboBox(QtWidgets.QComboBox):

    def __init__(self, page_widget, top_text):
        super(FilterComboBox, self).__init__(page_widget)
        self.page_widget = page_widget
        self.top_text = top_text

        self.listw = QtWidgets.QListWidget(self)
        self.setModel(self.listw.model())
        self.setView(self.listw)
        self.activated.connect(self.setTopText)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Style
        self.setMinimumWidth(130)
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
        itemWidget = FilterItem(self, text, preset)
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
            if widget.preset and widget.text == 'ALL':
                defaultPresetItem = widget
                continue
            if widget.preset or widget.text == 'ALL' or widget.text == '-':
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
            elidedText = f'{self.top_text} ({str(len(list_text))})'
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
        if self.previousData != newRes or newRes == []:
            # Reset preset if nothing is selected
            if newRes == []:
                self.setChecked(['ALL'], True)
                newRes = self.fetchNames()

            self.previousData = newRes

            if self.top_text == "Type":
                self.page_widget.update_presets(job_types=self.previousData)
            elif self.top_text == "Status":
                self.page_widget.update_presets(job_status=self.previousData)
            self.page_widget.content.listbox.list.refresh()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False


class JobQueueSearch(QtWidgets.QLineEdit):

    def __init__(self, overlay):
        super(JobQueueSearch, self).__init__()
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
            self.anim.setEndValue(250)
            self.anim.start()
            self.overlay.settingMask()
            self.page_widget.content.header.toggle_filter(True)
        
        super(JobQueueSearch, self).focusInEvent(event)

    def focusOutEvent(self, event):
        if self.text() == '':
            self.setText('')
            self.anim.setStartValue(250)
            self.anim.setEndValue(36)
            self.anim.finished.connect(self.overlay.settingMask)
            self.anim.start()
            self.page_widget.content.header.toggle_filter(False)

        super(JobQueueSearch, self).focusOutEvent(event)

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Escape) or (event.key() == QtCore.Qt.Key_Return):
            self.clearFocus()
        else:
            super(JobQueueSearch, self).keyPressEvent(event)


class JobQueueSearchOverlay(QtWidgets.QWidget):

    # Search is overlay on top of filter widgets

    def __init__(self, page_widget):
        super(JobQueueSearchOverlay, self).__init__(page_widget)
        self.page_widget = page_widget

        self.build()

    def build(self):
        hlo = QtWidgets.QHBoxLayout(self)

        self.search = JobQueueSearch(self)
        hlo.addWidget(self.search)
        hlo.addStretch()

        self.region = QtGui.QRegion(self.search.frameGeometry())
        self.region.translate(9, 0)
        self.setMask(self.region)

    def settingMask(self):
        self.region = QtCore.QRect(9, 0, self.search.anim.endValue(), 480)
        self.setMask(self.region)
        if self.search.anim.isSignalConnected(
            QtCore.QMetaMethod.fromSignal(self.search.anim.finished)
        ):
            self.search.anim.finished.disconnect()


class JobQueueHeader(QtWidgets.QWidget):

    def __init__(self, content_widget):
        super(JobQueueHeader,self).__init__(content_widget)
        self.content_widget = content_widget
        self.page_widget = self.content_widget.page_widget

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)

        self.opacity_anim = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setEasingCurve(QtCore.QEasingCurve.OutQuint)

        self.setStyleSheet('''
        QPushButton {
            background-color: palette(dark);
            border: 2px solid palette(button);
            border-radius: 7px;
        }
        ''')

        self.build()

    def build(self):
        self.filter_group = QtWidgets.QWidget()
        self.filter_lo = QtWidgets.QHBoxLayout(self.filter_group)
        self.filter_lo.setContentsMargins(42, 0, 0, 0)
        self.filter_group.setGraphicsEffect(self.opacity_effect)

        self.filter_label = QtWidgets.QLabel('Filter by:')
        self.filter_lo.addWidget(self.filter_label)

        self.filter_type_combobox = FilterComboBox(self.page_widget, "Type")
        self.filter_type_combobox.addItem('ALL', preset=True)
        self.filter_type_combobox.addItem('-')
        self.filter_type_combobox.addItems(['Download', 'Upload'])
        self.filter_type_combobox.setDefaultPreset()
        filter_value = self.page_widget.get_job_types_filter()
        if filter_value == [] or filter_value is None:
            self.filter_type_combobox.setChecked(['ALL'], True)
        else:
            for job_type in filter_value:
                self.filter_type_combobox.setChecked([job_type], True)
        self.filter_type_combobox.previousData = self.filter_type_combobox.fetchNames()
        self.page_widget.update_presets(job_types=self.filter_type_combobox.previousData)

        self.filter_lo.addWidget(self.filter_type_combobox)

        self.filter_status_combobox = FilterComboBox(self.page_widget, "Status")
        self.filter_status_combobox.addItem('ALL', preset=True)
        self.filter_status_combobox.addItem('-')
        self.filter_status_combobox.addItems(['PROCESSING','PROCESSED', 'WAITING', 'ERROR', 'PAUSE', 'WFA'])
        self.filter_status_combobox.setDefaultPreset()
        filter_value = self.page_widget.get_job_status_filter()
        if filter_value == [] or filter_value is None:
            self.filter_status_combobox.setChecked(['ALL'], True)
        else:
            for status in filter_value:
                self.filter_status_combobox.setChecked([status], True)
        self.filter_status_combobox.previousData = self.filter_status_combobox.fetchNames()
        self.page_widget.update_presets(job_status=self.filter_status_combobox.previousData)

        self.filter_lo.addWidget(self.filter_status_combobox)

        self.filter_user_combobox = FilterComboBox(self.page_widget, "User")

        self.filter_lo.addWidget(self.filter_user_combobox)

        self.clear_button = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.libreflow', 'clean'))), '')
        self.clear_button.clicked.connect(self._on_clear_button_clicked)
        self.clear_button.setIconSize(QtCore.QSize(20,20))
        self.clear_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.clear_button.setToolTip("Clear queue")

        self.removejobs_button = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.libreflow', 'waiting'))), '')
        self.removejobs_button.clicked.connect(self._on_removejobs_button_clicked)
        self.removejobs_button.setIconSize(QtCore.QSize(20,20))
        self.removejobs_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.removejobs_button.setToolTip("Remove outdated jobs")

        self.resetjobs_button = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.libreflow', 'refresh'))), '')
        self.resetjobs_button.clicked.connect(self._on_resetjobs_button_clicked)
        self.resetjobs_button.setIconSize(QtCore.QSize(20,20))
        self.resetjobs_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.resetjobs_button.setToolTip("Reset erroneous jobs")

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.filter_group)
        hlo.addStretch()
        hlo.addWidget(self.clear_button)
        hlo.addWidget(self.resetjobs_button)
        hlo.addWidget(self.removejobs_button)

        self.setLayout(hlo)

    def toggle_filter(self, hidden):
        # Used for MyTasksSearch focus animation
        if hidden:
            self.opacity_anim.setStartValue(1.0)
            self.opacity_anim.setEndValue(0.0)
        else:
            self.opacity_anim.setStartValue(0.0)
            self.opacity_anim.setEndValue(1.0)
            
        self.opacity_anim.start()

    def set_users(self, users):
        self.filter_user_combobox.addItem('ALL', preset=True)
        self.filter_user_combobox.addItem('-')
        self.filter_user_combobox.addItems(users)
        self.filter_user_combobox.setDefaultPreset()
        self.filter_user_combobox.setChecked(['ALL'], True)

    def _on_clear_button_clicked(self):
        self.page_widget.page.show_action_dialog(
                f"{self.page_widget.oid}/job_list/clear_queue"
            )

    def _on_removejobs_button_clicked(self):
        self.page_widget.page.show_action_dialog(
                f"{self.page_widget.oid}/job_list/remove_outdated_jobs"
            )
        self.page_widget.content.listbox.list.refresh()

    def _on_resetjobs_button_clicked(self):
        self.page_widget.page.show_action_dialog(
                f"{self.page_widget.oid}/job_list/reset_jobs"
            )
        self.page_widget.content.listbox.list.refresh()


class JobStatusDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        data = index.data(QtCore.Qt.DisplayRole)
        orig_brush = painter.brush()
        orig_pen = painter.pen()

        painter.setBrush(orig_brush)
        painter.setPen(orig_pen)

        # Base rectangle
        painter.save()
        painter.setBrush(QtGui.QColor(75, 75, 75))  # Background base color
        if data == "PROCESSED":
            painter.setBrush(QtGui.QColor(108, 211, 150))
        elif data == "PROCESSING":
            painter.setBrush(QtGui.QColor(65, 123, 216))
        painter.setPen(QtGui.QColor("transparent"))
        rounded_rect = QtCore.QRect(
            option.rect.x() + 5,
            option.rect.y() + 3.75,
            option.rect.width() - 10,
            option.rect.height() - 7,
        )
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawRoundedRect(rounded_rect, 10, 10)

        # Text value
        painter.setPen(QtGui.QColor(QtCore.Qt.white))
        if data == "ERROR":
            painter.setPen(QtGui.QColor(255, 88, 66))
        elif data == "WAITING":
            painter.setPen(QtGui.QColor(239, 221, 91))
        font = QtGui.QFont()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rounded_rect, QtCore.Qt.AlignCenter, data)
        painter.restore()


class JobQueueModel(QtCore.QAbstractTableModel):

    def __init__(self, table, parent=None):
        super(JobQueueModel, self).__init__(parent)
        self.table = table

    def rowCount(self, parent=None):
        return len(self.table.jobs_data)

    def columnCount(self, parent=None):
        return 6

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.table.header_labels[section]

        return super().headerData(section, orientation, role)

    def data(self, index, role):
        data = self.table.jobs_data[index.row()]
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return QtGui.QIcon(resources.get_icon(('icons.libreflow', data['type'].lower())))

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                if role == QtCore.Qt.EditRole:
                    return data['emitter_oid']
                elif role == QtCore.Qt.DisplayRole:
                    split = data["emitter_oid"].split('/')
                    indices = list(range(len(split) - 4, 2, -2))
                    indices[:0] = [len(split)-1]
                    source_display = ' – '.join([split[i] for i in reversed(indices)])
                    return source_display

            elif index.column() == 1:
                return data['status']

            elif index.column() == 2:
                if role == QtCore.Qt.EditRole:
                    return data['file_size'] if data.get('file_size', None) else 0
                elif role == QtCore.Qt.DisplayRole:
                    if data.get('file_size', None):
                        locale = QtCore.QLocale()
                        display_size = locale.formattedDataSize(
                            data["file_size"],
                            format=locale.DataSizeFormat.DataSizeTraditionalFormat,
                        )
                        return display_size
                    else:
                        return ""

            elif index.column() == 3:
                return QtCore.QDateTime.fromSecsSinceEpoch(int(data['date']))

            elif index.column() == 4:
                return data["requested_by_user"]

            elif index.column() == 5:
                return data["requested_by_studio"]

        if role == QtCore.Qt.UserRole:
            return data["name"]

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class JobQueueProxyModel(QtCore.QSortFilterProxyModel):

    # Handle Int64 values in sorting
    def lessThan(self, left, right):
        leftData = left.data(role=QtCore.Qt.EditRole)
        rightData = right.data(role=QtCore.Qt.EditRole)

        if left.column() == 2:
            return leftData < rightData

        return super(JobQueueProxyModel, self).lessThan(left, right)


class JobQueueListView(QtWidgets.QTableView):

    def __init__(self, box_widget):
        super(JobQueueListView, self).__init__(box_widget)
        self.box_widget = box_widget
        self.content_widget = self.box_widget.content_widget
        self.page_widget = self.content_widget.page_widget

        self.setStyleSheet('''QTableView {
                                background-color: transparent;
                                border: none;
                            }
                            QTableView::item {
                                padding: 4px;
                            }
                            QHeaderView {
                                background-color: transparent;
                                border-top: none;
                                border-left: none;
                                border-right: none;
                                border-color: palette(button)
                            }
                            QHeaderView::section {
                                background-color: transparent; 
                                border-color: palette(button)
                            }'''
                            )

        self.header_labels = ['Name', 'Status', 'Size', 'Emitted On', 'User', 'Site']

        self.model = JobQueueModel(self)
        self.proxy_model = JobQueueProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setSortRole(QtCore.Qt.EditRole)
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.setFilterKeyColumn(-1)
        self.setModel(self.proxy_model)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        self.refresh()

        self.verticalHeader().hide()
        self.setShowGrid(False)

        self.setItemDelegateForColumn(1, JobStatusDelegate())

        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignVCenter)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.setSortingEnabled(True)

        # Iterate through the first column to find the widest item
        widestWidthColumn0 = 0
        for row in range(0, self.model.rowCount()):
            text = str(self.model.data(self.model.index(row, 0), role=QtCore.Qt.DisplayRole))
            fm = QtGui.QFontMetrics(self.font())
            width = fm.boundingRect(text).width()
            widestWidthColumn0 = max(widestWidthColumn0, width)

        self.setColumnWidth(0, widestWidthColumn0 + 40)
        self.setColumnWidth(3, self.columnWidth(3) + 30)
        self.setColumnWidth(4, self.columnWidth(4) + 20)

        self.sortByColumn(3, QtCore.Qt.DescendingOrder)

        self.action_manager = ObjectActionMenuManager(
            self.page_widget.session, self.page_widget.page.show_action_dialog, 'Flow.map'
        )

        self.doubleClicked.connect(self._on_item_doubleClicked)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

    def count_jobs(self, filter_status=None):
        if not filter_status:
            return len(self.jobs_data)

        return len([data for data in self.jobs_data if data["status"] == filter_status])

    def refresh(self):
        if hasattr(self.page_widget, "footer"):
            self.page_widget.footer.loading_label.show()
            if self.page_widget.isVisible():
                QtWidgets.QApplication.processEvents()

        self.user_filter = self.content_widget.header.filter_user_combobox.fetchNames()

        self.proxy_model.beginResetModel()
        self.jobs_data = self.page_widget.get_jobs(
            type=self.page_widget.get_job_types_filter(),
            status=self.page_widget.get_job_status_filter(),
            user=(None if self.user_filter == [] else self.user_filter)
        )
        self.proxy_model.endResetModel()

        if hasattr(self.page_widget, "footer"):
            self.page_widget.footer.refresh()
            self.page_widget.footer.loading_label.hide()

    def refresh_search(self, query_filter):
        keywords = query_filter.split()
        query_filter = '.*'+'.*'.join(keywords)

        reg_exp = QtCore.QRegularExpression(
            query_filter,
            options=QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption,
        )
        self.proxy_model.setFilterRegularExpression(reg_exp)

    def _on_item_doubleClicked(self, item):
        self.page_widget.page.goto(
            f"{self.page_widget.oid}/job_list/{item.data(role=QtCore.Qt.UserRole)}"
        )

    def _on_context_menu_requested(self, pos):
        action_menu = QtWidgets.QMenu(self)
        index = self.indexAt(pos)

        if not index.isValid():
            return

        item_oid = f"{self.page_widget.oid}/job_list/{index.data(role=QtCore.Qt.UserRole)}"

        has_actions = self.action_manager.update_oid_menu(
            item_oid, action_menu, with_submenus=True
        )

        if has_actions:
            action_menu.exec_(self.viewport().mapToGlobal(pos))


class JobQueueListBox(QtWidgets.QWidget):
    def __init__(self, content_widget):
        super(JobQueueListBox, self).__init__(content_widget)
        self.setObjectName('JobQueueListBox')
        self.content_widget = content_widget
        self.page_widget = self.content_widget.page_widget

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('#JobQueueListBox { background-color: palette(window); border-radius: 5px; }')

        self.build()

    def build(self):
        box = QtWidgets.QVBoxLayout(self)
        self.list = JobQueueListView(self)
        box.addWidget(self.list)


class JobQueueContent(QtWidgets.QWidget):
    def __init__(self, page_widget):
        super(JobQueueContent, self).__init__(page_widget)
        self.setObjectName('JobQueueContent')
        self.page_widget = page_widget

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('#JobQueueContent { background-color: palette(dark); border-radius: 5px; }')

        self.build()

    def build(self):
        grid = QtWidgets.QGridLayout(self)

        self.overlay = JobQueueSearchOverlay(self.page_widget)
        self.header = JobQueueHeader(self)
        self.listbox = JobQueueListBox(self)
        self.overlay.search.textChanged.connect(self.listbox.list.refresh_search)
        self.header.set_users(self.page_widget.get_users())
        grid.addWidget(self.header, 0, 0)
        grid.addWidget(self.overlay, 0, 0, 1, 1)
        grid.addWidget(self.listbox, 1, 0)


class JobQueueWidget(CustomPageWidget):

    def build(self):
        self.store_delay = time.time()
        self.setStyleSheet('outline: 0;')

        self.content = JobQueueContent(self)
        self.footer = JobQueueFooter(self)

        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(0,0,0,0)
        vlo.setSpacing(1)
        vlo.addWidget(self.content)
        vlo.addWidget(self.footer)

    def get_jobs(self, type=None, status=None, user=None):
        return self.session.cmds.Flow.call(
            f"{self.oid}/job_list", "jobs", args=[True, type, status, user], kwargs={}
        )

    def get_jobs_count(self, type=None, status=None):
        return self.session.cmds.Flow.call(
            f"{self.oid}/job_list", "count", args=[type, status], kwargs={}
        )

    def get_users(self):
        return self.session.cmds.Flow.call(
            f"{self.oid}/job_list", "list_users", args=[], kwargs={}
        )

    def get_job_types_filter(self):
        return self.session.cmds.Flow.get_value(f"{self.oid}/job_types_filter")

    def get_job_status_filter(self):
        return self.session.cmds.Flow.get_value(f"{self.oid}/job_status_filter")

    def update_presets(self, job_types=None, job_status=None):
        if job_types:
            self.session.cmds.Flow.set_value(f"{self.oid}/job_types_filter", job_types)
        if job_status:
            self.session.cmds.Flow.set_value(f"{self.oid}/job_status_filter", job_status)

        return self.session.cmds.Flow.call(
            f"{self.oid}", "update_presets", args=[], kwargs={}
        )

    def on_touch_event(self, oid):
        # Quick and dirty fix to avoid too many events at the same time
        # Accept event if the last one was more than ten seconds ago
        self.delay = time.time() - self.store_delay
        if self.delay > 10:
            self.content.listbox.list.refresh()
            self.store_delay = time.time()
