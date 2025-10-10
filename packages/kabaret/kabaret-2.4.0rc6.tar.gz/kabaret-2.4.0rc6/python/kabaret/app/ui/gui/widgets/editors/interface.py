'''


'''


class Editor_Interface(object):
    '''
    This editor interface which define available behaviors for all kabaret editors

    Function:
        can_edit:           return True if the editor can handle the editor type
        needs_choices:      return True if the editor can accept only value among a choices list
        set_editable:       configure the editor according to the 'editable' property
        apply_options:      configure the editor according to ui configuration (dict of property)
        update:             update the editor value according to the getter (using fetch_value)
        get_edited_value:   return the editor value formatted for the setter

    Options: (needs to be applied by the editor parent)
        editable:   implies read-only
        tooltip:    the widget tooltip
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        raise NotImplementedError()

    def __init__(self, parent=None):
        '''
        The parent keyword is only there to be able to multiple inherit this w/ a widget (sucks)
        '''
        super(Editor_Interface, self).__init__()
        self._getter = None
        self._setter = None
        self._icon_provider = None
        self._is_edited = False

    def configure(self, getter, setter=None, icon_provider=None):
        '''
        Configures the value access for the editor.
        The getter and setter callables must accept arguments like:
            getter()
            setter(new_value)

        The editor will be editable if setter is not None.
        (using set_editable())
        '''
        self._getter = getter
        self._setter = setter
        self._icon_provider = icon_provider
        if self._setter is None:
            self.set_editable(False)

    def needs_choices(self):
        '''
        Must be overriden by editor presenting a choice of possible values.
        '''
        return False

    def get_icon_by_ref(self, icon_ref):
        try:
            resource_folder, icon_name = icon_ref
        except (TypeError, ValueError):
            # cannot unpack non-iterable
            # or not enough values to unpack
            icon_name = icon_ref
            # -> Use default value for resource_folder
            # by not using the kwarg:
            icon = self._icon_provider(
                None, 
                icon_name=icon_ref
            )
        else:
            icon = self._icon_provider(
                None, 
                resource_folder=resource_folder, 
                icon_name=icon_name,
            )
        return icon
        
    def get_icon_for(self, txt):
        if self._icon_provider is None:
            return None
        return self._icon_provider(txt)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        raise NotImplementedError()

    def is_edited(self):
        return self._is_edited

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        raise NotImplementedError()

    def fetch_value(self):
        '''
        Returns the value to display using the getter used
        on last configure() call.
        '''
        if self._getter is None:
            raise Exception('Editor getter not configured. (use configure())')
        try:
            return self._getter()
        except Exception as err:
            self.show_exception(err)

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        raise NotImplementedError()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        raise NotImplementedError()

    def apply(self):
        '''
        Applies the value returned by self.get_edited_value() using
        the setter used on last configure() call.
        '''
        if self._setter is None:
            raise Exception('Value cannot be edited. (no setter configured)')
        try:
            self._setter(self.get_edited_value())
        except Exception as err:
            self.show_exception(err)
        else:
            self._show_applied()

    def _on_edited(self):
        '''
        Must be called when the value has been edited.
        '''
        self._is_edited = True
        self._show_edited()

    def _on_updated(self):
        self._is_edited = False
        self._show_clean()

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        raise NotImplementedError()

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        raise NotImplementedError()

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is 
        up to date.
        '''
        raise NotImplementedError()

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        raise NotImplementedError()

    def show_exception(self, exception):
        import traceback
        err_msg = traceback.format_exc()
        self._show_error(err_msg)
