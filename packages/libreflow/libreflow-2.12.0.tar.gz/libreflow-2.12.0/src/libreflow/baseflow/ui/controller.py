import six
import sys
import copy
import re

from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets

from ...resources.icons import history as _
from ..task import IconSize


FILE_TYPE_NAMES = ["Inputs", "Outputs", "Works"]
COLOR_BY_STATUS = {
    "Available": "#79f7a4",
    "Requested": "#FF584D",
    "NotAvailable": "#FF584D",
}


def get_icon_ref(icon_name, resource_folder="icons.flow"):
    if isinstance(icon_name, six.string_types):
        icon_ref = (resource_folder, icon_name)
    else:
        icon_ref = icon_name

    return icon_ref


class RevisionData:
    """
    File revision data to be used by the task view.
    """

    def __init__(self, file_data, oid):
        self.file_data = file_data
        self.controller = file_data.controller
        self.session = file_data.session
        self.oid = oid
        self.name = oid.split("/")[-1]
        self.user = None
        self.comment = None
        self.date = None
        self.working_copy = None
        self.source = None
        self.links = None
        self.colors = None
        self.activate_oid = None
        self.site = None

        self.update()

    def set_links(self, links):
        self.links = links

    def set_colors(self, colors):
        self.colors = colors

    def update(self):
        properties = self.session.cmds.Flow.call(
            self.oid,
            "get_properties",
            ["user", "comment", "date", "working_copy", "source", "status", "site"],
            {},
        )
        self.user = properties["user"]
        self.comment = properties["comment"]
        self.date = properties["date"]
        self.working_copy = properties["working_copy"]
        self.source = properties["source"]
        self.status = properties["status"] or "init"
        self.site = properties["site"]
        exchange_status = self.session.cmds.Flow.call(
            self.oid, "get_sync_status", [], dict(exchange=True)
        )
        sync_status = self.session.cmds.Flow.call(self.oid, "get_sync_status", [], {})
        self.status_color = COLOR_BY_STATUS[sync_status]
        self.statutes = (
            [
                (
                    self.session.cmds.Flow.call(
                        self.oid,
                        "get_sync_status",
                        [self.controller.current_site_name],
                        {},
                    )
                    if self.controller.current_site_name != self.site
                    else "Owner"
                )
            ]
            + [exchange_status]
            + [
                (
                    self.session.cmds.Flow.call(self.oid, "get_sync_status", [name], {})
                    if name != self.site
                    else "Owner"
                )
                for name in self.controller.site_names
            ]
        )
        self.activate_oid = self.session.cmds.Flow.call(
            self.oid, "activate_oid", [], {}
        )

    def sync_status(self, index):
        return self.statutes[index]


class ActionData:
    """
    Task action data to be used by the task view.
    """

    def __init__(self, oid, ui):
        self.oid = oid
        self.icon = get_icon_ref(ui["icon"])
        self.label = ui["label"] or oid.rsplit("/", 1)[-1].replace("_", " ").title()
        self.tooltip = ui["tooltip"]


