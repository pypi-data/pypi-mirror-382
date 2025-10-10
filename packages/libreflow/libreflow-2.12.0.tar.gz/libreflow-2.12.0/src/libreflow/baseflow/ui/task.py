import os
import six
import time
import base64
import colorsys
import xml.etree.ElementTree as Et
from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui, CustomPageWidget
from kabaret.app.ui.gui.widgets.flow_layout import FlowLayout
from kabaret.app import resources
from kabaret.app.ui.gui.icons import flow as _

from ...resources.icons import gui as _

from .controller import Controller
from .file import FileWidget
from .file_list import FileListsWidget


def get_icon_ref(icon_name, resource_folder='icons.flow'):
    if isinstance(icon_name, six.string_types):
        icon_ref = (resource_folder, icon_name)
    else:
        icon_ref = icon_name

    return icon_ref


# Task page
# ----------------------


class TaskActionsButton(QtWidgets.QToolButton):
    """
    Holds the task's action shortcuts displayed in the task page header.
    """
    def __init__(self, flow_page, controller):
        super(TaskActionsButton, self).__init__()
        self.controller = controller
        self.flow_page = flow_page
        self.build()
    
    def build(self):
        self.setIcon(resources.get_icon(('icons.gui', 'menu')))
        self.setIconSize(QtCore.QSize(25, 25))
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setFixedWidth(40)

        # Add actions
        self.menu = QtWidgets.QMenu('Task actions', self)

        for ta in self.controller.task_actions():
            a = self.menu.addAction(ta.label, lambda a=ta: self._on_action_menu_triggered(a))
            a.setIcon(resources.get_icon(ta.icon))
            a.setToolTip(ta.tooltip)
        
        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setArrowType(QtCore.Qt.NoArrow)
        self.setMenu(self.menu)

    def _on_action_menu_triggered(self, action):
        self.flow_page.show_action_dialog(action.oid)


class TaskBookmarkButton(QtWidgets.QToolButton):
    """
    Allows to add the task to the user's bookmarks
    """
    def __init__(self, flow_page, controller):
        super(TaskBookmarkButton, self).__init__()
        self.controller = controller
        self.flow_page = flow_page
        self.build()

        self.clicked.connect(self._on_button_triggered)
    
    def build(self):
        if self.controller.is_bookmarked():
            self.setIcon(resources.get_icon(('icons.gui', 'star')))
        else:
            self.setIcon(resources.get_icon(('icons.gui', 'star-1')))
        self.setIconSize(QtCore.QSize(25, 25))
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.setFixedWidth(40)

    def _on_button_triggered(self):
        self.controller.toggle_bookmark()
        self.build()


class TaskHeader(QtWidgets.QWidget):
    """
    Represents the header of the task widget, displaying the task's name and icon.
    """
    def __init__(self, controller, task_widget):
        super(TaskHeader, self).__init__()
        self.controller = controller
        self.task_oid = task_widget.oid
        self.flow_page = task_widget.page

        self.build()
    
    def build(self):
        folder, icon = self.controller.task_small_icon()
        self.label_icon = QtWidgets.QLabel()
        pm = resources.get_pixmap(folder, icon)
        self.label_icon.setPixmap(pm.scaled(28, 28, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.label_icon.setFixedWidth(40)
        self.label_icon.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setWeight(QtGui.QFont.Bold)
        self.label_name = QtWidgets.QLabel(self.controller.task_label())
        self.label_name.setFont(font)
        self.label_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.bookmark_button = TaskBookmarkButton(self.flow_page, self.controller)
        self.actions_button = TaskActionsButton(self.flow_page, self.controller)

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self.label_icon)
        hlo.addWidget(self.label_name)
        hlo.addStretch(1)
        hlo.addWidget(self.bookmark_button)
        hlo.addWidget(self.actions_button)
        hlo.setContentsMargins(0, 0, 0, 0)
        hlo.setSpacing(1)
        self.setLayout(hlo)

        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor(self.controller.task_color()))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        
        self.setFixedHeight(40)


