'''

    kabaret.flow.object

    Defines the Object class, the base for all object in a flow, and
    the Root class used to hold a flow graph.

'''
import logging

import six

from .exceptions import WIPException
from .exceptions import MissingRelationError, MissingChildError

from .value_store import MemoryValueStore


class _Manager(object):

    def __init__(self, object, parent, name, value_store):
        super(_Manager, self).__init__()
        self.object = object
        self.parent = parent
        self.name = name
        self.value_store = value_store
        self.destroyed = False  # TODO: use this to stop behavior after desctuction

        if self.parent is not None:
            self.parent._mng.set_child(self, object)

        self.children = {}

#---OLD
    def create_manager(self, object, parent, name):
        raise WIPException('Is this used anywhere ?!?')
        return self.__class__(object, parent, name)

    def root(self):
        if self.parent is None:
            return self.object
        return self.parent._mng.root()

#---OLD
    def iter_parents(self):
        raise WIPException('Is this used anywhere ?!?')
        curr = self
        while curr is not None:
            parent = curr.parent
            if parent is None:
                raise StopIteration()
            yield parent
            curr = parent._mng

    def oid(self):
        # TODO: since we cant rename an item, and we use this quite a lot:
        # shouldn't we bake it ?
        # (it may help for Map.rows())
        if self.parent is None:
            return self.name
        return '%s/%s' % (self.parent._mng.oid(), self.name)

    def destroy(self):
        logging.getLogger('kabaret.flow').debug('----> DESTROYING ' + self.oid() + '. Should we notify refs ?')
        self.destroyed = True
        self.parent = None

    def set_child(self, mng, object):
        try:
            self.children[mng.name]
        except:
            self.children[mng.name] = object
        else:
            raise Exception('This child already exists !!!')

    def relations(self):
        return self.object._relations

#---OLD
    def drop_child(self, name):
        raise WIPException('This has been renamed destroy_child')

    def destroy_child(self, name):
        try:
            old = self.children[name]
        except KeyError:
            raise MissingChildError(self.oid(), name)
        else:
            old._mng.destroy()
        del self.children[name]

#---OLD
    def children_names(self):
        # relations must be used to find children names.
        raise WIPException('This should not be useful')
        try:
            return self.object.children_names()
        except AttributeError:
            return self.children.keys()

#---OLD
    def children_oids(self):
        raise WIPException('This should not be useful')
        oid = self.oid()
        return ['%s/%s' % (oid, n) for n in self.children_names()]

#---OLD
    def object_type_name(self):
        raise WIPException('Is this used anywhere ?!?')
        return self.object.__class__.__name__

    def get_qualified_type_name(self, TYPE):
        return '%s.%s' % (TYPE.__module__, TYPE.__name__)

    def object_qualified_type_name(self):
        return self.get_qualified_type_name(self.object.__class__)

    def qualified_type_name_to_type(self, qualified_type_name):
        # NB: str it because json tend to send unicodes here :/
        chunks = str(qualified_type_name).rsplit('.', 1)
        type_name = chunks.pop(-1)

        module_path = chunks[0]
        leaf_module_name = module_path.rsplit('.', 1)[-1]
        module = __import__(module_path, None, None, leaf_module_name, 0)

        try:
            return getattr(module, type_name)
        except AttributeError:
            raise ImportError("Nothing named %s in module %s" %
                              (type_name, module_path))

#---OLD
    def __len__(self):
        raise WIPException('This should not be useful')
        return len(self.children)

#---OLD
    def __iter__(self):
        raise WIPException('This should not be useful')
        for name, object in self.children.iteritems():
            yield name, object

#---OLD
    def __contains__(self, object_name):
        raise WIPException('This should not be useful')
        return object_name in self.children

    def has_related(self, relation_name):
        return relation_name in [r.name for r in self.object._relations]
    
    def get_relation(self, name):
        try:
            return next((r for r in self.object._relations if r.name == name))
        except StopIteration:
            raise AttributeError("Could not find relation '%s' under '%s'" %
                                (name, self.oid()))

#---OLD
    def get_child(self, name):
        raise WIPException('This has been renamed to get_existing_child(name)')

    def get_existing_child(self, name):
        '''
        Return the child object named 'name'.
        This DOES NOT involve Relation instance and can only return already
        existing children.

        If no such child exists, a MissingChildError is raised.
        '''
        try:
            return self.children[name]
        except KeyError:
            raise MissingChildError(self.oid(), name)

