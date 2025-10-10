from kabaret.app.ui.gui.widgets.flow.flow_view import (
    QtWidgets,
    QtCore,
    QtGui,
    CustomPageWidget,
)
from kabaret.app import resources

from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager


class BannerLabel(QtWidgets.QLabel):
    def __init__(self, widget):
        super(BannerLabel, self).__init__(widget)
        self.widget = widget
        self.page_widget = widget.page_widget

        self.project_name = self.page_widget.get_project_title()
        self.setText(self.project_name)
        self.thumbnail = None
        self.setMinimumSize(1, 1)
        self.setScaledContents(True)
        self.setAlignment(QtCore.Qt.AlignBottom)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )
        self.image = self.page_widget.get_banner()

    def paintEvent(self, event):
        QPainter = QtGui.QPainter()
        QPainter.begin(self)

        QPainter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        brush = QtGui.QBrush(
            QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Window)
        )
        QPainter.setBrush(brush)

        path = QtGui.QPainterPath()
        path.addRoundedRect(self.rect(), 10, 10)

        pen = QtGui.QPen(
            QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Dark)
        )
        pen.setWidth(10)

        QPainter.setPen(pen)
        QPainter.setClipPath(path)

        QPainter.fillPath(path, QPainter.brush())

        if self.thumbnail:
            x = self.rect().center().x() - (self.thumbnail.size().width() / 2)
            y = self.rect().center().y() - (self.thumbnail.size().height() / 2)
            QPainter.drawPixmap(x, y, self.thumbnail)

        QPainter.strokePath(path, QPainter.pen())

        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(30)
        QPainter.setFont(font)
        pen = QtGui.QPen("#FDFDFD")
        QPainter.setPen(pen)
        QPainter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.project_name)
        QPainter.end()

    def resizeEvent(self, event):
        if self.image:
            ba = QtCore.QByteArray.fromBase64(bytes(self.image.split(",")[1], "utf-8"))
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(ba, self.image.split(";")[0].split("/")[1])
            pixmap = pixmap.scaledToWidth(self.width(), QtCore.Qt.SmoothTransformation)
            self.thumbnail = pixmap
        super(BannerLabel, self).resizeEvent(event)


class BannerWidget(QtWidgets.QWidget):
    def __init__(self, content):
        super(BannerWidget, self).__init__(content)
        self.content = content
        self.page_widget = content.page_widget
        self.user = self.page_widget.get_user()

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )

        self.setStyleSheet("""
                    #UserWidget {
                        padding: 5px;
                        margin: 0px 25px 0px 25px;
                        max-height: 20px;
                        background-color: palette(button);
                        border-radius: 0px;
                        border-bottom-left-radius: 10px;
                        border-bottom-right-radius: 10px;}
                    QPushButton { border: transparent; }
                    QPushButton:hover { background-color: palette(highlight); }
                    QPushButton::menu-indicator{width:0px;}
                    """)

        self.build()

    def build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        lo.setAlignment(QtCore.Qt.AlignBottom)

        self.banner_label = BannerLabel(self)

        self.user_widget = QtWidgets.QWidget(self)
        self.user_widget.setObjectName("UserWidget")
        self.user_widget.sizePolicy().setVerticalPolicy(
            QtWidgets.QSizePolicy.Policy.Fixed
        )

        user_icon = QtWidgets.QLabel()
        user_icon.setPixmap(
            resources.get_icon(("icons.gui", "user")).pixmap(QtCore.QSize(16, 16))
        )

        bookmarks_action = QtGui.QAction("Bookmarks", self)
        bookmarks_action.triggered.connect(self._on_bookmarks_action_triggered)

        admin_action = QtGui.QAction("Admin", self)
        admin_action.triggered.connect(self._on_admin_action_triggered)

        log_out_action = QtGui.QAction("Log out", self)
        log_out_action.triggered.connect(self._on_log_out_action_triggered)

        user_menu_button = QtWidgets.QPushButton()
        user_menu_button.setIcon(resources.get_icon(("icons.gui", "menu_dots")))
        self.user_menu = QtWidgets.QMenu()
        self.user_menu.addAction(bookmarks_action)
        if self.page_widget.is_admin(self.user.name()):
            self.user_menu.addAction(admin_action)
        self.user_menu.addAction(log_out_action)
        user_menu_button.setMenu(self.user_menu)

        ulo = QtWidgets.QHBoxLayout(self.user_widget)
        ulo.setSpacing(4)
        ulo.addWidget(user_icon)
        ulo.addWidget(QtWidgets.QLabel(self.user.name()))
        ulo.addStretch()
        ulo.addWidget(user_menu_button)
        ulo.setContentsMargins(35, 0, 35, 0)

        lo.addWidget(self.banner_label)
        lo.addWidget(self.user_widget)

    def _on_admin_action_triggered(self):
        self.page_widget.page.goto(f"{self.page_widget.oid}/admin")

    def _on_log_out_action_triggered(self):
        self.page_widget.page.show_action_dialog(
            f"{self.page_widget.oid}/log_out_action"
        )

    def _on_bookmarks_action_triggered(self):
        self.page_widget.page.goto(f"{self.page_widget.oid}/user")