class FileData:
    """
    Task file data to be used by the task view.
    """

    def __init__(
        self, session, oid, task_name, task_data=None, goto_oid=None, activate_oid=None, ref_oid=None
    ):
        if task_data is not None:
            self.controller = task_data.controller
        self.session = session
        self.file_oid = oid
        self.task_name = task_name
        self.label = None
        self.icon = None
        self.goto_oid = goto_oid
        self.goto_source_display = None
        self.main_actions = None
        self.secondary_actions = None
        self.sources = None
        self.max_link = None
        self.max_color = None
        self.revisions_count = 0
        self.revision_oids = None
        self.revision_by_oid = None
        self.head_revision_oid = None
        self.activate_oid = activate_oid
        self.ref_oid = ref_oid
        self.is_primary_file = False
        self.file_user_status = None

        self.update(goto_oid)

    def oid(self):
        oid = self.file_oid
        if self.ref_oid is not None:
            oid = self.ref_oid
        return oid

    def update(self, goto_oid=None):
        self.label = self.session.cmds.Flow.get_value(self.file_oid + "/display_name")
        self.icon = get_icon_ref(
            self.session.cmds.Flow.call(self.file_oid, "get_icon", [], {})
        )
        self.goto_oid = goto_oid
        self.goto_source_display = self.session.cmds.Flow.call(
            goto_oid, "get_source_display", [goto_oid], {}
        )
        self.revisions_count = len(
            self.session.cmds.Flow.call(
                self.file_oid + "/history/revisions", "mapped_items", [], {}
            )
        )
        self.head_revision = self.session.cmds.Flow.call(
            self.file_oid, "get_head_revision", [], {}
        )
        self.is_primary_file = bool(
            self.session.cmds.Flow.get_value(self.file_oid + "/is_primary_file")
        )
        self.file_user_status = self.session.cmds.Flow.get_value(
            self.file_oid + "/file_user_status"
        )

        self.update_actions()

    def update_actions(self):
        mgr = self.session.cmds.Flow.call(
            "/".join(self.file_oid.split("/", 2)[:2]), "get_task_manager", [], {}
        )
        main, secondary = self.session.cmds.Flow.call(
            mgr.oid(), "get_file_priority_actions", [self.task_name, self.file_oid], {}
        )

        self.main_actions = [ActionData(a[3]["oid"], a[3]["ui"]) for a in main]
        self.secondary_actions = [
            ActionData(a[3]["oid"], a[3]["ui"]) for a in secondary
        ]

    def compute_history_data(self):
        self.revision_oids = self.session.cmds.Flow.call(
            self.file_oid, "get_revision_oids", [], {}
        )
        self.revision_by_oid = {
            oid: RevisionData(self, oid) for oid in self.revision_oids
        }
        self.update_graph()

    def revision_data(self, row):
        return self.revision_by_oid[self.revision_oids[row]]

    def ensure_revision_data(self, oid):
        # self.revision_oids = self.session.cmds.Flow.call(self.oid, 'get_revision_oids', [], {})

        if oid not in self.revision_by_oid:
            self.revision_by_oid[oid] = RevisionData(self, oid)
        else:
            self.revision_by_oid[oid].update()

        self.revision_oids = [
            r.oid for r in sorted(self.revision_by_oid.values(), key=lambda r: -r.date)
        ]
        self.update_graph()

    def update_graph(self):
        revisions = sorted(
            [self.revision_by_oid[oid] for oid in self.revision_oids],
            key=lambda r: r.date,
        )
        publications = [r for r in revisions if not r.working_copy]
        is_working_copy = [r.working_copy for r in revisions]
        source_names = [r.source or None for r in revisions]
        self.sources = {}
        links = [[-1, [], []] for i in range(len(revisions))]
        colors = [[-1, [], []] for i in range(len(revisions))]
        indices = {revisions[i].name: i for i in range(len(revisions))}
        self.max_link = 0

        # Compute input links
        # We assume that the oldest revision has no source
        k = 1
        for i in range(1, len(revisions)):
            self.sources[revisions[i].name] = source_names[i]

            if is_working_copy[i]:
                continue

            if source_names[i] is None:
                links[i][0] = -1
            elif source_names[i] == publications[k - 1].name:
                links[i][0] = 0
            else:
                links[i][0] = 1 + max(
                    [
                        links[j][0]
                        for j in range(indices[source_names[i]] + 1, i)
                        if not is_working_copy[j]
                    ],
                    default=-1,
                )
                links[i][0] += int(links[i][0] == 0)

            self.max_link = max(self.max_link, links[i][0])
            k += 1

        for i in range(0, len(revisions)):
            if is_working_copy[i]:
                self.max_link += 1

                if source_names[i] is not None:
                    links[i][0] = self.max_link

        crosslinks = []
        for i in range(len(revisions) - 1, -1, -1):
            # Compute output links
            if source_names[i] is not None:
                links[indices[source_names[i]]][1].insert(
                    0, links[i][0]
                )  # Source outputs are target inputs

            # Compute crossing links
            for outlink in links[i][1]:
                if outlink in crosslinks:
                    crosslinks.remove(outlink)

            links[i][2] = copy.deepcopy(crosslinks)

            if links[i][0] >= 0:
                crosslinks.append(links[i][0])

        # Compute colors
        progresscolors = [-1 for i in range(self.max_link + 1)]
        self.max_color = 0
        for i in range(len(revisions)):
            # Input colors
            if links[i][0] >= 0:
                colors[i][0] = progresscolors[links[i][0]]
                progresscolors[links[i][0]] = -1

            # Crossing link colors
            for l in links[i][2]:
                colors[i][2].append(progresscolors[l])

            # Output colors
            if links[i][1]:
                if links[i][0] >= 0:
                    colors[i][1].append(colors[i][0])
                    progresscolors[links[i][1][0]] = colors[i][0]
                else:
                    colors[i][1].append(self.max_color)
                    progresscolors[links[i][1][0]] = self.max_color
                    self.max_color += 1

                for j in range(1, len(links[i][1])):
                    colors[i][1].append(self.max_color)
                    progresscolors[links[i][1][j]] = self.max_color
                    self.max_color += 1

        for i in range(len(revisions)):
            revisions[i].set_links(links[i])
            revisions[i].set_colors(colors[i])

    def get_link_weights(self, selected_indexes):
        revisions = [self.revision_by_oid[oid] for oid in self.revision_oids]
        weights = [[0.45, {}, {}] for i in range(len(revisions))]
        revision_names = [r.name for r in revisions]
        visited = []

        for i in selected_indexes:
            selected = revision_names[i]
            source = self.sources.get(selected)
            selected_index = i

            while source is not None:
                weights[selected_index][0] = 1.0
                level = revisions[selected_index].links[0]
                source_index = revision_names.index(source)

                for j in range(selected_index + 1, source_index):
                    weights[j][2][level] = 1.0

                visited.append(source)
                weights[source_index][1][level] = 1.0

                selected = source
                selected_index = source_index
                source = self.sources.get(selected)

        return weights


