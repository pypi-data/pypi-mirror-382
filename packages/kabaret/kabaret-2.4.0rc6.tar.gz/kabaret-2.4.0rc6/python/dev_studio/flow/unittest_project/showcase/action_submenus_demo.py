from kabaret import flow

class NoDialogAction(flow.Action):
    def needs_dialog(self): return False

class ObjectWithSubmenus(flow.Object):

    with flow.group('Group A'):
        group_a_1 = flow.Child(flow.Action)
        group_a_2 = flow.Child(NoDialogAction)

    with flow.group('Group A/SubGroup A'):
        group_aa_1 = flow.Child(flow.Action)
        group_aa_2 = flow.Child(NoDialogAction)

    with flow.group('Group A/SubGroup B'):
        group_ab_1 = flow.Child(flow.Action)
        group_ab_2 = flow.Child(NoDialogAction)

    with flow.group('Group B'):
        group_b_1 = flow.Child(flow.Action)
        group_b_2 = flow.Child(NoDialogAction)

    with flow.group('Group B/SubGroup A'):
        group_ba_1 = flow.Child(flow.Action)
        group_ba_2 = flow.Child(NoDialogAction)
    
class AddItemAction(flow.Action):
    _map = flow.Parent()
    def needs_dialog(self): return False
    def run(self, button): self._map.do_add_item()

class MapWithSubmenus(flow.Map):

    add_item = flow.Child(AddItemAction)
    with flow.group('GroupA'):
        action_A1 = flow.Child(flow.Action)
        action_A2 = flow.Child(flow.Action)
    with flow.group('GroupA/SubA'):
        action_AA1 = flow.Child(flow.Action)
        action_AA2 = flow.Child(flow.Action)
    with flow.group('GroupA/SubB'):
        action_AB1 = flow.Child(flow.Action)
        action_AB2 = flow.Child(flow.Action)
    with flow.group('GroupB'):
        action_B1 = flow.Child(flow.Action)
        action_B2 = flow.Child(flow.Action)
    with flow.group('GroupB/SubA'):
        action_BA1 = flow.Child(flow.Action)
        action_BA2 = flow.Child(flow.Action)
    with flow.group('GroupB/SubB'):
        action_BB1 = flow.Child(flow.Action)
        action_BB2 = flow.Child(flow.Action)
        
    @classmethod
    def mapped_type(cls):
        return ObjectWithSubmenus
    
    def do_add_item(self):
        name = 'Item{:03}'.format(len(self))
        self.add(name)
        self.touch()

class ActionSubmenusDemo(flow.Object):

    doc = flow.Label(
        'See code in "{}" to learn how to activate Action Submenu like '
        'here.'.format(__name__)
        +'<pre>'
        '''
TL;DR:
    object_with_submenus = flow.Child(ObjectWithSubmenus).ui(
        action_submenus=True
    )
    map_with_submenus = flow.Child(MapWithSubmenus).ui(
        action_submenus=True,
        items_action_submenus=True,
    )
        '''
        '</pre>'
    )
    object_with_submenus = flow.Child(ObjectWithSubmenus).ui(
        action_submenus=True
    )
    map_with_submenus = flow.Child(MapWithSubmenus).ui(
        action_submenus=True,
        items_action_submenus=True,
    )