#---OLD
    def get_typed_children(self, class_or_type_or_tuple):
        raise WIPException('Is this used anywhere ?!?')
        return [
            relation.get_related(self.object)
            for relation in self.object._relations
            if issubclass(relation.related_type, class_or_type_or_tuple)
        ]

    def get_object(self, oid):
        '''
        Returns the object with the given oid.
        If oid is relative (does not start with /), returns a (grand) child.

        The oid may contain . and .. has in posix paths
        (do we really use that ? o.O)

        This will evaluate the _Relation used by self.object and potential
        override of __getattr__.
        '''
        if oid is None:
            return self.object

        # remove consecutive slashes (//) to avoid requesting root in
        # the middle of the search
        while '//' in oid:
            oid = oid.replace('//', '/')

        cuts = oid.split('/', 1)
        try:
            remain = cuts[1]
        except IndexError:
            remain = None

        next = cuts[0]

        if not next:
            root = self.root()
            return root._mng.get_object(remain)

        if next == '.':
            return self.get_object(remain)

        if next == '..':
            return self.parent._mng.get_object(remain)

        if self.has_related(next):
            # we must us getattr to have the relation do the job:
            child = getattr(self.object, next)
            if child is None:
                # This may happen with erroneous `Relative` oid
                return None
        else:
            # maybe it's in a map
            try:
                self.object.get_mapped
            except AttributeError:
                raise MissingRelationError(self.oid(), next)
            else:
                child = self.object.get_mapped(next)

        return child._mng.get_object(remain)

#---OLD
    def set_default_value(self, value):
        raise WIPException('! this should be in Value !')
        self.default_value = value

#---OLD
    def compute_value(self):
        raise WIPException('! this should be in ComputedValue !')
        if not self.is_dirty():
            return
        self.parent.compute_child_value(self.object)

    def add_ref(self, object):
        oid = object.oid()
        refs = set(self.refs())
        if oid in refs:
            # Avoid doubles and extra refresh/events:
            return
        refs.add(object.oid())
        refs = sorted(refs)
        self.value_store.set(self.oid() + '.refs', refs)

    def remove_ref(self, object):
        # use set to cleanup duplicates (was possible in previous code)
        refs = set(self.refs())
        try:
            refs.remove(object.oid())
        except KeyError:
            # This should not happen.
            logging.getLogger('kabaret.flow').warning('Removing ref %r from %r: ref not in list!')
            return
        refs = sorted(refs)
        self.value_store.set(self.oid() + '.refs', refs)

    def refs(self):
        try:
            return self.value_store.get(self.oid() + '.refs')
        except KeyError:
            return []

    def cleanup_refs(self):
        """
        check registered refs and remove those which are not relevant anymore (deleted object or not connected anymore)
        """
        try:
            refs = self.value_store.get(self.oid() + '.refs')
        except KeyError:
            return

        valid_refs = set()
        for ref_oid in refs:
            try:
                ref = self.get_object(ref_oid)
            except Exception as e:
                logging.getLogger('kabaret').warning("Cannot find {}: {}".format(ref_oid, e))
            else:
                if ref.get() == self.object:
                    valid_refs.add(ref_oid)

        self.value_store.set(self.oid() + '.refs', list(valid_refs))

    def ref_objects(self):
        return [self.get_object(ref_oid) for ref_oid in self.refs()]

    def get_value(self, default):
        try:
            return self.value_store.get(self.oid())
        except KeyError:
            return default

    def del_value(self):
        self.value_store.delete(self.oid())
        self._on_value_changed()

    def set_value(self, value):
        self.value_store.set(self.oid(), value)
        self._on_value_changed()