class TaskData:
    """
    Task data to be used by the task view.
    """

    def __init__(self, controller):
        self.controller = controller
        self.session = controller.session
        self.oid = controller.oid
        self.label = self.session.cmds.Flow.call(self.oid, "get_display_name", [], {})
        self.icon = get_icon_ref(
            self.session.cmds.Flow.call(self.oid, "get_icon", [], {})
        )
        self.small_icon = get_icon_ref(
            self.session.cmds.Flow.call(self.oid, "get_icon", [IconSize.SMALL], {})
        )
        self.color = self.session.cmds.Flow.call(self.oid, "get_color", [], {})
        self.actions = None

        self.update_files()
        self.update_actions()

    def update_files(self):
        self.files = {n: [] for n in FILE_TYPE_NAMES}
        self.file_indexes = {}
        self.ref_oids = {}
        i = 0

        for oid in self.session.cmds.Flow.get_mapped_oids(self.oid + "/files"):
            _type = self.session.cmds.Flow.get_value(oid + "/file_type") or "Works"
            self.file_indexes[oid] = (_type, len(self.files[_type]))
            self.files[_type].append(self.create_file_data(oid))

        for oid in self.session.cmds.Flow.get_mapped_oids(self.oid + "/file_refs"):
            source_oid = self.session.cmds.Flow.call(oid, "get_source_oid", [], {})
            goto_oid = self.session.cmds.Flow.call(oid, "get_goto_oid", [], {})
            _type = self.session.cmds.Flow.get_value(oid + "/file_type") or "Works"
            self.file_indexes[source_oid] = (_type, len(self.files[_type]))
            self.files[_type].append(
                self.create_file_data(source_oid, goto_oid, ref_oid=oid)
            )
            self.ref_oids[oid] = source_oid
            i += 1

    def update_actions(self):
        self.actions = [
            ActionData(a[3]["oid"], a[3]["ui"])
            for a in self.session.cmds.Flow.get_object_actions(self.oid)
            if not a[3]["ui"]["hidden"]
        ]
        self.file_actions = [
            ActionData(a[3]["oid"], a[3]["ui"])
            for a in self.session.cmds.Flow.get_object_actions(self.oid + "/files")
            if not a[3]["ui"]["hidden"]
        ]

    def create_file_data(self, oid, goto_oid=None, ref_oid=None):
        activate_oid = self.session.cmds.Flow.call(oid, "activate_oid", [], {}) or None
        return FileData(
            self.session, oid, self.oid.split("/")[-1], self, goto_oid, activate_oid, ref_oid
        )

    def remove_file_data(self, oid):
        _type, index = self.file_indexes[oid]
        del self.files[_type][index]
        del self.file_indexes[oid]

    def remove_ref_data(self, oid):
        source_oid = self.ref_oids.get(oid)
        if source_oid is not None:
            self.remove_file_data(source_oid)
            del self.ref_oids[oid]

        return source_oid

    def file_data(self, oid):
        _type, row = self.file_indexes[oid]
        return self.files[_type][row]

    def update_file_type(self, oid, file_type):
        source_type, index = self.file_indexes[oid]
        fd = self.files[source_type].pop(index)

        # Update files indices of the source category
        for i, f in enumerate(self.files[source_type]):
            self.file_indexes[f.file_oid] = (source_type, i)

        # Add file to the end of the target category list
        self.file_indexes[oid] = (file_type, len(self.files[file_type]))
        self.files[file_type].append(fd)

    def ensure_file_data(self, oid):
        if oid not in self.file_indexes:
            _type = self.session.cmds.Flow.get_value(oid + "/file_type") or "Works"
            self.file_indexes[oid] = (_type, len(self.files[_type]))
            fd = self.create_file_data(oid)
            self.files[_type].append(fd)
        else:
            fd = self.file_data(oid)
            fd.update()

        return fd

    def ensure_file_data_from_ref(self, ref_oid):
        source_oid = self.session.cmds.Flow.call(ref_oid, "get_source_oid", [], {})
        goto_oid = self.session.cmds.Flow.call(ref_oid, "get_goto_oid", [], {})

        if source_oid not in self.file_indexes:
            _type = self.session.cmds.Flow.get_value(ref_oid + "/file_type") or "Works"
            self.file_indexes[source_oid] = (_type, len(self.files[_type]))
            self.files[_type].append(
                self.create_file_data(source_oid, goto_oid, ref_oid=ref_oid)
            )
        else:
            self.file_data(source_oid).update(goto_oid)

        self.ref_oids[ref_oid] = source_oid


