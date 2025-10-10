
from warnings import warn

from .interface import Editor_Interface

from qtpy import QtWidgets, QtGui, QtCore

from ..event_filters import IgnoreMouseButton


class MultiChoiceValueEditor(QtWidgets.QListWidget, Editor_Interface):
    '''
    This editor lets you choose several items in a choice list.

    Editor Type Names:
        multichoice
        multichoices    (deprecated)
        multi_choices   (deprecated)

    Options:
        sorted:         bool (False) - sorts the choices
        default_height : int  (None)  - Force default width

    Deprecated options from previous kabaret versions:
        allow_add:  You must use child actions to provide this fonctionality
    '''
    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        if editor_type_name in ('multichoices', 'multi_choices'):
            warn('Editor Type Name {!r} is deprecated.'.format(
                editor_type_name))
        return editor_type_name in ('multichoice', 'multichoices', 'multi_choices')

    def __init__(self, parent, options):
        QtWidgets.QListWidget.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self.viewport().installEventFilter(IgnoreMouseButton(self))
        self.installEventFilter(IgnoreMouseButton(self))

        self._editable = True
        self._sorted = False
        self._default_height = None

        self.apply_options(options)

        self._current_value = []

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
        if b:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
            self.itemActivated.connect(self._on_item_activate)
            self.itemChanged.connect(self._on_item_changed)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        if 'allow_add' in options:
            raise ValueError("Obsolete option 'allow_add'")

        self._default_height = options.get('default_height')
        self._sorted = options.get('sorted', False)

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        self.blockSignals(True)
        # this is because needs_choices() returns True
        value, choices = self.fetch_value()
        self._current_value = value     # avoid copy

        self.clear()
        try:
            remaining = set(self._current_value)
        except TypeError as err:
            self._show_error(str(err))
            return

        for choice in choices or []:
            if choice is None:
                label = ''
            else:
                label = str(choice)
            item = QtWidgets.QListWidgetItem(label, self)
            item._choice = choice

            if not self._editable:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)

            if choice in self._current_value:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            icon = self.get_icon_for(label)
            if icon is not None:
                item.setIcon(icon)

            try:
                remaining.remove(choice)
            except KeyError:
                pass

        for choice in remaining:
            if choice is None:
                label = ''
            else:
                label = str(choice)
            item = QtWidgets.QListWidgetItem(label, self)
            item._choice = choice

            if not self._editable:
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)

            item.setCheckState(QtCore.Qt.Checked)

            icon = self.get_icon_for(label)
            if icon is not None:
                item.setIcon(icon)

        if self._sorted:
            self.sortItems()

        self.setMinimumSize(self.minimumSizeHint())

        self.blockSignals(False)
        self._on_updated()

    def minimumSizeHint(self):
        if self._default_height is not None:
            return QtCore.QSize(self.width(), self._default_height)

        if self.model().rowCount() == 0:
            return QtCore.QSize(self.width(), 0)

        height = (self.model().rowCount() + 0.2) * self.sizeHintForRow(0)
        return QtCore.QSize(self.sizeHintForColumn(0), min(height, 400))

    def sizeHint(self):
        if self._default_height is not None:
            return QtCore.QSize(self.width(), self._default_height)

        if self.model().rowCount() == 0:
            return QtCore.QSize(self.width(), 0)

        height = (self.model().rowCount() + 0.4) * self.sizeHintForRow(0)
        return QtCore.QSize(self.sizeHintForColumn(0), min(height, 500))

    def _on_item_activate(self, item):
        checked = item.checkState()
        if checked != QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)

    def _on_item_changed(self, item):
        if self.selectedItems():
            items = [item._choice for item in self.selectedItems()]
        else:
            items = [item._choice]

        if item.checkState() == QtCore.Qt.Checked:
            self._current_value = self._current_value + items
        else:
            for item in items:
                self._current_value.remove(item)
        self.apply()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        return self._current_value

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
        self.setToolTip(self.toolTip() + '\n' + msg)
