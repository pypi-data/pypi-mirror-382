from __future__ import print_function

from .interface import Editor_Interface

from qtpy import QtWidgets, QtCore


class LabelEditor(QtWidgets.QLabel, Editor_Interface):
    '''
    This editor only show a static text.

    Editor Type Names:
        label

    Options:
        label:      the text to display, may be html
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        return editor_type_name == 'label'

    def __init__(self, parent, options):
        QtWidgets.QLabel.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self.forced_text = None
        self.apply_options(options)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

    def minimumSizeHint(self, *args, **kwargs):
        return super(LabelEditor, self).minimumSizeHint() * 1.1

    def sizeHint(self, *args, **kwargs):
        return super(LabelEditor, self).sizeHint() * 1.2

    def set_editable(self, b):
        pass

    def apply_options(self, options):
        self.setWordWrap(options.get("wrap", True))
        self.forced_text = options.get('text', None)

    def apply(self):
        pass

    def update(self, *args, **kwargs):
        if self.forced_text is not None:
            self.setText(self.forced_text)
        else:
            self.setText(self.fetch_value())
        self._on_updated()

    def _show_clean(self):
        pass

    def _show_error(self, error_message):
        print(error_message)
        self.setProperty('error', True)
        self.style().polish(self)
        self.setToolTip('!!! ERROR !!! {}'.format(error_message))