class Controller:

    def __init__(self, task_widget):
        self.task_widget = task_widget
        self.session = task_widget.session
        self.oid = task_widget.oid
        self.cache = None
        self.selected = None
        self.selected_file_type = None
        self.selected_row = None
        self.history_selection = None
        self.link_weights = None
        self.site_names = None
        self.exchange_name = None
        self.studio_names = None
        self.current_site_name = None
        self.display_all = False

        self.display_sites = None
        self.statutes_section = None
        self.history_sections = ["History", "Revision", "User", "Comment", "Date"]

        self.site_short_names = None
        self.current_site_short_name = None
        self.exchange_short_name = None

        self.update_cache()

    def task_label(self):
        return self.cache.label

    def task_icon(self):
        return self.cache.icon

    def task_small_icon(self):
        return self.cache.small_icon

    def task_color(self):
        return self.cache.color

    def task_file_count(self, file_type):
        return len(self.cache.files[file_type])

    def task_actions(self):
        return self.cache.actions

    def task_file_actions(self):
        return self.cache.file_actions

    def file_data(self, file_type, row):
        return self.cache.files[file_type][row]

    def handle_dropped_oids(self, oids, file_type):
        valid_oids = [
            oid
            for oid in oids
            if (
                self.session.cmds.Flow.call(
                    self.oid + "/file_refs", "can_handle", [oid], {}
                )
                or oid
                in self.session.cmds.Flow.get_mapped_oids(self.oid + "/file_refs")
            )
        ]

        if not valid_oids:
            return

        self.task_widget.view.file_lists.beginResetModels()

        for oid in valid_oids:
            if oid in self.cache.file_indexes:
                source_type = self.session.cmds.Flow.get_value(oid + "/file_type")

                if source_type != file_type:  # File type change
                    self.session.cmds.Flow.set_value(oid + "/file_type", file_type)
                    self.cache.update_file_type(oid, file_type)
            elif oid in self.cache.ref_oids:
                source_type = self.session.cmds.Flow.get_value(oid + "/file_type")

                if source_type != file_type:  # Ref type change
                    self.session.cmds.Flow.set_value(oid + "/file_type", file_type)
                    source_oid = self.cache.ref_oids[oid]
                    self.cache.update_file_type(source_oid, file_type)
            else:
                ref = self.session.cmds.Flow.call(
                    self.oid + "/file_refs", "add_ref", [oid, file_type], {}
                )
                self.cache.ensure_file_data_from_ref(ref.oid())  # Create ref
                # TODO: try not to get the reference flow object itself

        self.task_widget.view.file_lists.endResetModels()
        self.task_widget.view.file_lists.updateLists()

    def handle_dropped_files(self, paths):
        action = self.session.cmds.Flow.call(
            "/" + self.oid.split("/")[1], "get_import_files", [], {}
        )
        if action is None:
            self.root().session().log_error(
                "Import Files Action is not defined on Project Settings"
            )
            return

        action.paths.set(paths)
        action.source_task.set(self.oid)

        self.show_action_dialog(action.oid())

    def create_refs(self, oids, file_type):
        valid_oids = [
            oid
            for oid in oids
            if self.session.cmds.Flow.call(
                self.oid + "/file_refs", "can_handle", [oid], {}
            )
            and oid not in self.cache.file_indexes
        ]

        if not valid_oids:
            return

        self.task_widget.view.file_lists.beginResetModel(file_type)

        for oid in valid_oids:
            ref = self.session.cmds.Flow.call(
                self.oid + "/file_refs", "add_ref", [oid, file_type], {}
            )
            self.cache.ensure_file_data_from_ref(ref.oid())

        self.task_widget.view.file_lists.endResetModel(file_type)
        self.task_widget.view.file_lists.update(file_type)

    def remove_ref(self, ref_oid, file_type):
        self.task_widget.view.file_lists.beginResetModel(file_type)
        source_oid = self.cache.remove_ref_data(ref_oid)
        self.session.cmds.Flow.call(
            self.oid + "/file_refs", "remove_ref", [source_oid], {}
        )
        self.task_widget.view.file_lists.endResetModel(file_type)
        self.task_widget.view.file_lists.update(file_type)

    def selected_file(self):
        return self.selected

    def update_selected(self, file_type=None, row=None):
        if file_type is None:
            self.task_widget.view.file_view.beginResetHistoryModel()
            self.selected.compute_history_data()
            self.task_widget.view.file_view.endResetHistoryModel()
            return

        # Clear selection of file lists of other types
        for _type in FILE_TYPE_NAMES:
            if _type != file_type:
                self.task_widget.view.file_lists.clear_list_selection(_type)

        # Invalidate history qmodel before updating cache
        self.task_widget.view.file_view.beginResetHistoryModel()
        self.selected = self.cache.files[file_type][row]
        self.selected_file_type = file_type
        self.selected_row = row

        QtWidgets.QApplication.instance().selectChanged.emit(self.selected.file_oid)

        if self.selected.revision_oids is None:
            # Display loading page before updating history: force qapplication to process last show event
            self.task_widget.view.file_view.update(loading=True)
            self.task_widget.view.file_view.show()
            QtWidgets.QApplication.processEvents()
            self.selected.compute_history_data()

        self.link_weights = [
            [0.45, {}, {}] for i in range(self.selected_file_revision_count())
        ]
        self.task_widget.view.file_view.endResetHistoryModel()

        # Show updated history
        self.task_widget.view.file_view.update(loading=False)
        self.task_widget.view.file_view.show()

    def clear_selected(self):
        # Check if an item is selected (selection already cleared or task view not yet instanciated otherwise)
        self.link_weights = None
        if self.selected is not None:
            self.task_widget.view.file_view.setVisible(False)
            self.task_widget.view.file_lists.clear_selection()

    def file_history_header(self, column):
        return self.history_sections[column]

    def file_statutes_header(self, column):
        return self.statutes_section[column]

    def selected_file_revision_count(self):
        if self.selected is not None:
            return len(self.selected.revision_oids)

        return 0

    def selected_file_revision_data(self, row):
        if self.selected is not None:
            return self.selected.revision_data(row)

        return None

    def selected_history_max_link(self):
        if self.selected is not None:
            return self.selected.max_link

        return -1

    def selected_history_max_color(self):
        if self.selected is not None:
            return self.selected.max_color

        return -1

    def update_history_link_weights(self, selected_rows):
        if self.selected is not None:
            self.link_weights = self.selected.get_link_weights(selected_rows)
            self.task_widget.view.file_view.content.history_view.update_graph()

    def revision_link_weights(self, row):
        if self.link_weights is not None:
            return self.link_weights[row]

        return None

    def selected_file_revision_status(self, row, column):
        if self.selected is not None:
            if column == 0:
                return self.selected.revision_data(row).name
            else:
                return self.selected.revision_data(row).statutes[column - 1]

        return None

    def toggle_file_statutes(self):
        if self.task_widget.view.file_view.isVisible():
            self.task_widget.view.file_view.toggle_file_statutes()

    def display_all_sites(self, checked):
        self.display_all = checked
        self.update_sites_order()
        self.update_selected()

    def update_cache(self):
        self.update_sites_order()
        self.cache = TaskData(self)

    def _is_not_complete(self, sites):
        return any(
            site not in sites
            for site in self.sites()[1:]
            if self.get_non_active_sites(site)
        )

    def update_sites_order(self):
        self.current_site_name = self.current_working_site_name()
        self.site_names = self.working_site_names()
        self.exchange_name = self.exchange_site_name()

        self.site_short_names = self.get_short_names(self.working_site_names())
        self.current_site_short_name = self.get_short_name(self.current_site_name)
        self.exchange_short_name = self.get_exchange_short_name()

        self.statutes_section = [
            "Revision",
            self.current_site_short_name,
            self.exchange_short_name,
            *self.site_short_names,
        ]

    def update_preset(self, values):
        self.session.cmds.Flow.set_value(f"{self.oid}/ordered_site_names", values)

        self.session.cmds.Flow.call(
            f"{self.oid}/ordered_site_names",
            "update_preset",
            [],
            {},
        )

    def ensure_presets(self):
        ordered_site_names = self.session.cmds.Flow.get_value(
            f"{self.oid}/ordered_site_names",
        )
        if not ordered_site_names:
            return None

        all_sites = self.sites()

        sites_map_changed = False
        for default_site in all_sites:
            if default_site == self.current_working_site_name():
                continue
            if ordered_site_names.get(default_site, None) is None:
                sites_map_changed = True
                ordered_site_names[default_site] = (
                    True
                    if self.get_working_site_type(default_site) == "Studio"
                    else False
                )

        copy = ordered_site_names.copy()
        for site in ordered_site_names:
            if site not in all_sites:
                copy.pop(site)
        ordered_site_names = copy

        if sites_map_changed:
            self.update_preset(ordered_site_names)

        return ordered_site_names

    def get_working_site_type(self, name):
        return self.session.cmds.Flow.get_value(
            "/"
            + self.oid.split("/")[1]
            + f"/admin/multisites/working_sites/{name}/site_type",
        )

    def sites(self):
        return [
            site
            for site in self.session.cmds.Flow.call(
                "/" + self.oid.split("/")[1] + "/admin/multisites/working_sites",
                "mapped_names",
                [],
                {},
            )
            if site not in ("default")
        ]

    def get_only_studios(self):
        return [
            site
            for site in self.sites()
            if self.get_working_site_type(site) == "Studio"
            if site != self.current_site_name
            if self.get_non_active_sites(site)
        ]

    def get_presets(self):
        sites = []
        for site, checked in self.ensure_presets().items():
            if checked and site != self.current_site_name:
                sites.append(site)
        return sites

    def working_site_names(self):
        if self.display_all:
            return [
                site
                for site in self.sites()
                if site not in (self.current_site_name)
                if self.get_non_active_sites(site)
            ]

        self.session.cmds.Flow.call(
            f"{self.oid}/ordered_site_names",
            "apply_preset",
            [],
            {},
        )

        ordered_site_names = self.ensure_presets()

        if not ordered_site_names:
            return [*self.get_only_studios(), "..."]

        sites = [site for site in self.get_presets() if self.get_non_active_sites(site)]
        if self._is_not_complete(sites):
            return [*sites, "..."]
        return sites

    def current_working_site_name(self):
        return self.session.cmds.Flow.get_value(
            "/" + self.oid.split("/")[1] + "/admin/multisites/current_site_name",
        )

    def exchange_site_name(self):
        return self.session.cmds.Flow.get_value(
            "/" + self.oid.split("/")[1] + "/admin/multisites/exchange_site_name"
        )

    def get_exchange_short_name(self):
        short_name = self.session.cmds.Flow.get_value(
            "/"
            + self.oid.split("/")[1]
            + f"/admin/multisites/exchange_sites/{self.exchange_site_name()}/short_name",
        )
        if short_name != "":
            return self.session.cmds.Flow.get_value(
                "/"
                + self.oid.split("/")[1]
                + f"/admin/multisites/exchange_sites/{self.exchange_site_name()}/short_name",
            )
        return self.exchange_site_name()

    def get_non_active_sites(self, name):
        return self.session.cmds.Flow.get_value(
            "/"
            + self.oid.split("/")[1]
            + f"/admin/multisites/working_sites/{name}/is_active",
        )
    
    def get_short_name(self, site):
        site_short_name = self.session.cmds.Flow.get_value(
            "/"
            + self.oid.split("/")[1]
            + f"/admin/multisites/working_sites/{site}/short_name",
        )
        if site_short_name != "":
            return site_short_name
        return site

    def get_short_names(self, sites):
        not_complete = False
        sites_list = []
        for site in sites:
            if site == "...":
                not_complete = True
                continue
            if self.get_non_active_sites(site):
                site_name = self.get_short_name(site)
                sites_list.append(
                    site_name)

        if not_complete:
            sites_list.append("...")
        return sites_list

    def site_count(self):
        return len(self.site_short_names) + 1

    def is_bookmarked(self):
        return self.session.cmds.Flow.call(
            self.oid + "/toggle_bookmark", "is_bookmarked", [], {}
        )

    def toggle_bookmark(self):
        self.session.cmds.Flow.run_action(
            oid=self.oid + "/toggle_bookmark", button="Toggle"
        )

    def show_action_dialog(self, action_oid):
        self.task_widget.page.show_action_dialog(action_oid)

    def goto(self, oid):
        self.task_widget.page.goto(oid)

    def on_touch_event(self, oid):
        import time

        start = time.time()
        m = re.match(
            "^" + self.oid + "(/files/[^/]+)?(/history/revisions/([^/]+))?$", oid
        )

        if m is None:
            # Touched object does not belong to this task
            return

        if m.group(1) is not None:
            if m.group(2) is None:
                self.task_widget.view.file_lists.beginResetModels()

            file_data = self.cache.ensure_file_data(self.oid + m.group(1))

            if m.group(2) is not None:
                if file_data.revision_oids is not None and self.session.cmds.Flow.call(
                    self.oid + m.group(1), "has_revision", [m.group(3)], {}
                ):
                    is_selected = (
                        self.selected is None
                        and self.selected.file_oid == file_data.file_oid
                    )

                    # Touched object is a revision and file history has been loaded for display at least once
                    if is_selected:
                        self.task_widget.view.file_view.beginResetHistoryModel()

                    file_data.ensure_revision_data(oid)
                    self.update_history_link_weights(
                        [
                            i.row()
                            for i in self.task_widget.view.file_view.content.history_view.selectionModel().selectedRows()
                        ]
                    )

                    if is_selected:
                        self.task_widget.view.file_view.endResetHistoryModel()
                        self.task_widget.view.file_view.update(loading=False)
            else:
                self.task_widget.view.file_lists.endResetModels()
                self.task_widget.view.file_lists.updateLists()

    # def get_file_display_name(self, file_type, row):
    #     oids = self.get_task_file_oids()
    #     # print(column)
    #     return self.cache[file_type].get(row, FileCache(self.session, oid))
    #     return self.session.cmds.Flow.get_value(oids[column]+'/display_name')

    # def get_task_file_oids(self):
    #     return self.session.cmds.Flow.get_mapped_oids(self.oid+'/files')

    # def get_file_type(self, oid):
    #     return self.session.cmds.Flow.get_value(oid+'/file_type')
