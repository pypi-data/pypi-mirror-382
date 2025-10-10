
from warnings import warn

from .interface import Editor_Interface

from qtpy import QtWidgets, QtGui, QtCore


class ChoiceValueEditor(QtWidgets.QComboBox, Editor_Interface):
    '''
    This editor lets you choose one items in a choice list.

    Editor Type Names:
        choice
        choices (deprecated)

    Options:
        sorted:         bool (False) - sorts the choices
        choice_icons:   dict mapping each choice to an icon_ref
                        example: choice_icons={'Work in Progress':('icons.status', 'WIP')}
    '''
    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        if editor_type_name in ('choices',):
            warn('Editor Type Name {!r} is deprecated.'.format(editor_type_name))
        return editor_type_name in ('choice', 'choices')  # Flow1 used choices... :/

    def __init__(self, parent, options):
        QtWidgets.QComboBox.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self._sorted = False
        self._choice_icons = {}
        self.apply_options(options)

        self.activated.connect(self._on_select)

    def needs_choices(self):
        '''
        Must be overriden by editor presenting a choice of possible values.
        '''
        return True

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
        self._sorted = options.get('sorted', False)
        self._choice_icons = options.get('choice_icons', {})

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        value, choices = self.fetch_value()  # this is because needs_choices() returns True
        if self._sorted:
            choices.sort()

        self.clear()
        for i, choice in enumerate(choices):
            if choice is None:
                label = ''
            else:
                label = str(choice)

            try:
                icon_ref = self._choice_icons[choice]
            except KeyError:
                icon = self.get_icon_for(label)
            else:
                icon = self.get_icon_by_ref(icon_ref)

            if icon is not None:
                self.addItem(icon, label)
            else:
                self.addItem(label)
            if choice == value:
                self.setCurrentIndex(i)

        self._on_updated()

    def _on_select(self):
        self.apply()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        return self.currentText()

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
        self.setToolTip('/!\\ ERROR: %s' % error_message)
