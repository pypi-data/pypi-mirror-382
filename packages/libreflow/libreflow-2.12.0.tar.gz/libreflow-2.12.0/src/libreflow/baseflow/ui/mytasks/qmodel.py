from kabaret.app.ui.gui.widgets.flow.flow_view import QtWidgets, QtCore, QtGui
from ..qmodel import QFileListModel as BaseQFileListModel


class QTaskFileListModel(BaseQFileListModel):
    
    def __init__(self, task_item, parent=None):
        super(BaseQFileListModel, self).__init__()
        self.task_item = task_item
        self.session = task_item.page_widget.session

    def rowCount(self, parent=None):
        return len(self.task_item.file_data)
   
    def headerData(self, section, orientation, role):       
        return None

    def data(self, index, role):
        if role == QtCore.Qt.UserRole:
            data = self.task_item.file_data[index.row()]
            return data

    def mimeData(self, indexes):
        mime_data = super(BaseQFileListModel, self).mimeData(indexes)
        oids = [
            self.task_item.file_data[index.row()].oid()
            for index in indexes
        ]
        md = self.session.cmds.Flow.to_mime_data(oids)
        for data_type, data in md.items():
            mime_data.setData(data_type, data)

        return mime_data
