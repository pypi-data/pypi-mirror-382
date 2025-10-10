from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui
from kabaret.app import resources


class QFileListModel(QtCore.QAbstractTableModel):
    
    def __init__(self, controller, file_type, parent=None):
        super(QFileListModel, self).__init__(parent)
        self.controller = controller
        self.session = controller.session
        self.file_type = file_type

    def rowCount(self, parent=None):
        return self.controller.task_file_count(self.file_type)
        # return 12

    def columnCount(self, parent=None):
        return 1
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.file_type
        
        return None

    def data(self, index, role):
        # name = self.controller.file_display_name(index.column())
        if role == QtCore.Qt.UserRole:
            data = self.controller.file_data(self.file_type, index.row())
            # print(index.row(), role)
            return data
            # return 'file.txt'
    
    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction
    
    def mimeData(self, indexes):
        mime_data = super(QFileListModel, self).mimeData(indexes)
        oids = [
            self.controller.file_data(self.file_type, index.row()).oid()
            for index in indexes
        ]
        md = self.session.cmds.Flow.to_mime_data(oids)
        for data_type, data in md.items():
            mime_data.setData(data_type, data)

        return mime_data
    
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled


class QFileHistoryModel(QtCore.QAbstractTableModel):

    def __init__(self, controller, parent=None):
        super(QFileHistoryModel, self).__init__(parent)
        self.controller = controller
    
    def rowCount(self, parent=None):
        return self.controller.selected_file_revision_count()

    def columnCount(self, parent=None):
        return 5
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.controller.file_history_header(section)
        
        return None

    def data(self, index, role):
        if role == QtCore.Qt.UserRole:
            data = self.controller.selected_file_revision_data(
                index.row()
            )
            max_link = self.controller.selected_history_max_link()
            max_color = self.controller.selected_history_max_color()
            link_weights = self.controller.revision_link_weights(index.row())

            return data, max_link, max_color, link_weights
    
    # def dataChanged(self, topLeft, bottomRight, roles):
    #     print('data changed')
    #     super(QFileListModel, self).dataChanged(topLeft, bottomRight, roles)
    
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class QFileStatutesModel(QtCore.QAbstractTableModel):

    def __init__(self, controller, parent=None):
        super(QFileStatutesModel, self).__init__(parent)
        self.controller = controller

    def rowCount(self, parent=None):
        return self.controller.selected_file_revision_count()

    def columnCount(self, parent=None):
        return self.controller.site_count() + 2

    def headerData(self, section, orientation, role):
        header_name = [
            "Revision",
            self.controller.current_site_name,
            self.controller.exchange_site_name,
            *self.controller.site_names,
        ]
        home = QtGui.QIcon(resources.get_icon(("icons.gui", "home")))
        user = QtGui.QIcon(resources.get_icon(("icons.gui", "user")))

        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self.controller.file_statutes_header(section)
            if role == QtCore.Qt.DecorationRole:
                if section not in (0,1,2) and header_name[section] != "...":
                    if self.controller.get_working_site_type(header_name[section]) == "Studio":
                        return home
                    return user
                if section == 1:
                    if (
                        self.controller.get_working_site_type(
                            self.controller.current_site_name
                        )
                        == "Studio"
                    ):
                        return home
                    return user

        return super().headerData(section, orientation, role)

    def data(self, index, role):
        if role == QtCore.Qt.UserRole:
            # data = self.controller.selected_file_revision_status(
            #     index.row(), index.column(),
            # )
            return self.controller.selected_file_revision_data(
                index.row(),
            )
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
