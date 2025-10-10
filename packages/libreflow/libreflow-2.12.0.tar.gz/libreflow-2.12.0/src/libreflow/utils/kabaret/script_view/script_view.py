from kabaret.app import plugin
from kabaret.script_view.script_view import ScriptView


class DefaultScriptView(ScriptView):
    def receive_event(self, event, data):
        if self._show_events and self.output is not None:
            self.output._std_capture.write("[EVENT: %s] %r\n" % (event, data))

        if event == "focus_changed":
            # Update dock title bar background color depending on the active view status
            view_id = data["view_id"]

            titlebar = self.dock_widget().titleBarWidget()
            if not titlebar:
                return

            dock_background = titlebar.get_container()
            dock_background.setProperty(
                "current", True if view_id == self.view_id() else False
            )

            dock_background.style().polish(dock_background)
            dock_background.update()


class DefaultScriptViewPlugin:
    @plugin(trylast=True)
    def install_views(session):
        if not session.is_gui():
            return

        from qtpy import QtCore

        type_name = session.register_view_type(DefaultScriptView)
        session.add_view(type_name, hidden=True, area=QtCore.Qt.RightDockWidgetArea)