#--- OLD
    # def update_dict_value(self, **new_values):
    #     self.value_store.update(self.oid(), **new_values)
    #     self._on_value_changed()

    def incr_value(self, by=1):
        self.value_store.incr(self.oid(), by)
        self._on_value_changed()

    def decr_value(self, by=1):
        self.value_store.decr(self.oid(), by)
        self._on_value_changed()

    # --- OSS

    def oss_get(self):
        return self.value_store.oss_get(self.oid())

    def oss_get_range(self, first, last):
        return self.value_store.oss_get_range(self.oid(), first, last)

    def oss_has(self, member):
        return self.value_store.oss_has(self.oid(), member)

    def oss_add(self, member, score):
        self.value_store.oss_add(self.oid(), member, score)
        self._on_value_changed()

    def oss_remove(self, member):
        self.value_store.oss_remove(self.oid(), member)
        self._on_value_changed()

    def oss_len(self):
        return self.value_store.oss_len(self.oid())

    def oss_get_score(self, member, score):
        return self.value_store.oss_get_score(self.oid(), member)

    def oss_set_score(self, member, score):
        self.value_store.oss_set_score(self.oid(), member, score)
        self._on_value_changed()

    # --- HASH

    def get_hash_value(self):
        return self.value_store.get(self.oid())

    def hash_get_key(self, key):
        return self.value_store.hash_get_key(self.oid(), key)

    def hash_has_key(self, key):
        return self.value_store.hash_has_key(self.oid(), key)

    def del_hash_key(self, key):
        self.value_store.del_hash_key(self.oid(), key)
        self._on_value_changed()

    def get_hash(self):
        return self.value_store.get_hash(self.oid())

    def get_hash_as_dict(self):
        return self.value_store.get_hash_as_dict(self.oid())

    def get_hash_keys(self):
        return self.value_store.get_hash_keys(self.oid())

    def get_hash_len(self):
        return self.value_store.get_hash_len(self.oid())

    def update_hash(self, mapping):
        self.value_store.update_hash(self.oid(), mapping)
        self._on_value_changed()

    def set_hash(self, mapping):
        self.value_store.set_hash(self.oid(), mapping)
        self._on_value_changed()

    def set_hash_key(self, key, value):
        self.value_store.set_hash_key(self.oid(), key, value)
        self._on_value_changed()

    def _on_value_changed(self):
        # use self.object.touch() and not self.touch()
        # because object.touch() may have been overridden to implement
        # touch propagation.
        self.object.touch()

    def touch(self):
        self.root().object_touched(self.object)

    def pformat(self, indent=0):
        from .values import Value, Ref

        if isinstance(self.object, Ref):
            target = self.object.get()
            if target is not None:
                infos = "%s<%s>(%s)" % (
                    self.object.__class__.__name__,
                    target.__class__.__name__,
                    target._mng.oid()
                )
            else:
                infos = "%s<%s>" % (
                    self.object.__class__.__name__, target.__class__.__name__)
        elif isinstance(self.object, Value):
            infos = "%s(%s)" % (
                self.object.__class__.__name__, repr(self.object.get())[:50])
        else:
            infos = self.object.__class__.__name__
        head = "%s%s = %s" % (
            indent * 0 * '  ',
            self.oid(),
            infos,
        )
        i = indent + 1
        body = '\n'.join([
            o._mng.pformat(i) for n, o in sorted(self.children.items())
        ])
        return head + (body and '\n' + body or '')
    
    def on_object_init(self):
        pass


