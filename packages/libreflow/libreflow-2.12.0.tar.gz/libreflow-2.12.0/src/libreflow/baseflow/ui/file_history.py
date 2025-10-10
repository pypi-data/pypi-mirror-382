from PySide6 import QtCharts


class HistoryGraph(QtCharts.QChart):
    
    def __init__(self, parent=None):
        super(HistoryGraph, self).__init__(parent)

        series = QtCharts.QLineSeries()
        series.append(2, 0)
        series.append(0, 1)
        series.append(0, 2)
        series.append(2, 3)
        self.addSeries(series)
        series = QtCharts.QLineSeries()
        series.append(2, 0)
        series.append(1, 1)
        series.append(1, 3)
        series.append(2, 4)
        self.addSeries(series)
        # self.createDefaultAxes()
        self.legend().hide()
        self.setBackgroundVisible(False)