class TaskView(QtWidgets.QWidget):

    def __init__(self, controller, task_widget):
        super(TaskView, self).__init__()
        self.task_widget = task_widget
        self.controller = controller

        self.build()
    
    def build(self):
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.file_lists = FileListsWidget(self.task_widget, self.splitter)
        self.file_view = FileWidget(self.task_widget, self.splitter)
        self.file_view.setVisible(False)
        self.splitter.setSizes([100, 100])

        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self.splitter)
        vlo.setSpacing(1)
        vlo.setContentsMargins(1, 1, 1, 1)
        self.setLayout(vlo)


class TaskPageWidget(CustomPageWidget):

    def __init__(self, host, session):
        super(TaskPageWidget, self).__init__(host, session)
        self.controller = None

    def build(self):
        # TODO: Task header
        # TODO: File lists
        # TODO: File view
        #       - header
        #       - history
        # self.parent().layout().setStretch(1, 0)
        import time
        start = time.time()
        
        self.controller = Controller(self)
        self.header = TaskHeader(self.controller, self)
        self.view = TaskView(self.controller, self)
        
        vlo = QtWidgets.QVBoxLayout()
        vlo.addWidget(self.header)
        vlo.addWidget(self.view)
        vlo.setSpacing(0)
        vlo.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlo)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.session.log_info('Task page built in %.3fs' % (time.time() - start))

        self.key_press_start_time = -1
    
    def on_touch_event(self, oid):
        if self.controller is not None:
            self.controller.on_touch_event(oid)
    
    def sizeHint(self):
        return QtCore.QSize(0, 2880)
    
    def keyPressEvent(self, event):
        super(TaskPageWidget, self).keyPressEvent(event)

        if event.key() == QtCore.Qt.Key_Escape:
            # This will automatically reset the selected item in the controller
            # (see selectionChanged())
            self.controller.clear_selected()
        elif event.key() == QtCore.Qt.Key_Shift:
            self.controller.toggle_file_statutes()
            self.key_press_start_time =  time.time()

    def keyReleaseEvent(self, event):
        super(TaskPageWidget, self).keyReleaseEvent(event)
        key_press_time = time.time() - self.key_press_start_time

        if event.key() == QtCore.Qt.Key_Shift and key_press_time > 0.5:
            self.controller.toggle_file_statutes()


# Task list page
# ----------------------

TASK_LIST_CSS = """
QScrollArea {
    border: none;
    border-radius: 5px;
}
#ScrollAreaContainer { 
    background-color: #232d33;
    border: none;
    border-radius: 5px;
}
#TaskButton {
    margin: 0;
    padding: 0;
    border: none;
    border-radius: 14px;
}
#TaskButton[svg="true"] {
    background-color: transparent;
}
#TaskButton:hover {
    border: 1px solid palette(highlight);
}
QPushButton:focus {
    outline: none;
}
"""


