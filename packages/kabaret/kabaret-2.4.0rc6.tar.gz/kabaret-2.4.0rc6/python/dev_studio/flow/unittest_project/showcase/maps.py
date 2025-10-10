
import random

from kabaret.flow import (
    values,
    Object, Map, DynamicMap, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam,
    Label,
)

from .map_as_view import MapAsViewGroup

class MyDynamicItem(Object):

    pass


class MyDynamicMap(DynamicMap):
    '''
    The DynamicMap items are defined by implementing the methods:
        - mapped_names(...)
            Returns the names of the items.

        - _get_mapped_item_type(name) [Optional]
            Return the type of the item with the given name
    '''
    @classmethod
    def mapped_type(cls):
        return MyDynamicItem

    def mapped_names(self, page_num=0, page_size=None):
        self._last_rand_names = [
            'Item_%03i' % (i)
            for i in range(random.randint(1, 10))
        ]
        return self._last_rand_names

    def has_mapped_name(self, name):
        # NB: this is needed because the demo is based on a random list, which you'll
        # probably never have in real life scenarii...
        return name in self._last_rand_names

    def summary(self):
        return 'The number of items is randomized, refresh several times to witness it.'


class LongMap(DynamicMap):

    def __init__(self, parent, name):
        self.items = {
            'Kajus': 'Fry',
            'Gail': 'Jennings',
            'Angel': 'Collins',
            'Amelia': 'Southern',
            'Nazia': 'Parrish',
            'Niamh': 'Mullen',
            'Kailan': 'Odling',
            'Aniqa': 'Haines',
            'Brittany': 'Lamb',
            'Jareth': 'Rowe',
            'Elsie_May': 'Melia',
            'Noah': 'Robins',
            'Rochelle': 'Farrell',
            'Abdallah': 'Hickman',
            'Shayne': 'Rhodes',
            'Neve': 'Hill',
            'Kyle': 'Blair',
            'Ishmael': 'Hoover',
            'Izaan': 'Hull',
            'Giles': 'Mccray',
            'Sumaiya': 'Santana',
            'Efa': 'Townsend',
            'Alba': 'Gates',
            'Asha': 'Mcintyre',
            'Brogan': 'Matthams',
            'Tyrique': 'Mcdermott',
            'Idris': 'Patterson',
            'Ravi': 'Whiteley',
            'Leyton': 'Lambert',
            'Anabella': 'Weir',
            'Franciszek': 'Alcock',
            'Sami': 'Searle',
            'Patrycja': 'Rodriguez',
            'Francesca': 'Conrad',
            'Marie': 'Randall',
            'Zakariya': 'Baldwin',
            'Mathew': 'Gay',
            'Elysia': 'Bateman',
            'Marley': 'Simons'
        }
        super(LongMap, self).__init__(parent, name)

    def mapped_names(self, page_num=0, page_size=None):
        return self.items.keys()

    def has_mapped_name(self, name):
        return name in self.items

    def columns(self):
        return ['Name', 'Surname']

    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Surname'] = self.items[item.name()]


class OuichMap(DynamicMap):

    def __init__(self, parent, name):
        self.items = {
            'George': 'Monde de merde',
            'Le_temoin_professionnel': 'Entre, fouille-merde. Je vais t\'en filer, moi, '
                                       'du biscuit sur George pour ta feuille de chou',
            'Dino': 'T\'es un ouf toi, un ouf malade',
            '_': 'Je suis limite nervous breakdown',
            'Peter': 'On dit une ouiche lorraine.',
            'Steven': 'Moi je suis sur qu\'on dit "quiche". Enfin bon...',
            'L_indien': 'On va manger des chips ! T\'entends ?!? Des chips !'
                        ' C\'est tout ce que ca te fait quand je te dis qu\'on va manger des chips ?',
            'Hugues': 'On l\'a retrouve assassine un jour. Il en est mort.',
        }
        super(OuichMap, self).__init__(parent, name)

    def mapped_names(self, page_num=0, page_size=None):
        return self.items.keys()

    def has_mapped_name(self, name):
        return name in self.items

    def columns(self):
        return ['Name', 'Sentence']

    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Sentence'] = self.items[item.name()]


class MyItem(Object):
    pass


class AddItemAction(Action):

    _map = Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        item_name = 'Item_%03i' % (len(self._map) + 1,)
        self._map.add(item_name)
        self._map.touch()


class RemoveItemAction(Action):

    _map = Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        names = self._map.mapped_names()
        if not names:
            return
        name = names[-1]
        self._map.remove(name)
        self._map.touch()


class MyMap(Map):

    add_item = Child(AddItemAction)
    remove_item = Child(RemoveItemAction)

    @classmethod
    def mapped_type(cls):
        return MyItem

    def summary(self):
        return 'use actions here to add/remove items. ->'

class SayHelloAction(Action):

    _shot = Parent()

    def needs_dialog(self): 
        return True
    
    def get_buttons(self):
        self.message.set('<H2>HELLO FROM %s!</H2>'%self._shot.name())
        return ['Bye...']
    
    def run(self, button):
        pass

