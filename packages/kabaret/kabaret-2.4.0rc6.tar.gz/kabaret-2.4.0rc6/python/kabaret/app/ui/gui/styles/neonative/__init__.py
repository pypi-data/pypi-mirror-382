

import os

from qtpy import QtWidgets

from .. import Style


class NeonativeStyle(Style):

    def __init__(self):
        super(NeonativeStyle, self).__init__('Neonative')

    def apply(self, widget):
        app = QtWidgets.QApplication.instance()

        # --- No palette setup for neo-native style

        # --- Load and apply the css

        this_folder = os.path.dirname(__file__)
        css_file = os.path.join(this_folder, 'neonative_style.css')
        with open(css_file, 'r') as r:
            css = r.read()
        widget.setStyleSheet(css)


