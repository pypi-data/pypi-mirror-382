import os
import re
import datetime
import pprint
import time
import webbrowser
from traceback import print_exc
from kabaret.app.ui.gui.widgets.flow.flow_view import (
    CustomPageWidget,
    QtWidgets,
    QtCore,
    QtGui,
)
from kabaret.app import resources
from kabaret.app.ui.gui.icons import flow as _

from ....resources.icons import gui as _

from .file_list import TaskFileList
from .components import (
    FilterStatusComboBox,
    MyTasksSearch,
    NavigationButton,
    NavigationSeparator,
    TaskStatusCapsule,
    WarningFrame
)
from .edit_dialog import EditStatusDialog
from ..controller import ActionData, FileData


class PopUpDialog(QtWidgets.QFrame):

    # Display a message during the loading process

    def __init__(self, content_widget):
        QtWidgets.QFrame.__init__(self)
        self.setObjectName('PopUpDialog')
        self.content_widget = content_widget

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

        if self.content_widget.list.get_count() > 0:
            self.hide()
        
        self.build()

    def build(self):
        self.container_lo = QtWidgets.QVBoxLayout(self)
       
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setWeight(QtGui.QFont.Bold)

        self.message_widget = QtWidgets.QFrame()
        self.message_widget.setObjectName('PopUpMessage')
        self.message_widget.setFixedWidth(200)

        self.message_lo = QtWidgets.QVBoxLayout(self.message_widget)
        self.message_lo.setContentsMargins(20,20,20,20)
        self.message_lo.setSpacing(10)

        self.main_label = QtWidgets.QLabel('Updating list')
        self.main_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_label.setFont(font)
        
        self.description_label = QtWidgets.QLabel('Please wait...')
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)

        self.message_lo.addWidget(self.main_label)
        self.message_lo.addWidget(self.description_label)

        self.container_lo.addWidget(self.message_widget, alignment=QtCore.Qt.AlignCenter)

    def refresh(self, main_text, desc_text):
        self.main_label.setText(main_text)
        self.description_label.setText(desc_text)


class MyTasksFooter(QtWidgets.QWidget):

    # Tasks count and tell the user how to display entity description

    def __init__(self, page_widget):
        super(MyTasksFooter, self).__init__(page_widget)
        self.page_widget = page_widget
        self.build()

    def build(self):
        self.left_text = QtWidgets.QLabel()
        self.left_text.setText(str(self.page_widget.content.list.get_count())+' Tasks')
        self.shift_label = QtWidgets.QLabel('Press SHIFT to display entity description')

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.left_text)
        hlo.addStretch()
        hlo.addWidget(self.shift_label)
        hlo.setContentsMargins(0,10,0,5)
        self.setLayout(hlo)

    def refresh_count(self):
        self.left_text.setText(str(self.page_widget.content.list.get_count())+' Tasks')


class RunnerSignals(QtCore.QObject):
    
    # Signals for QRunnable must be outside the class.

    progress = QtCore.Signal(object, str)


class KitsuCommentsRunner(QtCore.QRunnable):
    
    # Builds the HTML for kitsu comments of a task

    def __init__(self, task_widget):
        super(KitsuCommentsRunner, self).__init__()
        self.task_widget = task_widget
        self.signals = RunnerSignals()

    def run(self):
        comment_html = '''
        <style>
            a:link {
                color: #00BFFF;
                background-color: transparent;
                text-decoration: none;
            }
            .separator {
                border-bottom: 1px solid white;
                border-collapse: collapse;
            }
            .spacer {
                margin-bottom: 10px;
            }
        </style>
        '''

        for i, c in enumerate(self.task_widget.data.task_comments.get()):
            date_object = datetime.datetime.strptime(c['created_at'], "%Y-%m-%dT%H:%M:%S")

            comment_html = comment_html + '''
            <table cellspacing=0 width=100%>
            <tr>
                <td><span style='color: {color}; font-weight: bold;'>{status}</span> - {name}</td>
                <td align=right>{date}</td>
            </tr>
            </table>
            '''.format(
                color=c['task_status']['color'],
                status=c['task_status']['short_name'].upper(),
                name=c['person']['first_name'] + ' ' + c['person']['last_name'],
                date=date_object.strftime('%d/%m'),
            )

            if c['text'] != '':
                if '\n' in c['text']:
                    comment_lines = c['text'].split('\n')
                    for line in comment_lines:
                        comment_html = comment_html + '''<p>{text}</p>'''.format(text=line)
                else:
                    comment_html = comment_html + '''<p>{text}</p>'''.format(text=c['text'])

            if c['previews'] != []:
                revision_link = self.task_widget.create_revision_link(self.task_widget.data.entity_type.get(), c['previews'][0]['id'])
                comment_html = comment_html + '''<p><a href='{link}'>Revision</a></p>'''.format(link=revision_link)
            
            if i == len(self.task_widget.data.task_comments.get())-1:
                continue
            comment_html = comment_html + '''<table cellspacing=0 class="spacer" width=100%><tr><td class="separator"/></tr></table>'''

        self.signals.progress.emit(self.task_widget, comment_html)


class FileDataRunner(QtCore.QRunnable):
    
    # Create primary files data for TaskFileList model

    def __init__(self, task_widget):
        super(FileDataRunner, self).__init__()
        self.task_widget = task_widget
        self.signals = RunnerSignals()

    def run(self):
        if self.task_widget.data.primary_files.get():
            self.task_widget.create_file_data(self.task_widget.data.primary_files.get())
        self.signals.progress.emit(self.task_widget, '')