class TaskButton(QtWidgets.QWidget):

    def __init__(self, page_widget, data):
        super(TaskButton, self).__init__(page_widget)
        self.page_widget = page_widget
        self.task_oid = data['oid']
        self.task_name = data['name']
        self.task_enabled = data['enabled']
        self.task_icon = data['icon']
        self.task_color = data['color']

        self.opacity_effect = QtWidgets.QGraphicsOpacityEffect()

        self.build()
    
    def build(self):
        lo = QtWidgets.QVBoxLayout(self)

        # Task button
        button = QtWidgets.QPushButton()
        button.setObjectName('TaskButton')
        button.clicked.connect(self._on_clicked)
        button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(self._on_context_menu)
        lo.addWidget(button, alignment=QtCore.Qt.AlignCenter)

        # Set button icon
        # If default task icon, re-color function is used
        _, ext = os.path.splitext(resources.get(*self.task_icon))
        if ext == '.svg' and self.task_icon[0] == 'icons.tasks':
            # Make button background transparent
            button.setProperty('svg', True)

            default_icon = QtGui.QIcon()
            svg_icon = self.getSVGDefaultIcon()
            
            # Remove greyed out effect when button is disabled
            default_icon.addPixmap(svg_icon, QtGui.QIcon.Mode.Disabled)
            default_icon.addPixmap(svg_icon, QtGui.QIcon.Mode.Disabled)

            button.setIcon(QtGui.QIcon(default_icon))
            button.setFixedSize(QtCore.QSize(107, 107))
            button.setIconSize(QtCore.QSize(105, 105))
        else:
            # Upscale pixmap
            pixmap = resources.get_pixmap(*self.task_icon)
            pm_resized = pixmap.scaled(105, 105, QtCore.Qt.KeepAspectRatio)

            button.setIcon(QtGui.QIcon(pm_resized))
            button.setFixedSize(QtCore.QSize(107, 107))
            button.setIconSize(QtCore.QSize(button.width()-30, button.height()-30))

            if self.task_color:
                button.setStyleSheet(f'background-color: {self.task_color}')

        # Task name
        label = QtWidgets.QLabel(f'<center>{self.task_name.upper()}</center>')
        label.setMaximumWidth(110)
        label.setWordWrap(True)
        lo.addWidget(label)

        # Apply opacity if disabled task
        if self.task_enabled is False:
            button.setEnabled(False)

            self.opacity_effect.setOpacity(0.3)
            self.setGraphicsEffect(self.opacity_effect)

    def getSVGDefaultIcon(self):
        # Only change color if a hex code is defined
        if self.task_color is None:
            return resources.get_pixmap(*self.task_icon)

        # Parse SVG data tree
        svg_tree = Et.parse(resources.get(*self.task_icon)).getroot()

        # Change color layers
        for elem in svg_tree.findall('.//*[@id]'):
            # If element can be re-color
            if "Color" in elem.attrib["id"]:
                # Modify correct attribute
                subattr = None
                if elem.get("fill") is not None and elem.get("fill") != "none":
                    subattr = "fill"
                elif elem.get('stroke') is not None and elem.get('stroke') != "none":
                    subattr = "stroke"
                
                if subattr:
                    # Get current color in HSV (HEX > RGB > HSV)
                    color_hsv = self.rgb2hsv(*self.hex2rgb(elem.get(subattr)))

                    # Get new color hue
                    new_hue = self.rgb2hsv(*self.hex2rgb(self.task_color))[0]
                    
                    # Set new hue and convert values to 0-1 scale (for colorsys)
                    color_hsv = (new_hue/360, color_hsv[1]/100, color_hsv[2]/100)

                    # Convert HSV new color in RGB
                    new_color = tuple(round(x * 255) for x in colorsys.hsv_to_rgb(*color_hsv))

                    # Set new color in attr
                    elem.set(subattr, f'rgb{new_color}')

        # Convert data tree in str
        svg_str = Et.tostring(svg_tree, encoding='utf8', method='xml')
        
        # Encode in base64
        encoded_str = base64.b64encode(svg_str).decode('utf-8')
        svg_b64 = f'data:image/svg+xml;base64,{encoded_str}'

        # Parse base64 value to QPixmap
        ba = QtCore.QByteArray.fromBase64(bytes(svg_b64.split(',')[1], "utf-8"))
        icon_pixmap = QtGui.QPixmap()
        icon_pixmap.loadFromData(ba, svg_b64.split(';')[0].split('/')[1])

        return icon_pixmap

    def hex2rgb(self, hex_value):
        # Convert HEX color code in RGB values
        h = hex_value.strip("#") 
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        return rgb

    def rgb2hsv(self, r, g, b):
        # Normalize R, G, B values
        r, g, b = r / 255.0, g / 255.0, b / 255.0
    
        # h, s, v = hue, saturation, value
        max_rgb = max(r, g, b)    
        min_rgb = min(r, g, b)   
        difference = max_rgb - min_rgb 
    
        # if max_rgb and max_rgb are equal then h = 0
        if max_rgb == min_rgb:
            h = 0
        
        # if max_rgb==r then h is computed as follows
        elif max_rgb == r:
            h = (60 * ((g - b) / difference) + 360) % 360
    
        # if max_rgb==g then compute h as follows
        elif max_rgb == g:
            h = (60 * ((b - r) / difference) + 120) % 360
    
        # if max_rgb=b then compute h
        elif max_rgb == b:
            h = (60 * ((r - g) / difference) + 240) % 360
    
        # if max_rgb==zero then s=0
        if max_rgb == 0:
            s = 0
        else:
            s = (difference / max_rgb) * 100
    
        # compute v
        v = max_rgb * 100
        # return rounded values of H, S and V
        return tuple(map(round, (h, s, v)))

    def _on_clicked(self):
        self.page_widget.page.goto(self.task_oid)

    def _on_context_menu(self, event):
        # Show task actions by right-clicking on button
        context_menu = QtWidgets.QMenu(self)

        for action in self.page_widget.session.cmds.Flow.get_object_actions(self.task_oid):
            label = action[3]['ui']['label'] or action[3]['oid'].rsplit('/', 1)[-1].replace('_', ' ').title()
            oid = action[3]['oid']
            icon = get_icon_ref(action[3]['ui']['icon'])
            tooltip = action[3]['ui']['tooltip']

            a = context_menu.addAction(label, lambda a=oid: self._on_action_menu_triggered(a))
            a.setIcon(resources.get_icon(icon))
            a.setToolTip(tooltip)

        context_menu.exec_(self.mapToGlobal(event))

    def _on_action_menu_triggered(self, action_oid):
        self.page_widget.page.show_action_dialog(action_oid)


