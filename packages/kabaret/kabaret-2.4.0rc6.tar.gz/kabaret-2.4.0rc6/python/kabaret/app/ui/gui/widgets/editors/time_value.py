import time

from .interface import Editor_Interface

from qtpy import QtWidgets, QtCore


class NoWheelDateTimeEdit(QtWidgets.QDateTimeEdit):

    def wheelEvent(self, *args, **kwargs):
        event = args[0]
        event.ignore()

class DateTimeValueEditor(QtWidgets.QWidget, Editor_Interface):
    '''
    This editor lets you enter any value as its python representation.

    Editor Type Names:
        N/A     all value can be represented by this editor.

    Options:
        format: str(MM/dd/yy HH:mm:ss) - \
         Display format see http://doc.qt.io/qt-5/qdatetimeedit.html#displayFormat-prop
        minimum:    seconds since epoch - minimum valid date
        maximum:    seconds since epoch - maximum valid date
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('timestamp', 'datetime', )

    def __init__(self, parent, options):
        QtWidgets.QWidget.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self._layout = QtWidgets.QHBoxLayout()
        self.setLayout(self._layout)

        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)

        self.time_editor = NoWheelDateTimeEdit(self)
        self.calendar = QtWidgets.QCalendarWidget()
        self.calendar.activated.connect(self.calendar_activated)
        self._open_canlendar_btn = QtWidgets.QPushButton(self)
        self._open_canlendar_btn.setText("...")
        self._open_canlendar_btn.clicked.connect(self.calendar.show)
        self._layout.addWidget(self.time_editor, 90)
        self._layout.addWidget(self._open_canlendar_btn, 10)
        self.apply_options(options)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.time_editor.setReadOnly(not b)
        self._open_canlendar_btn.setEnabled(b)
        if b:
            self.time_editor.dateTimeChanged.connect(self._on_edited)

    def focusOutEvent(self, *args, **kwargs):
        if self.is_edited():
            super(DateTimeValueEditor, self).focusOutEvent(*args, **kwargs)
            self.apply()

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        self.time_editor.setDisplayFormat(options.get("format", "yyyy/MM/dd/ HH:mm:ss"))
        date = QtCore.QDateTime()
        date.setMSecsSinceEpoch(int(options.get("minimum", 0)*1000))
        self.time_editor.setMinimumDate(date.date())
        self.calendar.setMinimumDate(date.date())
        date.setMSecsSinceEpoch(int(options.get("maximum",
                                                time.mktime(time.strptime("31/12/2150", "%d/%m/%Y")))*1000))
        self.time_editor.setMaximumDate(date.date())
        self.calendar.setMaximumDate(date.date())

    def calendar_activated(self, date):
        self.time_editor.setDate(date)
        self.calendar.close()
        self.apply()

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        The value is stored in seconds
        '''
        try:
            date = QtCore.QDateTime()
            date.setMSecsSinceEpoch(int(self.fetch_value()*1000))
            self.time_editor.setDateTime(date)
        except Exception as e:
            self.show_exception(e)
        else:
            self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        The value is stored in seconds
        '''
        value = float(self.time_editor.dateTime().toMSecsSinceEpoch()) * 0.001
        return value

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        self.time_editor.setProperty('edited', True)
        self.time_editor.setProperty('applying', False)
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
        self.time_editor.setProperty('applying', True)

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is
        up to date.
        '''
        self.time_editor.setProperty('edited', False)
        self.time_editor.setProperty('applying', False)
        self.style().polish(self)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self.time_editor.setProperty('error', True)
        self.style().polish(self)
        self.setToolTip('!!!\nERROR: %s' % (error_message,))


class DateValueEditor(DateTimeValueEditor):

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('date', )

    def apply_options(self, options):
        super(DateValueEditor, self).apply_options(options)
        format = options.get("format", "yyyy/MM/dd/").replace('m','').replace('s','').replace('H','')
        self.time_editor.setDisplayFormat(format)
