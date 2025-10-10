from __future__ import print_function

import time
import math

from kabaret.flow import (
    values,
    Object, Map, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Label, Param, SessionParam,
    IntParam, BoolParam, FloatParam, StringParam,
    DictParam, OrderedStringSetParam, HashParam,
)


class StaticChoices(values.ChoiceValue):

    CHOICES = ['Static', 'List', 'Of', 'Choices', 'NYS',
               'INV', 'WAIT', 'WIP', 'RVW', 'RTK', 'DONE', 'OOP']


class DynamicChoices(values.ChoiceValue):

    def choices(self):
        choices = {
            None: ('This is a', 'Dynamic list', 'Of choices'),
            'This is a': ('I can changes', 'depending on', 'what you want', '[reset]'),
            'Dynamic list': ('So you can', 'implement', 'workflow statuses', '[reset]'),
            'Of Choices': ('Voila...', '[reset]'),
            '[reset]': ('This is a', 'Dynamic list', 'Of choices'),
        }
        value = self.get()
        return choices.get(value, ['[reset]'])


class ComputedExample(Object):

    warning = Label(
        '<hr><h2>'
        'By default, Computed values are updated on every get() '
        'and the value is not stored in the value store.<br>'
        '<font color=#f44>/!\\ You cannot assume the computation will append the minimum number of times !</font><br>'
        'See how refreshing the page recompute "Value" (and see how the compute_count increments too).'
    )

    value = Computed().watched()
    compute_count = IntParam(0)

    def child_value_changed(self, value):
        print('Value Changed:', value.oid())

    def compute_child_value(self, child_value):
        # FIXME: this is call twice for each GUI page load :/
        # find why and fix it, or uncached Computed relation make no sens :(
        if child_value == self.value:
            self.value.set(time.time())
            self.compute_count.incr()


class TouchComputedExample(Object):

    help = Label(
        '<hr><h2>'
        'Change the "First" or "Last" param to see the "Count" being recomputed.<br>'
        'See how refreshing the page does not affect the "Computed Count".'
    )

    first = Param(1).watched()
    last = Param(100).watched()
    count = Computed(cached=True)
    computed_count = IntParam(0)

    def child_value_changed(self, child):
        if child in (self.first, self.last):
            self.count.touch()

    def compute_child_value(self, child_value):
        if child_value is self.count:
            self.count.set(
                int(self.last.get()) - int(self.first.get()) + 1
            )
            self.computed_count.incr()


class ResetMyIntAction(Action):
    _value = Parent()

    def get_buttons(self):
        return ['Confirm']

    def run(self, button):
        self._value.set(0)


class MyIntWithAction(values.IntValue):

    reset = Child(ResetMyIntAction)


class ValuesGroup(Object):

    param_info = Label(
        '<hr><h2>'
        'Values are what configures your Flow, '
        'either by User input or by Computation.<br>'
        'There are several subclasses. Some ensure type checking, other add '
        'functionnality like the ChoiceValue.<br>'
        'You add a Value to an Object using the "Param" relation.'
        '(or any of its subclasses)'
        '</h2>'
    )

    default_info = Label(
        '<hr><H3>'
        'The default is to accept any value.<br>Here you can enter anything:'
    )
    default_value = Param([1, 2, 3])

    session_info = Label(
        '<HR><H3>'
        'A "Session" value exists only in memory (not saved to the value store) and '
        'will return to its default for every session.'
    )
    session_value = SessionParam('Default Value...')

    typed_info = Label(
        '<HR><h3>'
        'There are several typed Value, each one with a corresponding Param subclasse and '
        'default editor:'
    )
    int_value = IntParam(0)
    bool_value = BoolParam(True)
    float_value = FloatParam(math.pi)
    string_value = StringParam('Yippie Ki Yay !')
    dict_value = DictParam({1: 11, 'a': 'aa'})
    ordered_string_set_value = OrderedStringSetParam()
    hash_value = HashParam()

    custom_info = Label(
        '<HR><h3>'
        'Param subclasses are mostly just preconfigured Param. You can achieve the same result by '
        'specifying the value type:'
    )
    my_int = Param(909, values.IntValue)
    custom_example = Label(
        '<HR><h3>'
        'This is the way to go if you need to use your very own value type<br>'
        'Here is a Value with actions attached to it:'
    )
    my_int_with_action = Param(909, MyIntWithAction)

    choice_info = Label(
        '<HR><h3>'
        'The ChoiceValue does not have a corresponding Param subclasse since you will need to '
        'inherit it to specify the choices.<br>'
        'Here are two examples:'
    )
    static_choices = Param(None, StaticChoices)
    dynamic_choices = Param(None, DynamicChoices)

    compute_info = Label(
        '<HR><h3>'
        'Some value can be computed instead of input from user, here are examples.</h3>'
        '(Open those pages to test refresh behavior)'
    )
    computed = Child(ComputedExample)
    touch_computed = Child(TouchComputedExample)
