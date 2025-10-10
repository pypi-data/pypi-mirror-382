'''
    The Flow let you model you project structure, pipeline and tracking strategies.

    < insert introductionnal description here >
'''

WIP = '''


    Changes to implement:

    - An object can holds override info for each of its relation ui_config (icon, editor, hidden, enabled, ...)
    - the ui_config must give info to have several relation on the same line.
    - use a context to declare relations into groups
    - use a context to declare relations into line
    - use typed value in param relation, with type validation (and leverage redis value types)
    - object summary must be a related object (with touched events emited when changed)
        -> gui finds it by relation name '_summary'
    - there must be an option to the computed relation to cache the result between touch() calls.

    - Refs stored as set in redis
    - Have indexed flag on values (using Value.get_index_oid(), configurable in relation)
    - Have inherited flag on values (default is provided by Value.get_inherited_value(), configuragle in relation)
    - Map -> Hash, use a special type in _items to leverage redis Hash value (speed + stable default ordering)
    - Map should store a 'is_hidden' bool alongside the full_qualified_type_name to allow filtering of
        mapped item w/o instanciating all of them (which is required if the info is store in a value of items)
    - Drop Map row_icons, use a special column '_style' in rows that olds icon, colors, etc...
    - Map.rows() must accept a page len and a page number

    - value store dont send old/new values on set methods (network noise for nothing)
    - object should not use parent's value store but the return value of parent.default_related_value_store
        (so Object can override its value store and still provide default value store for children)
    - computed values must not be saved in the value store (maybe add an option to do it sometimes...)

    - relations to values must have an option "dont_store_value" so object can have some on its
    related value in memory only (and no all related object like when you override the value store)
    - in memory value should not send touch event to other sessions

    - Action._buttons => this sucks, find something better.
    - Action must be able to be visible in parent inline w/o being visible in parent page
    - DropAction MUST BE ABLE TO HANDLE SEVERAL SOURCES.

    - drop the dirty flags for now and see how it goes.

    - see if Object instanciation is too costly (__new__ stuff), and fix it if needed.

    - Connection (Refs...) are only used for flow configuration by the user (casting, todo list...)
        when an Ojbect needs to know another -not directly related one (blast's maya scene),
        it should use a method returning that object (so that subclasses can override it)
        -> drop the smoky "PipelineConnection" stuff

    Wish list:
    - Action proxy (a relation to a relative action, so that it is promoted to (grand)parents )
    - Action chaining (aka wizards)
    - A concept of Next / Prev on objects.
        -> if parent is a map, navigate the map
        -> return prev/next related object, or parent's prev last relation / next first relation.
        -> parent must be able to override the behavior.

'''

from .exceptions import (
    MissingChildError, MissingRelationError, MappedNameError,
    RefSourceTypeError, RefSourceError,
)

from .relations import (
    Parent, Child, Relative,
    Separator, Label,
    Param, SessionParam,
    IntParam, BoolParam, FloatParam, StringParam,
    DictParam, OrderedStringSetParam, HashParam,
    Computed,
    Connection
)
from . import values
from .value_store import AbstractValueStore, MemoryValueStore

from .object import Object, group, SessionObject, Root, ThumbnailInfo
from .action import (
    Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
)
from .map import DynamicMap, Map, RefsMap
MAP_TYPES = (DynamicMap, Map)

from .injection import injection, InjectionProvider