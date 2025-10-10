import os

from qtpy import QtCore, QtGui, QtWidgets

from kabaret.app import resources
from kabaret.app.ui.gui.styles import Style
from libreflow.resources import fonts

class LfsTechStyle(Style):
    """
    You can customize this style by modifying QSettings() (colors/*)
    """

    def __init__(self, name=None):
        super(LfsTechStyle, self).__init__(name or 'LfsTechStyle')

    def apply(self, widget=None):
        widget = widget or QtWidgets.QApplication.instance()

        app = QtWidgets.QApplication.instance()

        # --- Stuff we could not deal with only using css:

        self.set_property('alternate_child_color', False)

        # --- Change palette only for app wide apply:

        if widget is app:
            widget = widget or QtWidgets.QApplication.instance()

            settings = QtCore.QSettings()
            settings.beginGroup('colors')

            # setup the palette
            palette = QtWidgets.QApplication.palette()
            # A color to indicate a selected item or the current item. By default, the highlight color is Qt.darkBlue.
            palette.setColor(QtGui.QPalette.Highlight, settings.value('highlight', QtGui.QColor("#179066")))
            palette.setColor(QtGui.QPalette.HighlightedText, settings.value('highlighted_text', QtGui.QColor("#42314a")))
            palette.setColor(QtGui.QPalette.WindowText, settings.value('window_text', QtGui.QColor("#dcdbd6")))
            palette.setColor(QtGui.QPalette.Link, settings.value('link', QtGui.QColor("#b9c2c8")))
            palette.setColor(QtGui.QPalette.Window, settings.value('window', QtGui.QColor("#585b5d")))
            palette.setColor(QtGui.QPalette.Text, settings.value('text', QtGui.QColor("#a7b0b4")))
            palette.setColor(QtGui.QPalette.Base, settings.value('base', QtGui.QColor("#2b2b2b")))
            palette.setColor(QtGui.QPalette.Dark, settings.value('dark', QtGui.QColor("#22222b")))
            palette.setColor(QtGui.QPalette.Light, settings.value('light', QtGui.QColor("#838283")))
            palette.setColor(QtGui.QPalette.Midlight, settings.value('midlight', QtGui.QColor("#911f36")))
            palette.setColor(QtGui.QPalette.Mid, settings.value('mid', QtGui.QColor("#353b3d")))
            palette.setColor(QtGui.QPalette.Button, settings.value('button', QtGui.QColor("#4c5052")))
            palette.setColor(QtGui.QPalette.ButtonText, settings.value('button_text', QtGui.QColor("#dcdbd6")))

            settings.endGroup()

            widget.setPalette(palette)

        # --- Load and apply the css
        this_folder = os.path.dirname(__file__)
        css_file = os.path.join(this_folder, 'lfs_tech_style.css')
        with open(css_file, 'r') as r:
            self.apply_css(widget, r.read())
        
        # --- Load font
        fonts_dir = os.path.dirname(fonts.__file__)

        fontLoaded = False
        for f in os.listdir(fonts_dir):
            if f.endswith(".ttf"):
                QtGui.QFontDatabase.addApplicationFont(os.path.join(fonts_dir, f))
                if fontLoaded is False:
                    fontLoaded = True

        if fontLoaded:
            font = QtGui.QFont('Space Grotesk', 10)
            font.setStyleStrategy(QtGui.QFont.PreferAntialias)
            font.setHintingPreference(QtGui.QFont.HintingPreference.PreferNoHinting)

            app.setFont(font)