class SyncWidget(QtWidgets.QWidget):
    def __init__(self, content):
        super(SyncWidget, self).__init__(content)
        self.content = content
        self.page_widget = content.page_widget
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self.actions = self.page_widget.session.cmds.Flow.get_object_actions(
            f"{self.page_widget.oid}/synchronization"
        )

        self.build()

    def build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)

        title_widget = QtWidgets.QLabel("Synchronisation")
        title_widget.setObjectName("TitleWidget")

        jobs_waiting_label = QtWidgets.QLabel()
        sync_summary = self.page_widget.session.cmds.Flow.get_summary(
            f"{self.page_widget.oid}/synchronization"
        )
        jobs_waiting_label.setText(sync_summary)

        slo = QtWidgets.QHBoxLayout()
        slo.setContentsMargins(15, 0, 15, 5)
        slo.addWidget(jobs_waiting_label)
        slo.addStretch()

        for action in self.actions:
            label = (
                action[3]["ui"]["label"]
                or action[3]["oid"].rsplit("/", 1)[-1].replace("_", " ").title()
            )
            oid = action[3]["oid"]
            icon = action[3]["ui"]["icon"]
            tooltip = action[3]["ui"]["tooltip"]
            hidden = action[3]["ui"]["hidden"]

            if not hidden:
                button = QtWidgets.QPushButton(f" {label}")
                button.setIcon(resources.get_icon(icon))
                button.setToolTip(tooltip)
                button.clicked.connect(
                    lambda checked=False, x=oid: self.on_button_clicked(x)
                )

                slo.addWidget(button)

        lo.addWidget(title_widget)
        lo.setAlignment(title_widget, QtCore.Qt.AlignTop)
        lo.addLayout(slo)
        lo.setAlignment(slo, QtCore.Qt.AlignTop)

    def on_button_clicked(self, oid):
        self.page_widget.page.show_action_dialog(oid)


class ListItem(QtWidgets.QListWidgetItem):
    def __init__(self, list_widget, item):
        super(ListItem, self).__init__(list_widget)
        self.content = list_widget.content
        self.page_widget = list_widget.page_widget

        self.oid = item[0]
        self.icon_ref = item[1]["_style"]["icon"]

        size = QtCore.QSize(0, 25)
        self.setSizeHint(size)
        self.setData(QtCore.Qt.UserRole, self.oid)
        self.setText(item[1]["Name"])
        self.setIcon(resources.get_icon(self.icon_ref))


