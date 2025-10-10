from __future__ import print_function

from kabaret import flow

from .action_context import ActionContextGroup
from .action_submenus_demo import ActionSubmenusDemo
from .action_dialog_size import DialogSizeOptions

class NoDialogAction(flow.Action):

    def needs_dialog(self):
        return False

    def run(self, button):
        print('Well done Jolly Jumper !')

class SimpleDialogAction(flow.Action):

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is the action message: <3')
        return ['Ok', 'Maybe', 'Nope']

    def run(self, button):
        print('You chose {}'.format(button))

class DialogParamsAction(flow.Action):

    cut_down_trees = flow.BoolParam(True)
    skip_and_jump = flow.BoolParam(True)
    press_wild_flowers = flow.BoolParam(True)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Do you:')
        return ['Ok']

    def run(self, button):
        all_true = (
            self.cut_down_trees.get()
            and self.skip_and_jump.get()
            and self.press_wild_flowers.get()
        )
        if (
            self.cut_down_trees.get()
            and self.skip_and_jump.get()
            and self.press_wild_flowers.get()
        ):
            print('You hang around in bars')
        else:
            print('Do you ever party ?')

class DispatchParams(flow.Object):

    pool = flow.Param('Farm')
    priority = flow.Param(50)

    def get_flags(self):
        return [
            '-P', str(self.pool.get()),
            '-p', str(self.priority.get()),
        ]


class SequenceParam(flow.Object):

    first_frame = flow.Param(1)
    last_frame = flow.Param(100)

    def get_flags(self):
        return [
            '--first', str(self.first_frame.get()),
            '--last', str(self.last_frame.get()),
        ]

class ComplexDialogAction(flow.Action):

    dispatch = flow.Child(DispatchParams)
    sequence = flow.Child(SequenceParam)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Configure and Submit your job')
        return ['Submit']

    def run(self, button):
        cmd = ['spam_it']+self.dispatch.get_flags()+self.sequence.get_flags()
        print('#---> Cmd:', ' '.join(cmd))

class KeepOpenDialogAction(flow.Action):

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Click the Ok button !')
        return ['Ok', 'Close']

    def run(self, button):
        if button == 'Close':
            return

        self.message.set('Alrigth, now click the Close button :)')
        return self.get_result(close=False)

