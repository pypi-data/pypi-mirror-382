from .interface import Editor_Interface

from six import text_type as unicode

from qtpy import QtWidgets, QtCore


class PythonValueEditor(QtWidgets.QLineEdit, Editor_Interface):
    '''
    This editor lets you enter any value as its python representation.

    Editor Type Names:
        N/A     all value can be represented by this editor.

    Options:
        placeholder:  str - string displayed when the editor is empty
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return True     # This editor is the universal fallback

    def __init__(self, parent, options):
        QtWidgets.QLineEdit.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self.apply_options(options)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.setReadOnly(not b)
        if b:
            self.textEdited.connect(self._on_edited)
            self.returnPressed.connect(self.apply)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        self.setPlaceholderText(options.get("placeholder"))

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        self.setText(unicode(self.fetch_value()))
        self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        value = self.text()
        if not value.isalpha():     # to avoid python keywords
            try:
                value = eval(value)
            except Exception:
                pass
        return value

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
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
        self.setToolTip('!!!\nERROR: %s' % (error_message,))

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if len(urls) == 1 and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if len(urls) == 1 and urls[0].scheme() == 'file':
            event.acceptProposedAction()
            cursor_pos = self.cursorPositionAt(event.pos())
            self.setCursorPosition(cursor_pos)

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if len(urls) == 1 and urls[0].scheme() == 'file':
            filepath = str(urls[0].toLocalFile())#[1:]
            self.insert(filepath)
            self._on_edited()