class HPList(QtWidgets.QListWidget):
    def __init__(self, widget, oid):
        super(HPList, self).__init__(widget)
        self.content = widget.content
        self.page_widget = widget.page_widget
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.oid = oid

        self.itemDoubleClicked.connect(self.on_item_doubleclicked)

        self.action_manager = ObjectActionMenuManager(
            self.page_widget.session,
            self.page_widget.page.show_action_dialog,
            "Flow.map",
        )

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu_requested)

        self.build()
        self.installEventFilter(self)

    def build(self):
        map_oid = self.oid
        mapped_items = self.page_widget.session.cmds.Flow.get_mapped_rows(map_oid)

        for mapped_item in mapped_items:
            item = ListItem(self, mapped_item)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.Hide:
            # Reset selection when the widget is hidden
            QtWidgets.QApplication.instance().selectChanged.emit(None)
            return True
        
        return super().eventFilter(source, event)

    def selectionChanged(self, selected, deselected):
        if selected.indexes():
            index = selected.indexes()[0]
            QtWidgets.QApplication.instance().selectChanged.emit(
                index.data(QtCore.Qt.UserRole)
            )
        else:
            QtWidgets.QApplication.instance().selectChanged.emit(None)
            self.content.setFocus()

    def mousePressEvent(self, event):
        super(HPList, self).mousePressEvent(event)

        if event.button() == QtCore.Qt.LeftButton:
            index = self.indexAt(event.pos())
            if not index.isValid():
                QtWidgets.QApplication.instance().selectChanged.emit(None)
            else:
                QtWidgets.QApplication.instance().selectChanged.emit(
                    index.data(QtCore.Qt.UserRole)
                )

    def on_item_doubleclicked(self, item):
        self.page_widget.page.goto(item.oid)

    def _on_context_menu_requested(self, pos):
        action_menu = QtWidgets.QMenu(self)

        index = self.indexAt(pos)

        if not index.isValid():
            return

        item = self.itemAt(pos)

        has_actions = self.action_manager.update_oid_menu(
            item.oid, action_menu, with_submenus=True
        )

        if has_actions:
            action_menu.exec_(self.viewport().mapToGlobal(pos))


class HPListWidget(QtWidgets.QWidget):
    def __init__(self, content, oid, label):
        super(HPListWidget, self).__init__(content)
        self.content = content
        self.page_widget = content.page_widget
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.oid = oid
        self.label = label

        self.actions = self.page_widget.session.cmds.Flow.get_object_actions(
            self.oid, ".inline"
        )

        self.setStyleSheet("""
                    QPushButton { border: transparent }
                    QPushButton:hover { background-color: palette(highlight) }
                    QListWidget {background-color: transparent;
                                padding : 0px 10px;
                                border: transparent}
                    """)

        self.build()

    def build(self):
        lo = QtWidgets.QVBoxLayout(self)
        lo.setContentsMargins(0, 0, 0, 0)

        title_widget = QtWidgets.QWidget()
        title_widget.setObjectName("TitleWidget")

        self.hp_list = HPList(self, self.oid)

        tlo = QtWidgets.QHBoxLayout(title_widget)
        tlo.setContentsMargins(10, 0, 10, 0)
        tlo.addWidget(QtWidgets.QLabel(self.label))
        tlo.addStretch()
        tlo.setSpacing(0)

        for action in self.actions:
            label = (
                action[3]["ui"]["label"]
                or action[3]["oid"].rsplit("/", 1)[-1].replace("_", " ").title()
            )
            oid = action[3]["oid"]
            icon = action[3]["ui"]["icon"]
            tooltip = action[3]["ui"]["tooltip"]
            hidden = action[3]["ui"]["hidden"]

            if not hidden:
                button = QtWidgets.QPushButton()
                button.setIcon(resources.get_icon(icon))
                button.setToolTip(tooltip)
                button.clicked.connect(
                    lambda checked=False, x=oid: self.on_button_clicked(x)
                )

                tlo.addWidget(button)

        lo.addWidget(title_widget)
        lo.addWidget(self.hp_list)

    def on_button_clicked(self, oid):
        self.page_widget.page.show_action_dialog(oid)