class _Relation(object):
    '''
    This is the base class of all relations.
    You must use one of the subclasses.

    Relations are descriptors managing the instantiation and the access
    to object related to the relation owner.

    You can configure the relation behavior using the :any:`ui()` and :any:`editor()`
    methods.
    '''
    _RELATION_TYPE_NAME = None  # see cls.relation_type_name()

    MAX_INDEX = 100  # maximum automatic relation index.

    _next_relation_id = 0

    _GROUP_CONTEXT = []

    @classmethod
    def _generate_relation_id(cls):
        # tricky stuff to order relations in declaration order [part 1]
        # /!\ be sure to use _Relation class (not cls)
        _Relation._next_relation_id += 1
        return cls._next_relation_id

    @classmethod
    def relation_type_name(cls):
        '''
        Used by clients to classify relations.
        Returns cls._RELATION_TYPE_NAME. Subclass can set this
        class attribute to alter the string returned here.
        '''
        return cls._RELATION_TYPE_NAME

    @classmethod
    def get_default_group(cls):
        if not cls._GROUP_CONTEXT:
            return None
        return '.'.join(cls._GROUP_CONTEXT)

    def __init__(self, related_type):
        super(_Relation, self).__init__()
        self.id = self.__class__._generate_relation_id()
        self.index = 0

        self.group = None

        self.name = None
        self.related_type = related_type
        self.used = False

        self._ui = {
            # missing key means use default: 'editor_type': None,
            'icon': None,
            'editor_type': None,
            'editable': False,
            'label': None,
            'group': self.__class__.get_default_group(),
            'hidden': False,
            'tooltip': None,
        }

    def ui(
        self,
        icon=None,
        editor=None,
        editable=None,
        label=None,
        group=None,
        hidden=None,
        tooltip=None,
        expanded=None,
        expandable=None,
        **editor_options
    ):
        '''
        Configure the relation GUI.
        This method returns self so that you can chain
        it in assigment:
        ::
            meh = MyRelation('example').ui(label='Amazing')

        '''
        if icon is not None:
            self._ui['icon'] = icon
        if editor is not None:
            self._ui['editor_type'] = editor
        if editable is not None:
            self._ui['editable'] = editable
        if label is not None:
            self._ui['label'] = label
        if group is not None:
            self._ui['group'] = group
        if hidden is not None:
            self._ui['hidden'] = hidden and True or False
        if tooltip is not None:
            self._ui['tooltip'] = tooltip
        if expanded is not None:
            self._ui['expanded'] = bool(expanded)
        if expandable is not None:
            self._ui['expandable'] = bool(expandable)
        if editor_options:
            self._ui.update(editor_options)
        return self

    def is_hidden(self, of=None):
        ui = self.get_ui(of)
        return ui.get('hidden', False)

    def get_ui(self, of=None):
        '''

        :param of: the parent of the related object. If not None, the related
        Object._fill_ui(ui) is used instead of the default value set on the
        relation.
        :return: dict with keys icon, editor_type, editable, label, hidden, tooltip
        '''
        ui = self._ui.copy()
        if not ui.get('icon') and self.related_type is not None:
            ui['icon'] = self.related_type.ICON
        if of is not None:
            related = self.get_related(of)
            related._fill_ui(ui)
        return ui

    def set_related_type(self, related_type):
        if self.used:
            raise RuntimeError(
                'Too late to change the related type: '
                'some related object have already been created.'
            )
        self.related_type = related_type

    def _create_object(self, parent):
        raise NotImplementedError()

    def get_related(self, of):
        try:
            return of._mng.get_existing_child(self.name)
        except MissingChildError:
            pass  # let's create it

        related = self._create_object(of)
        self.used = True
        return related

    def __get__(self, o, t=None):
        '''
        Returns the child object referred to by this relation
        when it is accessed from an object instance. Otherwise
        (relation accessed from the class), returns the relation
        itself.
        '''
        if o is None:
            return self
        return self.get_related(o)


class _RelationGroupContext:

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        _Relation._GROUP_CONTEXT.append(self.name)
        return self

    def __exit__(self, type, value, tb):
        _Relation._GROUP_CONTEXT.pop()


def group(name):
    return _RelationGroupContext(name)


class ObjectType(type):

    def __new__(cls, class_name, bases, class_dict):
        # tricky stuff to order relations in declaration order [part 2]
        default_relation_group = class_dict.get('LABEL', class_name)
        if bases != (object,):  # if it's not our most base class
            if 'oid' in class_dict:
                raise ValueError(
                    'Cannot create ObjectType %r with %r named "oid" (reserved name)' % (
                        class_name, class_dict['oid']
                    )
                )
            if 'name' in class_dict:
                raise ValueError('Cannot create ObjectType %r with %r named "name" (reserved name)' % (
                    class_name, class_dict['name']))
        else:
            default_relation_group = None

        relations = []
        relation_index = 0
        for base in bases:
            try:
                base_relations = base._relations
            except AttributeError:
                pass
            else:
                relations.extend(base_relations)
                relation_indexes = [
                    r.index for r in base_relations if r.index > 0 and r.index < _Relation.MAX_INDEX]
                if relation_indexes:
                    relation_index = max(relation_index, max(relation_indexes))

        _relations = sorted(
            ((key, o) for (key, o) in class_dict.items() if isinstance(o, _Relation)),
            key=lambda x: x[1].id
        )

        for n, o in _relations:
            if isinstance(o, _Relation):
                o.name = n
                if not o.index:
                    relation_index = relation_index + 1
                    o.index = relation_index
                if o.group is None:
                    o.group = default_relation_group
                if o.index > _Relation.MAX_INDEX:
                    raise Exception('Relation index for %r of ObjectType %r exceeded the max of %s.' %
                                    (n, class_name, _Relation.MAX_INDEX))
                relations.append(o)

        # remove overridden relations by using only the last ones with same name:
        relations = dict([(r.name, r) for r in relations])

        def relation_sort_key(r):
            return r.index

        relations = sorted(
            six.viewvalues(relations),  # py 2+3 version of relations.values()
            key=relation_sort_key
        )

        class_dict['_ref_type'] = None
        class_dict['_relations'] = relations
        return super(ObjectType, cls).__new__(cls, class_name, bases, class_dict)