class GotoAction(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self._target_name = None
        return ['Goto Project', 'Goto Parent', 'Create Page and use it for all Goto', 'Open new a page every time',]

    def run(self, button):
        if button == 'Goto Project':
            project_oid = self.root().project().oid()
            return self.get_result(goto=project_oid, close=False, goto_target=self._target_name)

        if button == 'Goto Parent':
            parent_oid = self._parent.oid()
            return self.get_result(goto=parent_oid, close=False, goto_target=self._target_name)

        if button == 'Create Page and use it for all Goto':
            project_oid = self.root().project().oid()
            import time
            self._target_name = str(time.time())
            return self.get_result(goto=project_oid, close=False, goto_target=self._target_name)

        if button == 'Open new a page every time':
            project_oid = self.root().project().oid()
            return self.get_result(goto=project_oid, close=False, goto_target='_NEW_')

class GotoActionTitleFormater(flow.Action):
     
    _parent = flow.Parent()

    formater = flow.Param('-=# {} #=-')

    def needs_dialog(self):
        return True
    
    def get_buttons(self):
        self.message.set(
            '''
            <html>
            You can control the title of a view created 
            for an Action goto.<br>
            Enter a text containing "{}" in the formater
            field and click "Open".
            </html>
            '''
        )
        return ['Open', 'Close']
    
    def run(self, button):
        if button != 'Open':
            return 

        # You specify the format to use by building a view ID
        # in the form: <formater>|<view_id>
        # See the goto_target argument here:
        return self.get_result(
            goto=self.root().project().oid(),
            goto_target=str(self.formater.get())+'|VIEW_TITLW_SHOWCASE'
        )

class EditMyValueAction(flow.Action):

    _value = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('Pick a color:')
        return ['Red', 'Pink', 'Blue', 'Violet']

    def run(self, button):
        self._value.set(button)

class SetMyValueAction(flow.Action):

    _value = flow.Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._value.set('orange')

class MyValue(flow.values.Value):

    edit = flow.Child(EditMyValueAction)
    orange = flow.Child(SetMyValueAction)

class SubDialogAction(flow.Action):

    quote = flow.Param('', MyValue)

    def needs_dialog(self):
        return True

    def run(self, button):
        print('You selected: "{}"'.format(self.quote.get()))

class WizardDialogPage1(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is page <B>1/3</B> of a wizard style action')
        return ['Next']

    def run(self, button):
        return self.get_result(next_action=self._parent.wizard_page_2.oid())

class WizardDialogPage2(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is page <B>2/3</B> of a wizard style action')
        return ['Prev', 'Next']

    def run(self, button):
        if button == 'Next':
            return self.get_result(next_action=self._parent.wizard_page_3.oid())
        else:
            return self.get_result(next_action=self._parent.wizard_page_1.oid())

class WizardDialogPage3(flow.Action):

    _parent = flow.Parent()

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set('This is page <B>3/3</B> of a wizard style action')
        return ['Prev', 'Finish']

    def run(self, button):
        if button == 'Prev':
            return self.get_result(next_action=self._parent.wizard_page_2.oid())
        print('#---> You are a Wizard now !!!')


class ActionsGroup(flow.Object):

    no_dialog_action = flow.Child(NoDialogAction)
    simple_dialog_action = flow.Child(SimpleDialogAction)
    keep_dialog_open_action = flow.Child(KeepOpenDialogAction)
    goto_action = flow.Child(GotoAction)
    goto_title_formater = flow.Child(GotoActionTitleFormater)
    dialog_params_action = flow.Child(DialogParamsAction)
    complex_dialog_action = flow.Child(ComplexDialogAction)

    sub_dialog_action = flow.Child(SubDialogAction)

    wizard_page_1 = flow.Child(WizardDialogPage1)
    wizard_page_2 = flow.Child(WizardDialogPage2).ui(hidden=True)
    wizard_page_3 = flow.Child(WizardDialogPage3).ui(hidden=True)

    action_submenu_demo = flow.Child(ActionSubmenusDemo)

    sep = flow.Label(
        '<hr>'
        '<h2>Action Context</h2>'
        'Action are accessible from various places in the GUI. '
        'Each Action class can specify if it wants to appear in a given context by '
        'implementing the <b>allow_context(context)</b> method. Returning True will let '
        'the GUI show the action, returning False will prevent the GUI from considering '
        'the action. Note that even if shown, the action may be disabled by calling '
        'ui(enabled=False) on the relation pointing to it with<br> '
        'The context argument value will depend of the GUI context gathering the actions: '
        '<ul>'
        '<li>'
            'In Flow view\'s "inline" object representation:<br> '
            'A down arrow button is show at the right of Objects. '
            'It shows every Child action of the Object. '
            'This context is <font color=orange><B>Flow.inline</B></font><br>'
            'Note that this menu may in some case show actions from grand-children. '
            'In such cases, the context has a number of ">" appended: '
            '<font color=orange><B>Flow.inline&gt;&gt;&gt;</B></font><br>'
            'The number of ">" corresponds to the depth from the Object showing '
            'the inline representation.'
        '</li>'
        '<li>'
            'In Flow view\'s "details" object representation:<br> '
            'A button is show inside Objects for each of its '
            'Children actions. '
            'This context is <font color=orange><B>Flow.details</B></font> '
        '</li>'
        '<li>'
            'In Flow view\'s mapped items representation:<br> '
            'A right-click shows an action menu. '
            'This context is <font color=orange><B>Flow.map</B></font> '
        '</li>'
        '<li>'
            'Other view\'s may display action. Most views will use a context '
            'named after the view_type. For example, the ScriptView uses the '
            '<font color=orange><b>Script</b></font> context.'
        '</li>'
        '<li>'
            'The context may be <font color=orange><b>None</b></font> with legacy view '
            'code. In this case you can choose to return None so that the legacy '
            'behavior is used (using the class <i>SHOW_IN_PARENT_INLINE</i> and '
            '<i>SHOW_IN_PARENT_DETAILS</i> attributes) '
            'You should not relay on this since it will be deprecated at some point. '
        '</li>'
        '</ul>'
        'Enter the group below to explore a set of examples:'
    )
    action_context = flow.Child(ActionContextGroup)

    sep_2 = flow.Label(
        """
        <hr>
        <h2>Action Dialog Size</h2>
        <p>
            The size of an Action dialog at display can be configured using the <b>dialog_size</b> UI option.
            A minimum and a maximum size can also be specified using the <b>dialog_min_size</b> and
            <b>dialog_max_size</b> options. A size must be a tuple of the form (<i>width</i>, <i>height</i>).<br><br>
            
            In case the default size is outside the provided range, it is reset to the nearest limit. Invalid
            size limits are ignored though, in which case the default size is left unchanged.
            Providing a negative size (e.g., (-1, -1)) disables the option. It can be useful to disable
            a size option provided in a parent class of the Action.
            </p>
            <p>
            These options can be used either in the Action relation's <tt>ui()</tt> method
            <pre>>   Relation.ui(dialog[_min|_max]_size=(width, height))</pre>
            or in the Action's <tt>_fill_ui()</tt> method
            <pre>>   def _fill_ui(self, ui):
        ui['dialog[_min|_max]_size'] = (width, height)</pre>
            </p>
        </p>
        """
    )
    action_dialog_size_options = flow.Child(DialogSizeOptions)