class HomepageContent(QtWidgets.QWidget):
    def __init__(self, page_widget):
        super(HomepageContent, self).__init__(page_widget)
        self.setObjectName("HomepageContent")
        self.page_widget = page_widget

        self.children = self.page_widget.session.cmds.Flow.ls(self.page_widget.oid)[0]

        self.maps = [
            child for child in self.children if child[4] and not child[5]["hidden"]
        ]

        self.actions = [
            child for child in self.children if child[3] and not child[5]["hidden"]
        ]

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
                            #HomepageContent { 
                                background-color: palette(dark); 
                                border-radius: 15px; }
                            #HomepageContent > QWidget {
                                border: 2px solid palette(mid);
                                background-color: palette(window);
                                border-radius: 10px; }
                            #TitleWidget {
                                border: 2px solid palette(mid);
                                padding: 5px;
                                min-height: 25px;
                                max-height: 25px;
                                background-color: palette(button);
                                border-radius: 0px;
                                border-top-left-radius: 10px;
                                border-top-right-radius: 10px;}
                            #HomepageContent QPushButton {
                                background-color: palette(button);
                                border: 2px solid palette(mid);
                                border-radius: 7px;}
                            #HomepageContent QPushButton:hover {
                                border: 1px solid palette(highlight);
                                }
                            #HomepageContent QPushButton:pressed {
                                background-color: palette(highlight);
                                }
                            QListWidget::item:selected {
                                background-color: palette(highlight);
                                color: white;
                            }
                            """)

        self.build()

    def build(self):
        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(4, 4, 4, 4)
        vlo.setAlignment(QtCore.Qt.AlignBottom)

        self.banner = BannerWidget(self)
        self.sync = SyncWidget(self)

        glo = QtWidgets.QGridLayout()
        glo.addWidget(self.sync, 0, 0, 1, 2)

        # Dynamically add maps
        r = 1
        c = 0
        cs = 1
        for i, _map in enumerate(self.maps):
            if i == len(self.maps) - 1 and i % 2 == 0:
                cs = 2
            label = (
                _map[5]["label"] or _map[0].rsplit("/", 1)[-1].replace("_", " ").title()
            )
            widget = HPListWidget(self, _map[0], label)
            glo.addWidget(widget, r, c, 1, cs)
            if i % 2 != 0:
                c = 0
                r += 1
            else:
                c += 1

        r += 1
        c = 0

        # Dynamically add actions
        for i, action in enumerate(self.actions):
            if action[1] not in ["log_out_action", "goto_my_tasks"]:
                label = (
                    action[5]["label"]
                    or action[0].rsplit("/", 1)[-1].replace("_", " ").title()
                )
                oid = action[0]
                icon = action[5]["icon"]
                tooltip = action[5]["tooltip"]

                button = QtWidgets.QPushButton(label)
                button.setIcon(resources.get_icon(icon))
                button.setToolTip(tooltip)
                button.clicked.connect(
                    lambda checked=False, x=oid: self.on_button_clicked(x)
                )

                glo.addWidget(button, r, c)
                if i % 2 != 0:
                    c = 0
                    r += 1
                else:
                    c += 1

        glo.setContentsMargins(10, 10, 10, 10)
        glo.setSpacing(15)
        glo.setRowStretch(0, 1)
        glo.setRowStretch(1, 4)

        vlo.addWidget(self.banner)
        vlo.addLayout(glo)
        vlo.setStretchFactor(self.banner, 1)
        vlo.setStretchFactor(glo, 3)
        vlo.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vlo)

    def on_button_clicked(self, oid):
        self.page_widget.page.show_action_dialog(oid)


class HomepageWidget(CustomPageWidget):
    def build(self):
        self.content = HomepageContent(self)
        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(0, 0, 0, 0)
        # vlo.setSpacing(2)
        vlo.addWidget(self.content)

    def get_user(self):
        return self.session.cmds.Flow.call(self.oid, "get_user", {}, {})

    def is_admin(self, user):
        return self.session.cmds.Flow.call(self.oid, "is_admin", {user}, {})

    def get_banner(self):
        return self.session.cmds.Flow.call(self.oid, "get_project_thumbnail2", {}, {})

    def get_project_title(self):
        settings = self.session.cmds.Flow.call(self.oid, "settings", {}, {})

        if settings.show_project_name.get():
            return settings.project_nice_name.get()
        else:
            return None