class Object(six.with_metaclass(ObjectType, object)):

    _MANAGER_TYPE = None
    _PROPAGATE_MANAGER_TYPE = None

    @classmethod
    def _create_value_store(cls, parent, name):
        '''
        Subclasses may override this class method to return
        the value store they want to use.
        Default is to return None, which will lead to using the parent's value_store
        '''
        return None

    ICON = 'object'

    @classmethod
    def ref_type(cls):
        if cls._ref_type is not None:
            return cls._ref_type

        from .values import Ref

        class MyTypeRef(Ref):
            SOURCE_TYPE = cls
        MyTypeRef.__name__ = cls.__name__ + 'Ref'
        cls._ref_type = MyTypeRef
        return cls._ref_type

    @classmethod
    def get_source_display(cls, oid):
        '''
        Returns the text to display when showing a Ref pointing to the object of type cls with
        the id oid.

        This is used by Connection relations' GUI.
        '''
        return oid
    
    @classmethod
    def _resolve_manager_type(cls, parent):
        manager_type = None

        if parent is None:
            if cls._MANAGER_TYPE is None:
                manager_type = _Manager
            elif not issubclass(cls._MANAGER_TYPE, _Manager):
                raise TypeError(
                    'Invalid manager type %r (it must be _Manager or a subclass).' % cls._MANAGER_TYPE
                )
            else:
                manager_type = cls._MANAGER_TYPE
        else:
            if cls._MANAGER_TYPE is None:
                if parent._resolve_propagate_manager_type():
                    manager_type = parent._mng.__class__
                else:
                    manager_type = _Manager
            elif not issubclass(cls._MANAGER_TYPE, _Manager):
                raise TypeError(
                    'Invalid manager type %r (it must be _Manager or a subclass).' % cls._MANAGER_TYPE
                )
            else:
                manager_type = cls._MANAGER_TYPE
        
        return manager_type

    def _resolve_propagate_manager_type(self):
        propagate = self.__class__._PROPAGATE_MANAGER_TYPE
        parent = self._mng.parent
        
        # Get first propagation flag defined in parents
        while propagate is None and parent is not None:
            propagate = parent.__class__._PROPAGATE_MANAGER_TYPE
            parent = parent._mng.parent
        
        # Handle project root propagation flag set to None
        propagate = (propagate is not None) and propagate
        
        return propagate

    def __new__(cls, parent, name, **kwargs):
        if parent is None:
            # we are creating a root, the name must be none and kwargs must have a value_store key:
            if name != '':
                raise TypeError(
                    'Cannot create root (object parent == None) with a name that is not empty string.')
            if 'value_store' not in kwargs:
                raise TypeError(
                    'Cannot create root (object parent == None) without "value_store" keyword argument.')
            value_store = kwargs['value_store']
            manager_type = cls._resolve_manager_type(parent)
        else:
            # we are creating an Object, name must not be empty or None and kwargs must be empty:
            if parent is None:
                raise TypeError(
                    'Cannot create an object without parent (Use a Root() as parent if needed).')
            if not isinstance(parent, Object):
                raise TypeError(
                    'parent must be an Object, not a %r' % (type(parent),))
            if not name:
                raise TypeError('Cannot create an object without name.')
            if kwargs:
                raise TypeError(
                    'Cannot create object with more arguments than "parent" and "name".')

            # name must also be a valid python attribute name:
            if '.' in name:
                raise TypeError(
                    'Invalid object name %r (it must be a valid attribute name).' % (name,))
            try:
                exec(name + '=None') in {}
            except Exception:
                raise TypeError(
                    'Invalid object name %r (it must be a valid attribute name).' % (name,))

            manager_type = cls._resolve_manager_type(parent)

            # if not overriden, the value store is the the parent's one
            value_store = cls._create_value_store(parent, name)
            if value_store is None:
                value_store = parent._mng.value_store

        instance = super(Object, cls).__new__(cls)
        instance._mng = manager_type(instance, parent, name, value_store)

        return instance

    def __init__(self, parent, name):
        super(Object, self).__init__()
        self._mng.on_object_init()

    def name(self):
        return self._mng.name

    def oid(self):
        return self._mng.oid()

    def root(self):
        return self._mng.root()

    def touch(self):
        '''
        Force notification that the object has changed.
        '''
        self._mng.touch()

    def child_value_changed(self, child_value):
        '''
        Called when a watched child Value has changed.
        See relations.Param.watched() and values.Value.watch()
        '''
        raise NotImplementedError(
            'missing child_value_changed(child_value) in %s' % (self.oid()))

    def compute_child_value(self, child_value):
        '''
        Called when a ComputeValue child need its value to be computed.

        This happens when a computed value was touched before someone
        asks for its value.

        You must set the result of the computation to the child_value.
        '''
        raise NotImplementedError(
            'missing compute_child_value(child_value) in %s (child name: %r)' % (self.oid(), child_value.name()))

    def _fill_ui(self, ui):
        '''
        Override this to dynamically alter the ui option set on the
        relation holding this Object:
            icon, editor_type, editable, label, hidden, tooltip

        Default is to keep all default value.

        :param ui: the ui info set on the relation holding this Object.
        :return: None
        '''
        pass

