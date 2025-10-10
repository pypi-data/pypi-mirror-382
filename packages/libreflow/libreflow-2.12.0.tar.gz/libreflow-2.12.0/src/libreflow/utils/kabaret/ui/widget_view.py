from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets
from kabaret.app.ui.gui.widgets.widget_view import DockedView


class DefaultDockedView(DockedView):

    def __init__(self, session, view_id=None, hidden=False, area=None):
        try:
            parent = session.main_window_manager.main_window
        except AttributeError:
            raise TypeError(
                'The "%s" view cannont be used in a session without a main_window'%(
                    self.__class__.__name__
                )
            )
        ViewMixin.__init__(self, session, view_id)
        QtWidgets.QWidget.__init__(self, None)

        self._main_window_manager = session.main_window_manager

        # Menu
        self.view_menu = QtWidgets.QMenu(self.view_title())

        # Tools
        self._header_tools = {}
        self._header_tools_layout = QtWidgets.QHBoxLayout()

        content_widget = QtWidgets.QWidget(self)

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        self.setLayout(lo)

        hlo = QtWidgets.QHBoxLayout()
        hlo.setContentsMargins(0, 0, 0, 0)
        header_widgets_layout = QtWidgets.QHBoxLayout()
        hlo.addStretch()
        hlo.addLayout(header_widgets_layout, 100)
        hlo.addLayout(self._header_tools_layout)
        lo.addLayout(hlo)
        top_layout = QtWidgets.QHBoxLayout()
        lo.addLayout(top_layout)
        lo.addWidget(content_widget, 100)
        self._build(
            self, top_layout, content_widget,
            self, header_widgets_layout
        )

        self._update_menus()

        dock = self._main_window_manager.create_docked_view_dock(self, hidden=hidden, area=area)

        # This is needed for layout state
        # Multi instance view types must use another policy
        dock.setObjectName(self.view_id())