'''

Dependency Injection / Invertion of Control for Flow tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In some situations, you need to change the type of an Object in
a flow that is defined by some code you can't (or don't want to) modify.

*kabaret* let you do that on relations that have been flagged as 
`injectable()` by their author.

All `Child` relations (`Param`, `Computed`, `Connection`, ...) can be
injected, as well as the `Map.mapped_type(cls)` method. Here is how
to proceed:

Child Relations
^^^^^^^^^^^^^^^

1) The lib flow must flag the relation as injectable:

.. code-block:: python

    # in module awesome_flow_lib:

    class LibObject(flow.Object):
        # `inherit_default` arg is optional, defaults to True
        lib_child = flow.Child(LibChild).injectable(inherit_default=True)

2) Define your custom Object to use, then provide it in an ancestor of `LibObject`
that inherits `kabaret.flow.InjectionProvider` or just implements a 
`_injection_provider(slot_name, default_type)` classmethod:

.. code-block:: python

    from kabaret import flow
    import awesome_flow_lib

    class MyChild(awesome_flow_lib.LibChild):
        additionnal_param = flow.Param('Tadaaa !')

    class MyProject(flow.Object, flow.InjectionProvider):

        lib_object = flow.Child(awesome_flow_lib.LibOject)

        @classmethod
        def _injection_provider(cls, slot_name, default_type):
            if defalut_type is LibChild:
                return MyChild


Mapped Type
^^^^^^^^^^^

1) The lib flow must use `flow.injection.injectable()` in the `mapped_type(cls)` classmethod
of the injectable `Map`.

.. code-block:: python

    # in module awsome_flow_lib:

    class LibMap(flow.Map):

        @classmethod
        def mapped_type(cls):
            return flow.injection.injectable(
                LibMappedObject,
                # Optional, defaults to True:
                inherit_default=True,
            )

2) Define your custom Object to use, then provide it in an ancestor of `LibMap`
that inherits `kabaret.flow.InjectionProvider` or just implements a 
`_injection_provider(slot_name, default_type)` classmethod:

.. code-block:: python

    from kabaret import flow
    import awesome_flow_lib

    class MyMappedObject(awesome_flow_lib.LibMappedObject):
        additionnal_param = flow.Param('Tadaaa !')

    class MyProject(flow.Object, flow.InjectionProvider):

        lib_map = flow.Child(awesome_flow_lib.LibMap)

        @classmethod
        def _injection_provider(cls, slot_name, default_type):
            if slot_name == 'awesome_flow_lib.LibMappedObject':
                return MyMappedObject


'''
import logging
logger = logging.getLogger(__name__)

class InjectionSlotError(ValueError):
    pass

class InjectionInheritError(TypeError):
    def __init__(self, slot_name, injected_type, default_type):
        super(InjectionInheritError, self).__init__(
            "The injected type for slot '{}' must inherit '{}', got '{}'".format(
                slot_name, injected_type, default_type
            )
        )

class Injection(object):

    def __init__(self):
        super(Injection, self).__init__()
        self._inherit_defaults = {} # slot_name: bool
        self._cache = {}            # (context_name,slot_name): injected_type

    def _get_full_qualified_name(self, T):
        return '%s.%s' % (T.__module__, T.__name__)

    def get_context_name(self, o):
        project = o.root().project()
        return self._get_full_qualified_name(project.__class__)

    def get_slot_name(self, default_type):
        return self._get_full_qualified_name(default_type)

    def injectable(self, default_type, inherit_default=True):
        slot_name = self.get_slot_name(default_type)
        logger.debug("Declaring injection '{}'".format(slot_name))
        try:
            current_inherit_default = self._inherit_defaults[slot_name]
        except KeyError:
            self._inherit_defaults[slot_name] = inherit_default
        else:
            if current_inherit_default != inherit_default:
                raise InjectionSlotError(
                    "An incompatible injection already exists for '{}': "
                    "it has inherit_default=={:r}".format(
                        slot.inherit_default
                    )
                )
        return default_type

    def resolve(self, default_type, parent):
        slot_name = self.get_slot_name(default_type)
        try:
            inherit_default = self._inherit_defaults[slot_name]
        except KeyError:
            # Not slot defined for this type:
            logger.debug(
                "No injection declared for '{}', using default type.".format(
                    slot_name
                )
            )
            return default_type

        cache_key = (self.get_context_name(parent), slot_name)
        try:
            return self._cache[cache_key]
        except KeyError:
            logger.debug(
                "Resolving injection for '{}'.".format(
                    slot_name
                )
            )
        else:
            logger.debug(
                "Using cached injection for '{}'.".format(
                    slot_name
                )
            )

        injected_type = self._provide(slot_name, default_type, parent)
        if injected_type is default_type:
            logger.debug(
                "Injection for '{}' resolved to default type.".format(
                    slot_name
                )
            )
        elif inherit_default:
            if not issubclass(injected_type, default_type):
                raise InjectionInheritError(slot_name, injected_type, default_type)
        self._cache[slot_name] = injected_type
        return injected_type

    def _provide(self, slot_name, default_type, parent):
        '''
        Walk up all flow ancestors, resolving the injection at each step.
        Returns the last injected type.
        '''
        try:
            injected_type = parent._injection_provider(slot_name, default_type)
        except (AttributeError, TypeError):
            # The parent doesnt define `_injection_provider`
            # or does not define it as a callable:
            injected_type = default_type
        else:
            if injected_type is None:
                # The parent defines the `_injection_provider` method
                # but it didn't handle this injection
                injected_type = default_type

        parent = parent._mng.parent
        if parent is not None:
            injected_type = self._provide(slot_name, injected_type, parent)

        return injected_type
    
injection = Injection()

class InjectionProvider(object):
    '''
    This is a Mixin class used to implement injection
    provider in you flows.

    It's not mandatory to use it, you can simply add
    a _injection_provider(slot_name, default_type) class
    method in you flow Object(s). But this implementation
    prints out all requests so it's a nice way to see
    all the injectable slot_name before implementing
    your provider...
    '''
    def __init__(self):
        super(InjectionProvider, self).__init__()
    
    @classmethod
    def _injection_provider(cls, slot_name, default_type):
        logger.info(
            (
                'Default Injection Provider requested:\n'
                '  provider: {}\n'
                '  slot name: {}\n'
                '  deafult_type: {}\n'
            ).format(cls, slot_name, default_type)
        )
