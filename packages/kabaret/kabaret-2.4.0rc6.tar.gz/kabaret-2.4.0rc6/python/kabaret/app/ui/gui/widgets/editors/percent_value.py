

from .interface import Editor_Interface

from qtpy import QtWidgets, QtCore


class PercentValueEditor(QtWidgets.QProgressBar, Editor_Interface):
    '''
    This editor display a progression

    Editor Type Names:
        percent, progression

    Options:
        minimum: float (0)
        maximum: float (100)
        display_text: bool (True) - Display also value in text or not
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('percent', 'progress', )

    def __init__(self, parent, options):
        QtWidgets.QProgressBar.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self.apply_options(options)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.setEnabled(b)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        self.setMinimum(options.get('minimum', 0))
        self.setMaximum(options.get('maximum', 100))
        self.setTextVisible(options.get('display_text', True))

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        value = float(self.fetch_value())
        self.setValue(value)
        self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        return self.value()

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        # This will not happend, the changes are directly applied.
        self.setProperty('edited', True)
        self.setProperty('applying', False)
        self.style().polish(self)

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
        self.setToolTip('!!!\nERROR: %s' % (error_message,))