class _GotoDeptAction(Action):

    DEPT = None
    _item = Parent()

    def allow_context(self, context):
        return 'inline' in context

    def needs_dialog(self): 
        return False

    def run(self, button):
        return self.get_result(
            goto=getattr(self._item, self.DEPT).oid()
        )

class GotoAnimAction(_GotoDeptAction):
    DEPT = 'anim'

class GotoLightingAction(_GotoDeptAction):
    DEPT = 'lighting'

class GotoCompAction(_GotoDeptAction):
    DEPT = 'comp'

class ShotStatusValue(values.ChoiceValue):
    CHOICES = ('NYS', 'WIP', 'RTK', 'DONE', 'OOP')

class Dept(Object):

    shot = Parent()

    message = Computed()
    status = Param('NYS', ShotStatusValue).watched()

    def compute_child_value(self, value):
        value.set('This is the %s Department'%self.name())

    def child_value_changed(self, value):
        self.shot.touch()

class ActionMapItem(Object):

    say_hello = Child(SayHelloAction)
    goto_anim = Child(GotoAnimAction)
    goto_lighting = Child(GotoLightingAction)
    goto_comp = Child(GotoCompAction)
    
    anim = Child(Dept)
    lighting = Child(Dept)
    comp = Child(Dept)
    
class AddActionItemAction(Action):

    ICON = ('icons.gui', 'plus-sign-in-a-black-circle')
    
    _map = Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        count = len(self._map.mapped_names())
        self._map.add('Shot%03d'%count)
        self._map.touch()

class ClearMapAction(Action):

    ICON = ('icons.gui', 'remove-symbol')

    _map = Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._map.clear()
        self._map.touch()

class ActionMap(Map):

    add_item = Child(AddActionItemAction)
    clear_map = Child(ClearMapAction)

    def mapped_type(cls):
        return ActionMapItem

    def columns(self):
        return ['Name', 'Anim', 'Lighting', 'Comp']
    
    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Anim'] = item.anim.status.get()
        row['Lighting'] = item.lighting.status.get()
        row['Comp'] = item.comp.status.get()
        
    def _fill_row_style(self, style, item, row):
        style['activate_oid'] = item.say_hello.oid()
        style['Anim_activate_oid'] = item.goto_anim.oid()
        style['Lighting_activate_oid'] = item.goto_lighting.oid()
        style['Comp_activate_oid'] = item.goto_comp.oid()

        style['icon'] = 'shot'
        style['Anim_icon'] = ('icons.status', row['Anim'])
        style['Lighting_icon'] = ('icons.status', row['Lighting'])
        style['Comp_icon'] = ('icons.status', row['Comp'])

class MapActionsGroup(Object):

    doc = Label(
        '<H3>'
        'By default, double clicking a Map item will open the item page.<br>'
        'You can override this and trigger an Action instead by setting the '
        '"activate_oid" in the item row style to the Action oid to trigger:<br>'
        '''<pre>
        # In your Map subclass:
        def _fill_row_style(self, style, item, row):
            style['activate_oid'] = item.spread_love_action.oid()
        </pre>'''
        'With this, the `spread_love_action` is triggered when the user double '
        'clicks the item.<br>'
        '<br>'
        'As for icons and colors (see ShowCase/ui_config/map_example), you can '
        'also specify an action for a specific column with "<column_name>_activate_oid"<br>'
        '<br>'
        'Here is an example where Actions are used to say Hello or to open a specific page:'
    )
    my_map = Child(ActionMap).ui(expanded=True)

    def summary(self):
        return '<-- Double click this to see examples.'

class MapsGroup(Object):

    doc = Label(
        '<HR><H3>'
        'A "Map" has a per-instance list of related object.'
        '</H3>'
        'When modeling your flow, you will use maps to store arbitrary lists of objects.<br>'
        'This list may be dynamic to reflect existing stuff outside your Flow,<br>'
        'or user managed to grow your Flow instances.<br>'
        'Options are:'
        '<ul>'
        '   <li>sort_by (int or str) - The column with which the map is sorted</li>'
        '   <li>sort_order (str, asc or dsc) - Which order for sort the map</li>'
        '   <li>show_filter (bool) - display or not the filter field</li>'
        '   <li>default_height (int) - default height of the table'
        '   <li>auto_fit (bool) - adjust the column width to the content'
        '   <li>columns_width (tuple of percent) - width of columns'
        '</ul>'
        '<H3>Example:</H3>'
        '<pre>\n'
        'dynamic_map = Child(MyDynamicMap)\n'
        'sorted_map = Child(LongMap).ui(sort_by="Name", show_filter=True)\n'
        'bounded_map = Child(OuichMap).ui(default_height=150, auto_fit=False, columns_width=(30, 70))\n'
        '</pre>\n'
    )

    dynamic_map = Child(MyDynamicMap)
    managed_map = Child(MyMap)
    sorted_map = Child(LongMap).ui(sort_by="Name", show_filter=True)
    bounded_map = Child(OuichMap).ui(default_height=150, auto_fit=False, columns_width=(30, 70))
    map_view = Child(MapAsViewGroup)
    map_actions = Child(MapActionsGroup).ui(expandable=False)
