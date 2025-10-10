

from kabaret.flow import (
    values,
    Object, Map, Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam
)

from .icon_browser import IconBrowserGroup
from .showcase import (
    ValuesGroup, 
    MapsGroup, 
    EditorsGroup, 
    RelationsGroup, 
    ActionsGroup, 
    UIConfigGroup,
    InjectionGroup,
    OtherFeaturesGroup,
)

from .showcase.custom_page import CustomPageGroup


class UnittestProject(Object):

    values = Child(ValuesGroup)
    maps = Child(MapsGroup)
    relations = Child(RelationsGroup)
    editors = Child(EditorsGroup)
    ui_config = Child(UIConfigGroup)
    actions = Child(ActionsGroup)
    custom_page = Child(CustomPageGroup)
    injection = Child(InjectionGroup)
    other = Child(OtherFeaturesGroup)
    icons = Child(IconBrowserGroup)
