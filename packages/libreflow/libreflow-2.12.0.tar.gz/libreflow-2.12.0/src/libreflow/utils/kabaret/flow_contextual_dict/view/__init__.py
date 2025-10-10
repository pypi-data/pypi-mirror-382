from kabaret.app.ui.gui.widgets.flow import FlowView
from kabaret.flow_contextual_dict.view import ContextualDictView

class DefaultContextualDictView(ContextualDictView):

    def receive_event(self, event, data):
        if (
            event == "select_changed"
            and self.isVisible()
            and self.active_view_enabled()
        ):
            # Update Navigator with the selected item
            if data["selected"] is not None:
                oid = data["selected"]["oid"]
                if oid != self.current_oid():
                    self.goto(oid)
                    return

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

            # Update Navigator with the current active view
            if self.isVisible() and self.active_view_enabled():
                view_id = data['view_id']
                if view_id == self._view_id:
                    return

                view = self.session.find_view(FlowView.view_type_name(), view_id)
                if (
                    view is None
                    or view.flow_page.current_oid() == self.current_oid()
                    or self.session.current_oid_selected() is not None
                ):
                    return

                self.goto(view.flow_page.current_oid())