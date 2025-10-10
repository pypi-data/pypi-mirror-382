from qtpy import QtWidgets, QtCore

from .python_value import PythonValueEditor


class PasswordEditor(PythonValueEditor):
    '''
    This editor lets you enter password text value.

    Editor Type Names:
        password
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('password',)

    def __init__(self, parent, options):
        super(PasswordEditor, self).__init__(parent, options)
        self.apply_options(options)
        self.setEchoMode(QtWidgets.QLineEdit.Password)
        self.setInputMethodHints(QtCore.Qt.ImhHiddenText | QtCore.Qt.ImhNoPredictiveText | QtCore.Qt.ImhNoAutoUppercase)