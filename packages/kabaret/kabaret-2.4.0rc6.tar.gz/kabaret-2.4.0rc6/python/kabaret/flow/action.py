'''

    kabaret.flow.action

    Defines the Action class, an object on which UI commands can call
    the run() method to execute some code.

    The return value of run() dictates some UI behavior
    (see Action.run() doc).

    Defines the DropAction class, an object used to handle GUI drops
    on the ConnectAction parent.
    (NB: it is not a subclasse of Action and wont show up as a button)

'''

from .object import Object
from .relations import SessionParam, Parent


class Action(Object):

    ICON = 'action'

    # does this action shows in parent's inline GUI ?
    SHOW_IN_PARENT_INLINE = True
    # does this action shows in parent's detailed GUI ?
    SHOW_IN_PARENT_DETAILS = True

    message = SessionParam().ui(editor='label', wrap=True).ui(editable=False, label='')

    @classmethod
    def get_result(
            cls, close=None, refresh=None,
            goto=None, goto_target=None, goto_target_type=None, 
            next_action=None
    ):
        '''
        The value returned by run(button) will be inspected by callers to
        decide how they should react.
        This helper class method will generate a result matching its args:
            close: (bool)
                Prevent the action dialog to be closed when set to False
            refresh: (bool)
                Force a reload of the parent page avec dialog close
                (This should not be needed anymore thanks to touch() calls...)
            goto: (oid)
                Force the caller to load the given oid page.
            goto_target: (string or "_NEW_")
                The string identifer of the view targeted by the goto directive.
                The default targeted view is the current one or the one that created
                the action dialog. Spcecifying a target can be usefull to alter
                another view. If the specified target is not found, a new view
                will be created with this identifier so that further use of the
                action will affect this new view.
                The special identifier "_NEW_" can be used to force the creation
                of a new view.
            goto_target_type: (string)
                The type of the view targeted by the goto directive.
                Default is 'Flow'
                An easy way to find out the available type names is to use
                a obviously invalid value like "???" and look for the error
                message: it will contain a list of available type names.
            next_action: (oid)
                Force the dialog to not close but load the ui for the action
                with the given oid.
                This is the way to implement "Wizard Pages"

        '''
        ret = {}
        if close is not None:
            ret['close'] = close and True or False
        if refresh is not None:
            ret['refresh'] = refresh and True or False
        if goto is not None:
            ret['goto'] = goto
        if goto_target is not None:
            ret['goto_target'] = goto_target
        if goto_target_type is not None:
            ret['goto_target_type'] = goto_target_type

        if next_action is not None:
            ret['next_action'] = next_action

        return ret

    def allow_context(self, context):
        '''
        Override this to control where the action will be accessible.
        Return True to allow the action in the given context, False to disallow it,
        and None to fall back to legacy behavior (SHOW_IN_PARENT_* class attributes)

        Default is to return None.

        :param context: string. the context fetching the actions to show.
        Usually the type name of the View, optionally followed by sub-categories.
        The built-in Flow view will send:
            Flow.details    the action's parent details representation
            Flow.inline     the action's parent inline representation
            Flow.indline>>> the inline representation of  (the number of '>' depicts the depth of the inline
            action)
        :return: True/False/None
        '''
        if context is None:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning('Action.allow_context() with context=None ! {}'.format(self.oid()))
        return None

    def needs_dialog(self):
        '''
        May be overriden by subclasses to return False if the action
        does not need to show a dialog.
        Action without dialog are called with run(button=None), plus the 'goto'
        and 'next_action' fields of the returned value do the same.

        NB: If the action cannot run, it should show a dialog with a
        desciption why in self.message (override get_button() to do so).
        '''
        return True

    def get_buttons(self):
        '''
        Returns a list of string suitable as the 'button' argument for a
        call to self.run().

        NB: If the action cannot run, you should set a desciption why
        in self.message, return ['Cancel'] and handle that in run().
        This is far better than returning False from needs_dialog() or let
        the run() method decide to do nothing since the user will not have
        a clear feedback showing that nothing happened...
        '''
        return ['Run']

    def run(self, button):
        '''
        The return value should be None or the return value of
        a self.get_result() call.
        GUI will inspect the returned value and act upon it.
        '''
        self.message.set('This is an abstract action and it cannot be used.')
        return self.get_result(close=False)


class ConnectAction(Object):
    '''
    Subclasses will want to overwrite those methods:
        - accept_label: 
            return the label to show in GUI if the objects and urls are
            acceptable, None otherwise.
        - run: 
            to do the job.

    The run method is guaranted to be called only if accept_label did not return None.
    '''

    def accept_label(self, objects, urls):
        return 'Drop %i Oject(s)/File(s) here' % (len(objects) + len(urls),)

    def run(self, objects, urls):
        raise NotImplementedError()


class ChoiceValueSetAction(Action):

    SHOW_IN_PARENT_INLINE = False
    VALUE_TO_SET = None

    _choice_value = Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._choice_value.set(self.VALUE_TO_SET)


class ChoiceValueSelectAction(Action):

    SHOW_IN_PARENT_INLINE = False

    _choice_value = Parent()

    def get_buttons(self):
        return self._choice_value.choices()

    def run(self, button):
        self._choice_value.set(button)