#---OLD #FIXME: replace this by a _summary child or a Summary relation...
    def summary(self):
        return None

    def log(self):
        logging.getLogger('kabaret.flow').info(self._mng.pformat())


class SessionObject(Object):
    '''
    The SessionObject overrides its default value store
    with a MemoryValueStore() (all value die when the session ends)

    As the default value store is inherited by parent Objects, the
    whole branch under this one will also be "in memory only".
    '''

    @classmethod
    def _create_value_store(cls, parent, name):
        return MemoryValueStore()


class Root(Object):

    def __new__(cls, value_store):
        return super(Root, cls).__new__(cls, None, '', value_store=value_store)

    def __init__(self, value_store):
        super(Root, self).__init__(None, '')
        self._object_touched_handler = []

    def get_mapped(self, name):
        '''
        Implementing this is needed to have Ref's working with
        source_oid specified as absolute.
        '''
        raise NotImplementedError()

    def add_object_touched_handler(self, handler):
        self._object_touched_handler.append(handler)

    def remove_object_touched_handler(self, handler):
        self._object_touched_handler.remove(handler)

    def object_touched(self, object):
        '''
        Called when any object under this root was touched.
        '''
        for handler in self._object_touched_handler:
            handler(object)


class ThumbnailInfo(Object):
    '''
    This object defines the interface needed to provide "object image view" in
    the GUI.

    You define an object's thumbnail by defining its get_thumbnail_object()
    method and returning a related ThumbnailInfo instance:
        class MyObject(Object):

            _thumbnail = Child(MyThumbnailIn)
    '''

    def is_resource(self):
        '''
        Must return True if your thumbnail source is a resource file.
        If this returns True, does methods need to be implemented:
            get_default_heigth()
            get_label()
            get_resource()
        '''
        raise NotImplementedError()

    def get_resource(self):
        '''
        If is_resource() returns True, this must return a 2d string:
            resource_folder_name, resource_name
        '''
        raise NotImplementedError()

    def is_image(self):
        '''
        Must return True if your thumbnail source is a single image.
        If this returns True, does methods need to be implemented:
            get_default_heigth()
            get_label()
            get_path()
        '''
        raise NotImplementedError()

    def is_sequence(self):
        '''
        Must return True if your thumbnail source is a sequence of images.
        If this returns True, does methods need to be implemented:
            get_default_heigth()
            get_label()
            get_path()
            get_first_and_last()
        '''
        raise NotImplementedError()

    def get_label(self):
        '''
        Returns the label to display on the thumbnail.
        A value of None will use the basename of the thumbnail source file.
        '''
        return None

    def get_path(self):
        '''
        Returns the path of the thumbnail source.
        If is_sequence() returns True, the path must contain a formater for the
        frame number:
            /path/to/my/images.%04d.jpg

        Supported images types are roughtly the same as a standard webbrowser.
        (I.e: no EXP support here.)
        '''
        raise NotImplementedError()

    def get_default_height(self):
        '''
        Returns the default height of the thumbnail when first show in GUI.
        '''
        return 50

    def get_first_last_fps(self):
        '''
        If is_sequence() returns True, this must return the index of the
        first and the last frames, and the frame per second rate
        '''
        raise NotImplementedError()
