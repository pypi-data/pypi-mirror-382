from kabaret.subprocess_manager.views import SubprocessView


class DefaultSubprocessView(SubprocessView):
    def receive_event(self, event, data):
        super(DefaultSubprocessView, self).receive_event(event, data)
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