class TasksCustomWidget(CustomPageWidget):

    def build(self):
        self.setStyleSheet(TASK_LIST_CSS)
        self.visibility_status = False

        # Main Layout
        grid = QtWidgets.QGridLayout(self)
        grid.setContentsMargins(0,0,0,0)

        # Scroll Area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        # Scroll Area Container
        container = QtWidgets.QWidget()
        container.setObjectName('ScrollAreaContainer')
        scroll.setWidget(container)
        
        container_lo = QtWidgets.QVBoxLayout(container)
        self.task_list_lo = FlowLayout()
        self.task_list_lo.setSpacing(20)
        container_lo.addLayout(self.task_list_lo)

        self.refresh_list()
        
        # Buttons
        self.button_visibility_toggle = QtWidgets.QPushButton(
            resources.get_icon(('icons.libreflow', 'show')), ''
        )
        self.button_visibility_toggle.setToolTip('Show disabled tasks')
        self.button_visibility_toggle.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.button_visibility_toggle.setFixedWidth(40)
        self.button_visibility_toggle.clicked.connect(self._on_visibility_toggle_button_clicked)

        button_add_task = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'plus-black-symbol')), ''
        )
        button_add_task.setToolTip('Add task')
        button_add_task.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        button_add_task.setFixedWidth(40)
        button_add_task.clicked.connect(self._on_addtask_button_clicked)
        
        # Add widgets to Main Layout
        grid.addWidget(scroll, 0, 0, 1, 4)
        grid.setColumnStretch(1, 1)
        grid.addWidget(self.button_visibility_toggle, 1, 2)
        grid.addWidget(button_add_task, 1, 3)
    
    def sizeHint(self):
        return QtCore.QSize(0, 2880)
    
    def refresh_list(self):
        # Clear all existing tasks
        for i in reversed(range(self.task_list_lo.count())):
            self.task_list_lo.itemAt(i).widget().deleteLater()
        
        # Create tasks buttons
        for task_oid in self.session.cmds.Flow.get_mapped_oids(self.oid + '/tasks'):
            # Don't add disabled tasks if visibility option is not active
            enabled = bool(self.session.cmds.Flow.get_value(task_oid + "/enabled"))
            if not enabled and self.visibility_status == False:
                continue

            data = dict(
                oid=task_oid,
                name=self.session.cmds.Flow.call(task_oid, 'get_display_name', [], {}),
                enabled=enabled,
                icon=self.session.cmds.Flow.call(task_oid, 'get_icon', [], {}),
                color=self.session.cmds.Flow.call(task_oid, 'get_color', [], {})
            )
            
            b = TaskButton(self, data)
            self.task_list_lo.addWidget(b)
    
    def _on_visibility_toggle_button_clicked(self):
        # Update status
        if self.visibility_status == False:
            self.visibility_status = True
            self.button_visibility_toggle.setToolTip("Hide disabled tasks")
            self.button_visibility_toggle.setIcon(resources.get_icon(('icons.libreflow', 'hide')))
        else:
            self.visibility_status = False
            self.button_visibility_toggle.setToolTip("Show disabled tasks")
            self.button_visibility_toggle.setIcon(resources.get_icon(('icons.libreflow', 'show')))
        
        self.refresh_list()

    def _on_addtask_button_clicked(self):
        self.page.show_action_dialog(f'{self.oid}/tasks/add_task')