class TaskBorderDelegate(QtWidgets.QStyledItemDelegate):
    """
    Defines a delegate responsible for display a row line
    when user can resize a task
    """

    def __init__(self, parent=None):
        super(TaskBorderDelegate, self).__init__(parent)
    
    def paint(self, painter, option, index):
        widget = option.widget.indexWidget(index)

        if widget.expanded:
            # Set color
            painter.setPen(QtGui.QColor('#757575'))
            
            # Set coordinates
            bottomLeft = option.rect.bottomLeft()
            bottomLeft.setX(100)

            bottomRight = option.rect.bottomRight()
            bottomRight.setX(option.rect.bottomRight().x()-100)

            # Draw line
            painter.drawLine(bottomLeft, bottomRight)


class TaskItem(QtWidgets.QWidget):

    def __init__(self, tasks_list, data, row):
        super(TaskItem, self).__init__()
        self.setObjectName('TaskItem')
        self.tasks_list = tasks_list
        self.page_widget = tasks_list.page_widget
        self.data = data
        self.row_index = row

        # self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('''
        #LeftWidget, #RightWidget {
            background-color: palette(window);
            border: 2px solid palette(button);
            border-radius: 10px;
        }
        ''')

        self.file_data = []
        self.file_actions = []

        self.file_data_thread = None
        self.comments_thread = None
        
        self.expanded = False
        self.kitsu_description = False
        self.kitsu_not_found = False
        self.entity_exists = True

        self.build()
        self.data_init()

        self.setMouseTracking(True)

        # Thread setup for store task expand state
        self.expand_thread = QtCore.QThread()
        
        self.expand_worker = ExpandStateWorker(self)
        self.expand_worker.moveToThread(self.expand_thread)

        self.expand_thread.started.connect(self.expand_worker.run)
        self.expand_worker.finished.connect(self.expand_thread.quit)

    def build(self):
        container = QtWidgets.QHBoxLayout(self)
        container.setContentsMargins(5,15,5,15)
        container.setSpacing(0)

        self.build_left_widget()
        self.build_right_widget()

        container.addWidget(self.left_widget)
        container.addWidget(self.right_kitsu)

    # For libreflow data
    def build_left_widget(self):
        self.left_widget = QtWidgets.QWidget()
        self.left_widget.setObjectName('LeftWidget')
        self.left_widget.installEventFilter(self)
        self.left_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        left_lo = QtWidgets.QVBoxLayout(self.left_widget)
        left_lo.setContentsMargins(0,0,0,0)
        left_lo.setSpacing(0)

        # Header
        self.left_header = QtWidgets.QWidget()
        self.left_header.setFixedHeight(36)
        left_lo.addWidget(self.left_header)
        
        self.left_header_lo = QtWidgets.QHBoxLayout(self.left_header)
        self.left_header_lo.setContentsMargins(7,0,7,0)
        self.left_header_lo.setSpacing(0)

        self.expand_button = QtWidgets.QToolButton()
        self.expand_button.setFixedSize(20, 20)
        self.expand_button.setIconSize(QtCore.QSize(10, 10))
        self.expand_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.expand_button.clicked.connect(self._on_expand_button_clicked)
        self.left_header_lo.addWidget(self.expand_button)
        self.left_header_lo.addSpacing(5)

        line = QtWidgets.QFrame()
        line.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Plain)
        line.setLineWidth(2)
        line.setStyleSheet('color: #504f4f;')
        self.left_header_lo.addWidget(line)

        self.oid_lo = QtWidgets.QHBoxLayout()
        self.oid_lo.setContentsMargins(0,0,0,0)
        self.oid_lo.setSpacing(0)
        self.left_header_lo.addLayout(self.oid_lo)

        self.bookmark_button = QtWidgets.QToolButton()
        self.bookmark_button.setFixedSize(22, 22)
        self.bookmark_button.setIconSize(QtCore.QSize(14, 14))
        self.bookmark_button.setIcon(resources.get_icon(('icons.gui', 'star')))
        self.bookmark_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.bookmark_button.clicked.connect(self._on_bookmark_button_clicked)
        self.bookmark_button.hide()

        # Horizontal separator
        hline = QtWidgets.QFrame()
        hline.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Plain)
        hline.setLineWidth(2)
        hline.setStyleSheet('color: #504f4f;')

        left_lo.addWidget(hline)

        # File List
        self.task_warning = WarningFrame(self, f'Could not find Libreflow entity')
        if self.data.dft_task_name.get() is None:
            left_lo.addWidget(self.task_warning)
        else:
            self.files_list = TaskFileList(self)
            left_lo.addWidget(self.files_list)

    # For Kitsu data
    def build_right_widget(self):
        self.right_kitsu = QtWidgets.QWidget()
        self.right_kitsu.installEventFilter(self)
        self.right_kitsu.setObjectName('RightWidget')
        self.kitsu_lo = QtWidgets.QVBoxLayout(self.right_kitsu)
        self.kitsu_lo.setContentsMargins(0,0,0,0)
        self.kitsu_lo.setSpacing(0)

        # Header
        self.kitsu_header = QtWidgets.QWidget()
        self.kitsu_header_lo = QtWidgets.QHBoxLayout(self.kitsu_header)
        self.kitsu_header_lo.setContentsMargins(10,5,10,5)
        self.kitsu_header_lo.setSpacing(2)

        self.shot_frames = QtWidgets.QLabel('')
        self.type_label = QtWidgets.QLabel('')

        self.redirect_task = QtWidgets.QToolButton()
        self.redirect_task.setIcon(QtGui.QIcon(resources.get_icon(('icons.libreflow', 'kitsu'))))
        self.redirect_task.setIconSize(QtCore.QSize(15,15))
        self.redirect_task.setStyleSheet('padding: 2px; border-radius: 4px; background-color: palette(button);')

        self.edit_status = QtWidgets.QToolButton()
        self.edit_status.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'send2'))))
        self.edit_status.setIconSize(QtCore.QSize(15,15))
        self.edit_status.setStyleSheet('padding: 2px; border-radius: 4px; background-color: palette(button);')
        self.edit_status.clicked.connect(self._on_edit_status_button_clicked)

        self.kitsu_header_lo.addWidget(self.shot_frames)
        self.kitsu_header_lo.addStretch()
        self.kitsu_header_lo.addWidget(self.type_label)
        self.kitsu_header_lo.addWidget(self.redirect_task)
        self.kitsu_header_lo.addWidget(self.edit_status)

        self.kitsu_lo.addWidget(self.kitsu_header)

        # Horizontal separator
        hline2 = QtWidgets.QFrame()
        hline2.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Plain)
        hline2.setLineWidth(2)
        hline2.setStyleSheet('color: #504f4f;')
        self.kitsu_lo.addWidget(hline2)

        # Comments
        self.kitsu_comments = QtWidgets.QTextBrowser()
        self.kitsu_comments.setOpenExternalLinks(True)
        self.kitsu_comments.setReadOnly(True)
        self.kitsu_comments.setPlaceholderText('No comment for this task.')
        self.kitsu_comments.setStyleSheet('border: none; background-color: transparent;')

        self.kitsu_lo.addWidget(self.kitsu_comments)

        # Warning message
        self.kitsu_task_warning = WarningFrame(
            self, f'Could not find Kitsu entity'
        )

        # Entity Description
        if self.data.task_id.get() is None:
            self.kitsu_not_found = True
            self.kitsu_lo.addWidget(self.kitsu_task_warning)
            self.kitsu_comments.hide()
        else:
            self.entity_description = QtWidgets.QTextEdit('')
            self.entity_description.setPlaceholderText('No description')
            self.entity_description.setReadOnly(True)
            self.entity_description.setStyleSheet('border: none; background-color: transparent;')
        
            # Set line spacing
            descBlockFmt = QtGui.QTextBlockFormat()
            descBlockFmt.setLineHeight(120, 1) # 1 = QtGui.QTextBlockFormat.LineHeightTypes.ProportionalHeight
            descTextCursor = self.entity_description.textCursor()
            descTextCursor.clearSelection()
            descTextCursor.select(QtGui.QTextCursor.Document)
            descTextCursor.mergeBlockFormat(descBlockFmt)

            self.kitsu_lo.addWidget(self.entity_description)
            self.entity_description.hide()

    def data_init(self):
        # Navigation buttons
        project_oid = self.page_widget.get_project_oid()

        if self.page_widget.session.cmds.Flow.exists(self.data.task_oid.get()) is False:
            self.entity_exists = False
            label_to_oid = self.split_oid(self.data.task_oid.get())
        else:
            label_to_oid = self.page_widget.session.cmds.Flow.split_oid(self.data.task_oid.get(), True, project_oid)

        for i, (label, goto_oid) in enumerate(label_to_oid):
            nav_button = NavigationButton(label, goto_oid, self)
            self.oid_lo.addWidget(nav_button)
            if i != len(label_to_oid)-1:
                self.oid_lo.addWidget(NavigationSeparator(
                    nav_button, self.data.task_oid.get() if self.entity_exists else None
                ))
            
        self.left_header_lo.addStretch()
        self.left_header_lo.addWidget(self.bookmark_button)

        # Bookmark
        if self.data.is_bookmarked.get():
            self.bookmark_button.show()

        # Files
        if self.entity_exists is False:
            self.left_widget.layout().addWidget(self.task_warning)
        elif self.data.dft_task_name.get() is not None:
            self.file_data_thread = FileDataRunner(self)
            self.file_data_thread.signals.progress.connect(self.page_widget.show_files)

        # Kitsu data
        if self.data.task_id.get():
            entity_type = self.data.entity_type.get()

            # Task Status
            self.type_label.setText(f'{self.data.task_type.get()} ')
            self.status_capsule = TaskStatusCapsule(self)
            self.kitsu_header_lo.insertWidget(3, self.status_capsule)
            
            # Redirect Task
            task_link = self.create_task_link(entity_type)
            self.redirect_task.clicked.connect(lambda: self._on_redirect_task_button_clicked(task_link))

            # Comments
            if self.data.task_comments.get():
                self.comments_thread = KitsuCommentsRunner(self)
                self.comments_thread.signals.progress.connect(self.page_widget.set_comment)

            if self.data.shot_frames.get():
                self.shot_frames.setText(str(self.data.shot_frames.get())+' frames')
            else:
                self.shot_frames.hide()
            self.entity_description.setText(self.data.entity_description.get())

        # Expand
        if self.data.task_id.get() in self.tasks_list.tasks_expanded:
            expand_state = self.tasks_list.tasks_expanded[self.data.task_id.get()]

            if isinstance(expand_state, bool): # Handle old data
                self.expanded = expand_state
            elif isinstance(expand_state, list):
                self.expanded = expand_state[0]

        elif self.page_widget.get_auto_expand():
            self.expanded = True
        
        self.expand()

    def split_oid(self, oid):
        root_oid = '/'.join(oid.split('/', 2)[:2])
        
        oid_no_project = f"/{oid.split('/', 2)[2]}"
        oid_split = re.findall(r"\/\w+(?=\/|)", oid_no_project)

        splited = []
        if len(oid_split) % 2 == 0:
            oid_iter = iter(oid_split)
            oid_pair = zip(oid_iter, oid_iter)
            store_previous_oid = root_oid
            for entity_type, entity_name in oid_pair:
                object_oid = f'{store_previous_oid}{entity_type}{entity_name}'
                splited.append([f'{entity_type[1:]}:{entity_name[1:]}', None])
                store_previous_oid = object_oid

        return splited

    # Used for RefreshWorker
    def refresh(self):
        self.file_data = []
        self.file_actions = []

        self.bookmark_button.show() if self.data.is_bookmarked.get() else self.bookmark_button.hide()

        if self.data.dft_task_name.get() is not None:
            self.file_data_thread = FileDataRunner(self)
            self.file_data_thread.signals.progress.connect(self.page_widget.show_files)

        if self.data.task_id.get():
            # Task Status
            self.type_label.setText(f'{self.data.task_type.get()} ')
            self.status_capsule.refresh()

            if self.data.task_comments.get():
                self.comments_thread = KitsuCommentsRunner(self)
                self.comments_thread.signals.progress.connect(self.page_widget.set_comment)

            if self.data.shot_frames.get():
                self.shot_frames.setText(str(self.data.shot_frames.get())+' frames')
            else:
                self.shot_frames.hide()

            self.entity_description.setText(self.data.entity_description.get())

    def create_file_data(self, oids):
        for file_oid in oids:
            activate_oid = self.page_widget.session.cmds.Flow.call(file_oid, 'activate_oid', [], {}) or None
            self.file_data.append(FileData(
                self.page_widget.session,
                file_oid,
                self.data.task_oid.get().split('/')[-1],
                activate_oid=activate_oid
            ))

    def create_task_link(self, entity_type):
        return '{server}/productions/{project}/{entity}/tasks/{task}'.format(
            server=self.page_widget.get_server_url(),
            project=self.page_widget.get_project_id(),
            entity=entity_type.lower(),
            task=self.data.task_id.get()
        )

    def create_revision_link(self, entity_type, preview_id):
        return '{server}/productions/{project}/{entity}/tasks/{task}/previews/{preview}'.format(
            server=self.page_widget.get_server_url(),
            project=self.page_widget.get_project_id(),
            entity=entity_type.lower(),
            task=self.data.task_id.get(),
            preview=preview_id
        )
    
    def expand(self):
        if self.expanded:
            # Switch to the correct expand icon
            self.expand_button.setIcon(resources.get_icon(('icons.gui', 'arrow-down')))
            
            # If row height value is stored, use it
            height_value = None
            if self.data.task_id.get() in self.tasks_list.tasks_expanded:
                expand_state = self.tasks_list.tasks_expanded[self.data.task_id.get()]

                if isinstance(expand_state, list):
                    height_value = expand_state[1]  

            self.tasks_list.setRowHeight(self.row_index, height_value if height_value else 200)

            # Show additionnal border, file and kitsu widgets
            self.left_widget.layout().itemAt(1).widget().show()
            if self.entity_exists is False:
                self.task_warning.show()
            else:
                self.left_widget.layout().itemAt(2).widget().show()
            self.right_kitsu.layout().itemAt(1).widget().show()

            if self.kitsu_not_found:
                self.kitsu_task_warning.show()
            elif self.kitsu_description:
                self.entity_description.show()
            else:
                self.kitsu_comments.show()
        else:
            # Switch to the correct expand icon
            self.expand_button.setIcon(resources.get_icon(('icons.gui', 'arrow-right')))

            # Set a fixed row height value
            self.tasks_list.setRowHeight(self.row_index, 67)

            # Hide additionnal border, file and kitsu widgets
            self.left_widget.layout().itemAt(1).widget().hide()
            if self.entity_exists is False:
                self.task_warning.hide()
            else:
                self.left_widget.layout().itemAt(2).widget().hide()
            self.left_widget.layout().itemAt(2).widget().hide()
            self.right_kitsu.layout().itemAt(1).widget().hide()

            if self.kitsu_not_found:
                self.kitsu_task_warning.hide()
            elif self.kitsu_description:
                self.entity_description.hide()
            else:
                self.kitsu_comments.hide()

    def store_expand_state(self):
        # Get store height value if exists
        height_value = 0
        if self.data.task_id.get() in self.tasks_list.tasks_expanded:
            expand_state = self.tasks_list.tasks_expanded[self.data.task_id.get()]

            if isinstance(expand_state, list):
                height_value = expand_state[1]

        self.tasks_list.tasks_expanded[self.data.task_id.get()] = [
            self.expanded, height_value if self.expanded == False else self.tasks_list.rowHeight(self.row_index)
        ]
        self.page_widget.update_presets(expand_data=self.tasks_list.tasks_expanded)

    def eventFilter(self, obj, event):
        # Reset to default cursor shape
        if event.type() == QtCore.QEvent.Enter:
            if self.tasks_list.viewport().cursor().shape() != QtCore.Qt.ArrowCursor:
                self.tasks_list.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        return super().eventFilter(obj, event)

    def _on_expand_button_clicked(self):
        self.expanded = False if self.expanded == True else True
        self.expand()
        
        self.expand_thread.start()

    def _on_bookmark_button_clicked(self):
        is_bookmarked = self.page_widget.toggle_bookmark(self.data.task_oid.get())
        self.bookmark_button.setIcon(resources.get_icon(
            ('icons.gui', 'star') if is_bookmarked else ('icons.gui', 'star-1')
        ))

    def _on_redirect_task_button_clicked(self, link):
        webbrowser.open(link)
    
    def _on_edit_status_button_clicked(self):
        dialog = EditStatusDialog(self)
        dialog.exec()


class CompareDataWorker(QtCore.QObject):

    # Fetch data and compare it to determine whether the list needs updating

    finished = QtCore.Signal(bool)

    def __init__(self, page_widget):
        super(CompareDataWorker, self).__init__()
        self.page_widget = page_widget

    def run(self):
        status = self.page_widget.session.cmds.Flow.call(
            self.page_widget.oid, 'compare', {}, {}
        )
        self.finished.emit(status)


class RefreshWorker(QtCore.QObject):

    # Main worker for update MyTasksList widget

    progress = QtCore.Signal(object)
    finished = QtCore.Signal()

    def __init__(self, page_widget):
        super(RefreshWorker, self).__init__()
        self.page_widget = page_widget

    def run(self):
        try:
            tasks = self.page_widget.session.cmds.Flow.call(
                self.page_widget.oid, 'get_tasks', {self.page_widget.force_update}, {}
            )
        except Exception as e:
            print_exc()
            self.page_widget.session.log_error(f'[MyTasks] An error has occurred')
            self.page_widget.content.popup.refresh('Error ⚠', 'Check the console')

        for task in tasks:
            self.progress.emit(task)
        
        self.finished.emit()


class ExpandStateWorker(QtCore.QObject):

    # Store task expand state with row height value

    finished = QtCore.Signal()

    def __init__(self, task_widget):
        super(ExpandStateWorker, self).__init__()
        self.task_widget = task_widget

    def run(self):
        self.task_widget.store_expand_state()
        self.finished.emit()


class HeaderlessTableView(QtWidgets.QTableWidget):

    # Custom TableWidget for resize rows without showing headers

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_boundary_height = 15
        self.m_row_index = -1

        self.setColumnCount(1)

        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        self.horizontalHeader().setStretchLastSection(True)
        self.setShowGrid(False)

        self.setStyleSheet('''
        QTableView {
            background-color: transparent;
            border: none;
        }
        padding: 0;
        ''')

        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(20)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.viewport().setMouseTracking(True)
        self.viewport().installEventFilter(self)

    def row_index(self):
        return self.m_row_index
    
    def eventFilter(self, obj, event):
        # Check if cursor is on a row boundary
        if event.type() == QtCore.QEvent.MouseMove:
            # Get row index at the top
            row_top = self.rowAt(self.mapFromGlobal(QtGui.QCursor.pos()).y() - self.m_boundary_height / 2)
            # Get row index at the bottom
            row_bottom = self.rowAt(self.mapFromGlobal(QtGui.QCursor.pos()).y() + self.m_boundary_height / 2)

            was_on_boundary = self.m_row_index != -1

            if row_top != row_bottom:
                if self.m_row_index == -1:
                    if row_top != -1:
                        # Set new row index
                        self.m_row_index = row_top
            else:
                # Reset to default value
                self.m_row_index = -1
            
            is_on_boundary = self.m_row_index != -1

            if is_on_boundary != was_on_boundary:
                self.entered_row_boundary(is_on_boundary)
    
        return super().eventFilter(obj, event)

    def entered_row_boundary(self, entered):
        pass


class MyTasksList(HeaderlessTableView):

    def __init__(self, page_widget):
        super(MyTasksList, self).__init__(page_widget)
        self.page_widget = page_widget
        self.tasks_expanded = self.page_widget.get_user_expanded()
        self.cellsContent = []

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Set attributes for drag handler
        self.m_dragging = False
        self.m_mouse_pos = QtCore.QPoint()
        self.m_cursor = QtGui.QCursor()

        self.scroll_start = 0
        self.row_position = QtCore.QPoint()
        self.row_position_reset = False

        self.viewport().installEventFilter(self)

        # Display a row line when a task can be resized
        # self.setItemDelegate(TaskBorderDelegate(self))
    
    def eventFilter(self, obj, event):
        # Enable drag if mouse click is press
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.page_widget.setFocus()
            if self.row_index() != -1:
                task_widget = self.cellWidget(self.row_index(), 0)

                # Only accept if task is expanded
                if task_widget and task_widget.expanded:
                    # Store mouse position and scroll value
                    self.m_mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())
                    self.scroll_start = self.verticalScrollBar().value()
                    
                    self.m_dragging = True
                    return True
        
        # Disable drag if mouse click is release
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            self.m_dragging = False
            self.row_position_reset = False
            
            # To be able to resize if we leave the row at minimum height size
            if self.rowHeight(self.row_index()) == 185:
                self.setRowHeight(self.row_index(), 186)
            
            # Store task expand state with row height
            task_widget = self.cellWidget(self.row_index(), 0)
            if task_widget:
                task_widget.expand_thread.start()
        
        # Drag handler
        elif event.type() == QtCore.QEvent.MouseMove:
            if self.m_dragging:
                # Calculate delta from previous mouse y position
                # Positive value, mouse goes to the bottom, Negative value, mouse goes to the top
                delta = self.mapFromGlobal(QtGui.QCursor.pos()).y() - self.m_mouse_pos.y()

                # Force a minimum row height size
                if (
                    self.rowHeight(self.row_index()) <= 185
                    and self.mapFromGlobal(QtGui.QCursor.pos()).y() <= self.row_position.y()
                ):
                    self.setRowHeight(self.row_index(), 185)

                # Don't resize if row position is reset and cursor position is above
                elif self.row_position_reset and self.mapFromGlobal(QtGui.QCursor.pos()).y() <= self.row_position.y():
                    self.setRowHeight(self.row_index(), self.rowHeight(self.row_index()))

                else:
                    # Reset row position if mouse is going to bottom and scroll value is lower from start value
                    if delta > 0 and (self.verticalScrollBar().value() < self.scroll_start):
                        self.row_position_reset = True
                        self.row_position.setY(
                            self.mapFromGlobal(QtGui.QCursor.pos()).y() + (self.scroll_start - self.verticalScrollBar().value())
                        )
                        self.scroll_start = self.verticalScrollBar().value()
                    else:
                        # Set new row height value
                        self.row_position_reset = False
                        self.setRowHeight(self.row_index(), self.rowHeight(self.row_index()) + delta)

                    # Update row position if it's not reset
                    if self.row_position_reset is False:
                        self.row_position = self.mapFromGlobal(QtGui.QCursor.pos())
                
                # Update mouse position
                self.m_mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())
                return True
        
        return super().eventFilter(obj, event)
    
    # Switch cursor shape if user can resize a row
    def entered_row_boundary(self, entered):
        task_widget = self.cellWidget(self.row_index(), 0)
        
        # Only accept if task is expanded
        if task_widget and task_widget.expanded:
            if entered:
                self.m_cursor = self.viewport().cursor()
                self.viewport().setCursor(QtGui.QCursor(QtCore.Qt.SplitVCursor))
                return
        
        # Reset to default cursor shape
        self.viewport().setCursor(self.m_cursor)

    def clear(self):
        for row, column, task in reversed(self.cellsContent):
            if task:
                task.setParent(None)
                task.deleteLater()
        
        self.setRowCount(0)
        self.cellsContent = []

    def refresh(self, force_update=False):
        self.blockSignals(True)
        
        self.page_widget.start = time.time()
        if force_update:
            self.clear()
            self.page_widget.force_update = True
            self.page_widget.content.popup.show()
        elif self.page_widget.get_cache_key() is None:
            self.page_widget.force_update = True

        if not self.page_widget.thread.isRunning():
            self.page_widget.thread.start()
        
        self.blockSignals(False)

    def refresh_search(self, query_filter):
        count = 0
        keywords = query_filter.split()
        query_filter = '.*'+'.*'.join(keywords)
        for row, column, task in reversed(self.cellsContent):
            if task is not None:
                if re.match(query_filter, task.data.task_oid.get()):
                    self.showRow(row)
                    count = count + 1
                else:
                    self.hideRow(row)
        self.page_widget.footer.left_text.setText(str(count)+' Tasks')

    def get_last_idx(self):
        last_r, last_c = divmod(self.get_count(), self.columnCount())
        return last_r, last_c

    def addTask(self, data):
        self.blockSignals(True)

        start_r, start_c = self.get_last_idx()
        if start_c == 0:
            self.setRowCount(start_r + 1)
        
        widget = TaskItem(self, data, start_r)
        self.setCellWidget(start_r, start_c, widget)

        self.cellsContent.append((start_r, start_c, widget))

        self.blockSignals(False)

    def get_count(self):
        return len(self.cellsContent)

    def toggle_description(self):
        for row, column, task in reversed(self.cellsContent):
            if task is not None and task.data.task_id.get():
                if task.kitsu_description:
                    task.kitsu_description = False
                    if task.expanded:
                        task.entity_description.hide()
                        task.kitsu_comments.show()
                else:
                    task.kitsu_description = True
                    if task.expanded:
                        task.kitsu_comments.hide()
                        task.entity_description.show()


class MyTasksSearchOverlay(QtWidgets.QWidget):

    # Search is overlay on top of FilterStatusComboBox

    def __init__(self, page_widget):
        super(MyTasksSearchOverlay, self).__init__(page_widget)
        self.page_widget = page_widget

        self.build()

    def build(self):
        hlo = QtWidgets.QHBoxLayout(self)
        hlo.setContentsMargins(0,1,0,10)

        self.widget = MyTasksSearch(self)
        hlo.addSpacing(46)
        hlo.addWidget(self.widget)
        hlo.addStretch()

        self.region = QtGui.QRegion(self.widget.frameGeometry())
        self.region.translate(hlo.itemAt(0).sizeHint().width(), 2)
        self.setMask(self.region)

    def settingMask(self):
        self.region = QtCore.QRect(
            self.layout().itemAt(0).sizeHint().width(),
            2,
            self.widget.anim.endValue(),
            self.widget.frameGeometry().height()
        )
        self.setMask(self.region)
        try:
            self.widget.anim.finished.disconnect()
        except Exception:
            pass


class MyTasksHeader(QtWidgets.QWidget):

    # Main actions for updating, searching and customising the list

    def __init__(self, content):
        super(MyTasksHeader, self).__init__(content)
        self.content = content
        self.page_widget = content.page_widget
        self.setStyleSheet('''
        QPushButton {
            background-color: palette(dark);
            border: 2px solid palette(button);
            border-radius: 7px;
        }
        ''')

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)

        self.opacity_anim = QtCore.QPropertyAnimation(self.opacity_effect, b'opacity')
        self.opacity_anim.setDuration(400)
        self.opacity_anim.setEasingCurve(QtCore.QEasingCurve.OutQuint)

        self.build_completed = False
        self.build()

    def build(self):
        # Refresh button
        self.refresh_button = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.gui', 'refresh'))), '')
        self.refresh_button.clicked.connect(self._on_refresh_button_clicked)
        self.refresh_button.setIconSize(QtCore.QSize(20,20))
        self.refresh_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # If the list needs updating
        self.update_label = QtWidgets.QLabel('Tasks list needs to be updated ⚠️')
        self.update_label.setStyleSheet('color: #FF584D; font-weight: bold;')
        self.update_label.hide()
        
        # Filter task status
        self.filter_label = QtWidgets.QLabel('Filter by')
        
        self.filter_combobox = FilterStatusComboBox()
        self.filter_combobox.setGraphicsEffect(self.opacity_effect)
        self.filter_combobox.addItem('Default', preset=True)
        self.filter_combobox.addItem('-')
        self.filter_combobox.addItems(sorted([task.upper() for task in self.page_widget.get_task_statutes(True)]))
        self.filter_combobox.setDefaultPreset()
        filter_value = self.page_widget.get_user_filter()
        if filter_value == []:
            self.filter_combobox.setChecked(['Default'], True)
        else:
            for statues in filter_value:
                self.filter_combobox.setChecked([statues], True)
        self.filter_combobox.previousData = self.filter_combobox.fetchNames()
        self.page_widget.update_presets(filter_data=self.filter_combobox.previousData)
        
        # Sort list
        self.sort_label = QtWidgets.QLabel('Sort by')
        self.sort_combobox = QtWidgets.QComboBox()
        self.sort_combobox.addItems(['Entity name', 'Status', 'Latest update'])
        self.sort_combobox.currentTextChanged.connect(self._on_sort_combobox_changed)
        self.sort_combobox.setView(QtWidgets.QListView())
        self.sort_combobox.setStyleSheet('''
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
        )
        sort_value = self.page_widget.get_user_sorted()
        if sort_value == None:
            self.page_widget.update_presets(sort_data='Entity name')
        else:
            self.sort_combobox.setCurrentText(sort_value)

        # Web shortcuts
        self.kitsu_tasks = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.libreflow', 'kitsu'))), 'My Tasks')
        self.kitsu_tasks.clicked.connect(self._on_kitsu_tasks_button_clicked)
        self.kitsu_tasks.setIconSize(QtCore.QSize(16,16))
        self.kitsu_tasks.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        timesheet_label = os.environ.get('LF_MYTASKS_FDT_LABEL')
        if timesheet_label is None :
            timesheet_label = 'Timesheet'
        self.fdt_button = QtWidgets.QPushButton(timesheet_label)

        self.fdt_button.clicked.connect(self._on_fdt_button_clicked)
        self.fdt_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.refresh_button)
        hlo.addSpacing(self.content.search.widget.width()+8)
        hlo.addWidget(self.update_label)
        hlo.addWidget(self.filter_label)
        hlo.addWidget(self.filter_combobox)
        hlo.addSpacing(35)
        hlo.addWidget(self.sort_label)
        hlo.addWidget(self.sort_combobox)
        hlo.addStretch()
        hlo.addWidget(self.kitsu_tasks)
        hlo.addWidget(self.fdt_button)
        hlo.setContentsMargins(0,0,0,10)
        self.setLayout(hlo)
        self.build_completed = True

    def toggle_warning(self):
        if self.update_label.isVisible():
            self.update_label.hide()
            self.filter_label.show()
            self.filter_combobox.show()
            self.sort_label.show()
            self.sort_combobox.show()
        else:
            self.filter_label.hide()
            self.filter_combobox.hide()
            self.sort_label.hide()
            self.sort_combobox.hide()
            self.update_label.show()

    def toggle_filter(self, hidden):
        # Used for MyTasksSearch focus animation
        if hidden:
            self.opacity_anim.setStartValue(1.0)
            self.opacity_anim.setEndValue(0.0)
        else:
            self.opacity_anim.setStartValue(0.0)
            self.opacity_anim.setEndValue(1.0)
            
        self.opacity_anim.start()

    def _on_sort_combobox_changed(self, value):
        if self.build_completed == False:
            return
        self.page_widget.update_presets(sort_data=value)
        self.page_widget.content.list.refresh(True)

    def _on_refresh_button_clicked(self):
        self.page_widget.stopThreads()
        if self.update_label.isVisible():
            self.toggle_warning()
        self.page_widget.content.list.refresh(force_update=True)

    def _on_kitsu_tasks_button_clicked(self):
        webbrowser.open(self.page_widget.get_server_url() + '/' + self.page_widget.get_url_suffix())

    def _on_fdt_button_clicked(self):
        timesheet_url = os.environ.get('LF_MYTASKS_FDT_URL')
        print (timesheet_url)
        if timesheet_url is not None:
            webbrowser.open(timesheet_url)


