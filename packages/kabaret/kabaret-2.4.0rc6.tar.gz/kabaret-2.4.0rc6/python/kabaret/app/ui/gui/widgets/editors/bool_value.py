

from .interface import Editor_Interface

from qtpy import QtWidgets, QtCore


class BoolValueEditor(QtWidgets.QCheckBox, Editor_Interface):
    '''
    This editor lets you choose True or False, optionaly displaying
    a corresponding label.

    Editor Type Names:
        bool

    Options:
        true_text:  str ('Yes') - Label when value is True
        false_text:  str ('No') - Label when value is False
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('bool', )

    def __init__(self, parent, options):
        QtWidgets.QCheckBox.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self.apply_options(options)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.setEnabled(b)
        if b:
            self.stateChanged.connect(self._on_state_changed)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        self._true_text = options.get('true_text', '')
        self._false_text = options.get('false_text', '')

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        value = bool(self.fetch_value())
        # Avoid this and that or thut here since QtCore.Qt.Unchecked or
        # self._false_text may evaluate to False...
        state, text = {
            True: (QtCore.Qt.Checked, self._true_text),
            False: (QtCore.Qt.Unchecked, self._false_text),
        }[value]
        self.setCheckState(state)
        self.setText(text)
        self._on_updated()

    def _on_state_changed(self, new_state):
        self.apply()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        value = bool(self.checkState() == QtCore.Qt.Checked)
        return value

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        # This will not happend, the changes are directly applied.
        self.setProperty('edited', True)
        self.setProperty('applying', False)
        self.style().polish(self)
        self.setText('Edited...')

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        self.setProperty('applying', True)
        self.setText('Applying...')

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is 
        up to date.
        '''
        self.setProperty('edited', False)
        self.setProperty('applying', False)
        self.style().polish(self)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self.setProperty('error', True)
        self.style().polish(self)
        msg = '/!\\ ERROR: ' + error_message
        self._true_text += msg
        self._false_text += msg
        self.setText(msg)