class MyTasksContent(QtWidgets.QWidget):

    def __init__(self, page_widget):
        super(MyTasksContent, self).__init__(page_widget)
        self.setObjectName('MyTasksContent')
        self.page_widget = page_widget

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('#MyTasksContent { background-color: palette(dark); border-radius: 5px; }')

        self.build()

    def build(self):
        grid = QtWidgets.QGridLayout(self)

        self.search = MyTasksSearchOverlay(self.page_widget)
        self.header = MyTasksHeader(self)
        self.list = MyTasksList(self.page_widget)
        self.popup = PopUpDialog(self)
        grid.addWidget(self.header, 0, 0)
        grid.addWidget(self.search, 0, 0, 1, 1)
        grid.addWidget(self.list, 1, 0)
        grid.addWidget(self.popup, 1, 0, 1, 1)


class MyTasksPageWidget(CustomPageWidget):

    def build(self):
        # To multithread files list and kitsu comments widget
        self.__pool = QtCore.QThreadPool()
        self.__pool.setMaxThreadCount(self.__pool.globalInstance().maxThreadCount())

        self.start = time.time()
        self.force_update = False

        self.setStyleSheet('outline: 0;')

        self.content = MyTasksContent(self)
        self.footer = MyTasksFooter(self)

        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(0,0,0,0)
        vlo.setSpacing(0)
        vlo.addWidget(self.content)
        vlo.addWidget(self.footer)

        self.key_press_start_time = -1

        # Thread setup
        self.thread = QtCore.QThread()
        self.compare_thread = QtCore.QThread()
        self.auto_compare = QtCore.QTimer(self)

        self.list_refresh = RefreshWorker(self)
        self.list_refresh.moveToThread(self.thread)

        self.list_compare = CompareDataWorker(self)
        self.list_compare.moveToThread(self.compare_thread)

        self.thread.started.connect(self.list_refresh.run)
        self.list_refresh.finished.connect(self.thread.quit)
        self.list_refresh.progress.connect(self.addTaskWidget)
        self.thread.finished.connect(self.complete_refresh)

        self.compare_thread.started.connect(self.list_compare.run)
        self.list_compare.finished.connect(self.compare_thread.quit)
        self.list_compare.finished.connect(self.needs_update)

        self.auto_compare.setInterval(30000)
        self.auto_compare.timeout.connect(self.compare_thread.start)

        self.content.search.widget.textChanged.connect(self.content.list.refresh_search)
        self.content.list.refresh()

        self.setFocus()
    
    def sizeHint(self):
        return QtCore.QSize(0, 2880)

    def mousePressEvent(self, event):
        self.setFocus()
    
    def keyPressEvent(self, event):
        super(MyTasksPageWidget, self).keyPressEvent(event)

        if event.key() == QtCore.Qt.Key_Shift:
            self.content.list.toggle_description()
            self.key_press_start_time = time.time()

    def keyReleaseEvent(self, event):
        super(MyTasksPageWidget, self).keyReleaseEvent(event)
        key_press_time = time.time() - self.key_press_start_time

        if event.key() == QtCore.Qt.Key_Shift and key_press_time > 0.5:
            self.content.list.toggle_description()

    def stopThreads(self):
        self.auto_compare.stop()
        self.__pool.clear()

    # Progress signal for RefreshWorker
    def addTaskWidget(self, data):
        self.content.list.addTask(data)

    # Finish signal for RefreshWorker
    def complete_refresh(self):
        # Update tasks expanded user list
        for task_id, value in list(self.content.list.tasks_expanded.items()):
            has_key = False
            for row, column, task in reversed(self.content.list.cellsContent):
                if task and task_id == task.data.task_id.get():
                    has_key = True
                    break
            if not has_key:
                self.content.list.tasks_expanded.pop(task_id)
        
        self.update_presets(expand_data=self.content.list.tasks_expanded)

        # Update some ui elements
        self.footer.refresh_count()
        self.content.popup.hide()
        if self.content.search.widget.text():
            self.content.list.refresh_search(self.content.search.widget.text())

        # Start threads
        for row, column, task in reversed(self.content.list.cellsContent):
            if task and task.file_data_thread:
                self.__pool.start(task.file_data_thread)
            if task and task.comments_thread:
                self.__pool.start(task.comments_thread)
        
        if self.force_update is False and self.compare_thread.isRunning() is False:
            self.compare_thread.start()
        
        self.auto_compare.start()

        self.force_update = False

    # Progress signal for KitsuCommentsRunner
    def set_comment(self, task, comment):
        scroll_value = task.kitsu_comments.verticalScrollBar().value()
        task.kitsu_comments.setHtml(comment)
        task.kitsu_comments.verticalScrollBar().setValue(scroll_value)
    
    # Progress signal for FileDataRunner
    def show_files(self, task, empty):
        try:
            task.files_list.model.layoutChanged.emit()
            task.files_list.update()
        except RuntimeError:
            pass

    # Finished signal for CompareDataWorker
    def needs_update(self, status):
        # Update current tasks
        for row, column, task in reversed(self.content.list.cellsContent):
            if task and task.data:
                task.refresh()
            if task and task.file_data_thread:
                self.__pool.start(task.file_data_thread)
            if task and task.comments_thread:
                self.__pool.start(task.comments_thread)

        # Show warning label if any new or deassigned tasks
        if status is False and self.content.header.update_label.isVisible() is False:
            self.content.header.toggle_warning()

    def get_cache_key(self):
        return self.session.cmds.Flow.call(
            self.oid+"/_settings/tasks", 'get_cache_key', {}, {}
        )
    
    def get_project_oid(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_project_oid', {}, {}
        )

    def get_project_id(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_project_id', {}, {}
        )

    def get_project_fps(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_project_fps', {}, {}
        )

    def get_user_filter(self):
        return self.session.cmds.Flow.get_value(self.oid+'/_settings/task_statues_filter')

    def get_user_sorted(self):
        return self.session.cmds.Flow.get_value(self.oid+'/_settings/task_sorted')
    
    def get_user_expanded(self):
        return self.session.cmds.Flow.get_value(self.oid+'/_settings/tasks_expanded')

    def get_auto_expand(self):
        return self.session.cmds.Flow.get_value(self.oid+'/_settings/auto_expand')

    def get_task_comments(self, task_id):
        return self.session.cmds.Flow.call(
            self.oid, 'get_task_comments', {task_id}, {}
        )

    def get_server_url(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_server_url', {}, {}
        )
    
    def get_url_suffix(self):
        return self.session.cmds.Flow.call(
            self.oid, 'get_url_suffix', {}, {}
        )

    def is_uploadable(self, file_name):
        return self.session.cmds.Flow.call(
            self.oid, 'is_uploadable', [file_name], {}
        )

    def get_task_statutes(self, short_name):
        return self.session.cmds.Flow.call(
            self.oid, 'get_task_statutes', [short_name], {}
        )

    def get_task_status(self, task_status_name):
        return self.session.cmds.Flow.call(
            self.oid, 'get_task_status', [task_status_name], {}
        )

    def set_task_status(self, task_id, task_status_name, comment, files):
        return self.session.cmds.Flow.call(
            self.oid, 'set_task_status', [task_id, task_status_name, comment, files], {}
        )

    def upload_preview(self, entity_id, task_name, task_status_name, file_path, comment):
        return self.session.cmds.Flow.call(
            self.oid, 'upload_preview', [entity_id, task_name, task_status_name, file_path, comment], {}
        )

    def toggle_bookmark(self, oid):
        return self.session.cmds.Flow.call(
            self.oid, 'toggle_bookmark', [oid], {}
        )

    def update_presets(self, filter_data=None, sort_data=None, expand_data=None):
        if filter_data:
            self.session.cmds.Flow.set_value(self.oid+'/_settings/task_statues_filter', filter_data)
        if sort_data:
            self.session.cmds.Flow.set_value(self.oid+'/_settings/task_sorted', sort_data)
        if expand_data:
            self.session.cmds.Flow.set_value(self.oid+'/_settings/tasks_expanded', expand_data)
        return self.session.cmds.Flow.call(
            self.oid+'/_settings', 'update_presets', {}, {}
        )
