'''

    kabaret.flow.map

    Defines the Map Object which has a parametrable ordered list of children.

    The mapped children must derive from the type returned by mapped_type()
    Use the add() and remove() method in Action subclasses to modify the children list.


'''
import logging

from .exceptions import WIPException

from .exceptions import MissingChildError, MappedNameError
from .object import Object
from .relations import OrderedStringSetParam, HashParam
from .injection import injection

class DynamicMap(Object):
    '''
    A DynamicMap contains a procedural list of items.
    This list is computed every time its is needed.

    One must subclass this an implement the methods:
        mapped_names(self, page_num=0, page_size=None)
    and optionnaly:
        _get_mapped_item_type(self, mapped_name)

    '''

    @classmethod
    def mapped_type(cls):
        '''
        Returns the default (which is also be the base) type of the mapped objects.
        Subclasses may override this to specialize the children type.

        Default is to return Object.
        '''
        return Object

    def __init__(self, parent, name):
        super(DynamicMap, self).__init__(parent, name)

    def __len__(self):
        return len(self.mapped_names())

    def mapped_names(self, page_num=0, page_size=None):
        raise NotImplementedError()

    def has_mapped_name(self, name):
        return name in self.mapped_names()

    def mapped_items(self, page_num=0, page_size=None):
        names = self.mapped_names(page_num, page_size)
        ret = []
        for name in names:
            ret.append(self.get_mapped(name))
        return ret

    def columns(self):
        '''
        Returns the list of columns name.
        Subclasses may reimplement this and rows() to provide inline informations
        about the children.

        Default is to return ['Name'] which will contain the mapped object name in rows()
        '''
        return ['Name']

    def page_size(self):
        '''
        Subclasses must override this and current_page_num() to enable paging.
        '''
        return None

    def current_page_num(self):
        '''
        Subclasses must override this and page_size() to enable paging.
        '''
        return 0

    def rows(self):
        '''
        Returns a list of
        ::
            (oid, dict) 
        per child in the order given by mapped_names().
        All dicts must contains the keys found in self.columns() + an optional "_style" key.

        Subclasses should not reimplement this but _fill_row_cells() and _fill_row_style() to
        customize table cells for the mapped items.

        Default behavior is to return the 'name' keys only in rows.

        The _style value in the row must be a dict with those optional keys:
            - icon: the icon in first column
            - background-color: the whole row background-color
            - foreground-color: the row font color

            - <col_name>_<property>: set the <property> style in column <col_name> (example: 'name_icon')
        '''
        # TODO: implement another method for 'thumbnail' view
        # TODO: sort rows
        page_num = self.current_page_num()
        page_size = self.page_size()
        rows = []
        for item in self.mapped_items(page_num, page_size):
            rows.append(self.row(item))
        return rows

    def row(self, item):
        '''
        Returns one of the entry returned by rows:
        ::
            (item_oid, cells_data)
        '''
        row = {}
        self._fill_row_cells(row, item)
        style = {'icon': item.ICON}
        row['_style'] = style
        self._fill_row_style(style, item, row)

        return item.oid(), row

    def _fill_row_cells(self, row, item):
        '''
        Subclasses must override this to fill value for each column returned by columns()
        '''
        row['Name'] = item.name()

    def _fill_row_style(self, style, item, row):
        '''
        Subclasses must override this to configure the style of a given item.
        The 'row' dict contains values for all columns and may be used to decide
        of the style but not to be edited.

        The _style value in the row must be a dict with those optional keys:
            - icon: the icon in first column
            - background-color: the whole row background-color
            - foreground-color: the row font color

            - <col_name>_<property>: set the <property> style in column <col_name> (example: 'name_icon')
        '''
        pass

    def _get_mapped_item_type(self, mapped_name):
        '''
        Returns the type of the given mapped item.
        Default is to return the Map's default mapped type
        (with resolved type injection).

        NB: The GUI assumes that the returned type is a subclass
        of mapped_type().

        '''
        # MEMO:
        # To get a type from a 'fully qualified type name' string, with
        # a fallback to the map's default mapped type:
        # try:
        #     object_type = self._mng.qualified_type_name_to_type(
        #         object_qualified_type_name
        #     )
        # except ImportError:
        #     mapped_type = self.mapped_type()
        #     print(
        #         'WARNING: unable to access type %r. Downgrading to map default type %r' % (
        #             object_qualified_type_name, mapped_type
        #         )
        #     )
        #     object_type = mapped_type
        #
        # ALSO:
        # If you want to support mapped item type injection, you should use:
        #   mapped_type = injection.resolve(
        #       self.mapped_type(), self
        #       )
        # instead of just `self.mapped_type()`
        # Or call the default implementation which does exactly that
        return injection.resolve(
            self.mapped_type(), self
        )

    def _create_child(self, name, object_type):
        '''
        Creates and return a new child object of the given type.
        '''
        object = object_type(self, name)
        self._configure_child(object)
        return object

    def _configure_child(self, child):
        '''
        This can be used by subclass to modify mapped items right
        after their instanciation (by _create_child())

        Default is to do nothing.
        '''
        pass

    def __getitem__(self, name):
        return self.get_mapped(name)

    def get_mapped(self, name):
        '''
        Returns the item mapped under 'name', instanciating it if not yet done.
        '''
        try:
            return self._mng.get_existing_child(name)
        except MissingChildError:
            # This child does not exists yet
            # We will need to create and store it (if it is a registered mapped name)
            pass

        if not self.has_mapped_name(name):
            raise MappedNameError(self.oid(), name)

        object_type = self._get_mapped_item_type(name)
        return self._create_child(name, object_type)

# FIXME: UPDATE THIS IF STILL NEEDED:
    # def _bake_children_type(self):
    #     '''
    #     When the mapped_type's name has changed, every entry in self._items
    #     will have the wrong type stored.
    #     You can call this to update the whole list.

    #     Warning: this will instantiate all children!
    #     '''
    #     new_items = {}
    #     for name in self.mapped_names():
    #         child = self.get_mapped(name)
    #         object_qualified_type_name = child._mng.object_qualified_type_name()
    #         new_items[name] = object_qualified_type_name
    #     self._items.set(new_items)


class Map(DynamicMap):
    '''
    A Map manages a per-instance list of children Objects.

    '''
    _mapped_names = OrderedStringSetParam()
    _mapped_types = HashParam()

    def _item_cmp(self, name_a, name_b):
        '''
        This is used by bake_order.
        '''
        return cmp(name_a, name_b)

    def bake_order(self):
        '''
        Stores a new mapped names order according to the _item_cmp() method.
        This should not be useful but in edge cases like you loaded the order
        from an external source and did not get a satisfying order in mapped
        items.


        Note that this cannot express an order based on anything else than the
        mapped name.

        '''
        names = self.mapped_names()
        names.sort(cmp=self._item_cmp)  # /!\ is this py3 compatible ???
        mn = self._mapped_names
        for score, name in enumerate(names):
            mn.set_score(name, score)

    def mapped_names(self, page_num=0, page_size=None):
        if page_size is not None:
            first = (page_num * page_size)
            last = first + page_size
            return self._mapped_names.get_range(first, last)
        return self._mapped_names.get()

    def add(self, name, object_type=None):
        '''
        Adds an object to the map.
        If provided, object_type must be a subclass of the map's mapped_type (returned by the
        classmethod mapped_type())
        '''
        mapped_type = injection.resolve(
            self.mapped_type(), self
        )
        if object_type is None:
            object_type = mapped_type
        elif not issubclass(object_type, mapped_type):
            raise TypeError(
                'Cannot add %r of type %r to Map %r: not a subclass of %r' % (
                    name, object_type, self.oid(), mapped_type
                )
            )
        if '.' in name:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        try:
            exec(name + '=None') in {}
        except:
            raise TypeError(
                'Invalid object name %r (it must be a valid attribute name).' % (name,))
        if name in dir(self):
            raise ValueError(
                'Cannot add an item "%r", this name is already defined in the class "%s" (%s).' %
                (
                    name, self.__class__.__name__, self._mng.oid()
                )
            )
        if self._mapped_names.has(name):
            raise ValueError(
                'An item %r is already mapped in %r.' %
                (
                    name, self._mng.oid()
                )
            )

        object_qualified_type_name = self._mng.get_qualified_type_name(
            object_type)
        self._mapped_names.add(name, 0)
        self._mapped_types.set_key(name, object_qualified_type_name)

        return self.get_mapped(name)

    def remove(self, name):
        '''
        Removes an Object from the map.
        '''
        self._mapped_names.remove(name)
        self._mapped_types.del_key(name)

        try:
            self._mng.destroy_child(name)
        except MissingChildError:
            # was not yet instantiated, nothing to destroy
            pass

    def clear(self):
        '''
        Remove all Objects from the Map.
        '''
        item_names = self.mapped_names()

        self._mapped_names.revert_to_default()
        self._mapped_types.set({})

        for name in item_names:
            try:
                self._mng.destroy_child(name)
            except MissingChildError:
                # was not yet instantiated, nothing to destroy
                pass
        # The touch() is most of time not wanted yet since a
        # repopulation is probably going to occur.
        # So we let the user decide if he needs it:
        # self.touch()

    def _get_mapped_item_type(self, mapped_name):
        '''
        Returns the type of the given mapped item.
        NB: The GUI assumes that the returned type is a subclass
        of mapped_type().

        '''
        object_qualified_type_name = self._mapped_types.get_key(mapped_name)
        try:
            object_type = self._mng.qualified_type_name_to_type(
                object_qualified_type_name
            )
        except ImportError:
            mapped_type = injection.resolve(
                self.mapped_type(), self
            )
            logging.getLogger('kabaret.ui').debug(
                'WARNING: unable to access type %r. Downgrading to map default type %r' % (
                    object_qualified_type_name, mapped_type
                )
            )
            object_type = mapped_type
        return object_type


class RefsMap(DynamicMap):
    '''
    The RefsMaps lists all the references pointing to a given object
    (default is the RefMap's parent)

    '''

    def ref_of(self):
        '''
        Subclasses may override this to return the object this
        RefsMap lists references to.
        (default is to return this RefsMap's parent)
        '''
        return self._mng.parent

    def ref_source(self, ref):
        '''
        Subclasses may override this to return the object of interest 
        given the ref pointing to self.ref_of()
        (default is to return ref's parent)
        '''
        return ref._mng.parent

    def mapped_names(self, page_num=0, page_size=None):
        '''
        This will use the ref oids as mapped item name.
        Subclasses can override this and call base implementation
        to do a quick and cheap filtering based on ref oids.
        '''
        oids = self.ref_of()._mng.refs()
        return oids

    def get_mapped(self, name):
        '''
        '''
        if not self.has_mapped_name(name):
            raise MappedNameError(self.oid(), name)

        try:
            ref = self._mng.get_object(name)
        except ValueError:
            raise

        return self.ref_source(ref)


class OLD_HASH_Map(Object):

    # stores mapped name to (is_hidden, full_qualified_type_name), used for lazy instantiation
    _items = HashParam()

    @classmethod
    def mapped_type(cls):
        '''
        Returns the default (which is also be the base) type of the mapped objects.
        Subclasses may override this to specialize the children type.

        Default is to return Object.
        '''
        return Object

    def __init__(self, parent, name):
        super(Map, self).__init__(parent, name)

    def __len__(self):
        return self._items.len()

    def mapped_names(self):
        '''
        Ordered list of mapped names 
        '''
        return self._items.keys()

    def has_mapped_name(self, name):
        return self._items.has_key(name)

    # Should not be needed (use has_mapped_oid() instead)
    # def mapped_oids(self):
    #     '''
    #     Ordered list of mappend items oids.
    #     '''
    #     oid = self.oid()
    #     return [ oid+'/'+name for name in self.mapped_names() ]

    def has_mapped_oid(self, oid):
        my_oid = self.oid()
        if not oid.startswith(my_oid + '/'):
            return False
        name = oid[len(my_oid) + 1:]
        if '/' in name:
            # We could actually consider that a child of a mapped is inside this map, no ?
            return False
        return self._items.has_key(name)

    def mapped_items(self, page_num=0, page_size=None, include_hidden=False):
        names = self.mapped_names()
        if page_size:
            first_index = (page_num * page_size) + 1
            names = names[first_index:]

        found = 0
        ret = []
        for name in names:
            is_hidden, object_qualified_type_name = self._get_mapped_info(name)
            if is_hidden and not include_hidden:
                continue
            found += 1
            ret.append(self.get_mapped(name))
            if page_size and found > page_size:
                break
        return ret

    def columns(self):
        '''
        Returns the list of columns name.
        Subclasses may reimplement this and rows() to provide inline informations
        about the children.

        Default is to return ['Name'] which will contain the mapped object name in rows()
        '''
        return ['Name']

    def page_size(self):
        '''
        Subclasses must override this and current_page_num() to enable paging.
        '''
        return None

    def current_page_num(self):
        '''
        Subclasses must override this and page_size() to enable paging.
        '''
        return 0

    def show_hidden(self):
        '''
        Subclasses must override this to enable show_hidden toggle.
        '''
        return False

    def rows(self):
        '''
        Returns a list of (oid, dict) per child in the order given by mapped_names().
        All dicts must contains the keys found in self.columns() + an optional "_style" key.

        Subclasses should not reimplement this but _fill_row_cells() and _fill_row_style() to 
        customize table cells for the mapped items.

        Default behavior is to return the 'name' keys only in rows sorted by creation order.

        The _style value in the row must be a dict with those optional keys:
            - icon: the icon in first column
            - background-color: the whole row background-color
            - foreground-color: the row font color

            - <col_name>_<property>: set the <property> style in column <col_name> (example: 'name_icon')
        '''
        # TODO: implement another method for 'thumbnail' view
        page_num = self.current_page_num()
        page_size = self.page_size()
        show_hidden = self.show_hidden()
        rows = []
        for item in self.mapped_items(page_num, page_size, show_hidden):
            rows.append(self.row(item))
        return rows

    def row(self, item):
        '''
        Returns one of the entry returned by rows: (item_oid, cells_data)
        '''
        row = {}
        self._fill_row_cells(row, item)
        style = {'icon': item.ICON}
        row['_style'] = style
        self._fill_row_style(style, item, row)

        return item.oid(), row

    def _fill_row_cells(self, row, item):
        '''
        Subclasses must override this to fill value for each column returned by columns()
        '''
        row['Name'] = item.name()

    def _fill_row_style(self, style, item, row):
        '''
        Subclasses must override this to configure the style of a given item.
        The 'row' dict contains values for all columns and may be used to decide
        of the style but not to be edited.

        The _style value in the row must be a dict with those optional keys:
            - icon: the icon in first column
            - background-color: the whole row background-color
            - foreground-color: the row font color
            - activate_oid: the oid of a flow.Action to trigger on double-click

            - <col_name>_<property>: set the <property> style in column <col_name> (example: 'name_icon')
        '''
        pass

#---OLD
    def row_icons(self):
        '''
        Return a list of icon name per child.
        (in the order given gy mapped_names())
        '''
        raise WIPException('This is obsolete, use _style column in rows()')
        # icon_name_cache = {}
        # ret = []
        # items = self._items.get() # dont use self.mapped_names() to avoid a value store fetch for each child!
        # for name in sorted(items.keys()):
        #     qualified_type_name = items[name]
        #     try:
        #         icon_name = icon_name_cache[qualified_type_name]
        #     except KeyError:
        #         try:
        #             object_type = self._mng.qualified_type_name_to_type(qualified_type_name)
        #         except ImportError:
        #             icon_name = None
        #         else:
        #             icon_name = object_type.ICON
        #     icon_name_cache[qualified_type_name] = icon_name
        #     ret.append(icon_name)
        # return ret

    def add(self, name, object_type=None):
        '''
        Adds an object to the map.
        If provided, object_type must be a subclass of the map's mapped_type (returned by the
        classmethod mapped_type())
        '''
        # FIXME: This sucks, we need to update it on refactoring, plus subclasses cant protect their reserved
        # keywords :/
        # FIND SOMETHING BETTER !
        if name.startswith('_') or name in (
            'get_mapped', 'add', 'hide', 'remove', 'clear', 'mapped_type',
            'iteritems', 'mapped_names', 'columns', 'rows', 'row_icons',
        ):
            raise ValueError(
                'The name %r is reserved, cannot use it for an item name.' % (name,))

        mapped_type = self.mapped_type()
        if object_type is not None:
            if not issubclass(object_type, mapped_type):
                raise TypeError(
                    'Cannot add %r of type %r to Map %r: not a subclass of %r' % (
                        name, object_type, self.oid(), mapped_type
                    )
                )
        else:
            object_type = mapped_type

        try:
            self._mng.get_existing_child(name)
        except MissingChildError:
            # creating it will set it
            object = self._create_child(name, object_type)
            self._set_mapped_infos(object, hidden=False)
            return object
        else:
            raise ValueError('An item %r is already mapped in %r.' %
                             (name, self._mng.oid()))

    def set_hidden(self, name, hidden):
        mapped_item = self.get_mapped(name)
        self._set_mapped_infos(mapped_item, bool(hidden))
        mapped_item.touch()

    def remove(self, name):
        try:
            self._items.del_key(name)
        except ValueError:
            raise MissingChildError(self.oid(), name)

        try:
            self._mng.destroy_child(name)
        except MissingChildError:
            # was not yet instantiated, nothing to destroy
            pass

    def clear(self):
        item_names = self.mapped_names()
        self._items.set({})
        for name in item_names:
            try:
                self._mng.destroy_child(name)
            except MissingChildError:
                # was not yet instantiated, nothing to destroy
                pass
        # The touch() is most of time not wanted yet since a
        # repopulation is probably going to occur.
        # So we let the user decide if he needs it:
        # self.touch()

    # def _mapped_type_from_qualified_type_name(self, object_qualified_type_name):
    #     try:
    #         object_type = self._mng.qualified_type_name_to_type(object_qualified_type_name)
    #     except ImportError:
    #         mapped_type = self.mapped_type()
    #         print(
    #             'WARNING: unable to access type %r. Downgrading to map default type %r'%(
    #               object_qualified_type_name, mapped_type
    #             )
    #         )
    #         object_type = mapped_type
    #     return object_type

    def _get_mapped_info(self, mapped_name):
        info = self._items.get_key(mapped_name)
        is_hidden = info.startswith('!')
        object_qualified_type_name = info[1:]
        return is_hidden, object_qualified_type_name

    # FIXME: this mapped infos thing is crap.
    # -> we should use another related hash to store the is_hidden info
    # -> and this should be done in a subclass since not always needed.
    def _set_mapped_infos(self, mapped_item, hidden):
        object_qualified_type_name = mapped_item._mng.object_qualified_type_name()
        info = '%s%s' % (hidden and '!' or ' ', object_qualified_type_name)
        self._items.set_key(mapped_item.name(), info)

    def _create_mapped(self, name, object_qualified_type_name):
        try:
            object_type = self._mng.qualified_type_name_to_type(
                object_qualified_type_name
            )
        except ImportError:
            mapped_type = self.mapped_type()
            logging.getLogger('kabaret.flow').debug(
                'WARNING: unable to access type %r. Downgrading to map default type %r' % (
                    object_qualified_type_name, mapped_type
                )
            )
            object_type = mapped_type
        return self._create_child(name, object_type)

    def _create_child(self, name, object_type):
        '''
        Creates a child object of the given type, register it has attribute
        '''
        object = object_type(self, name)
        setattr(self, name, object)
        return object

    def get_mapped(self, name):
        '''
        Returns the item mapped under 'name', instanciating it if not yet done.
        '''
        if 1:
            try:
                return self._mng.get_existing_child(name)
            except MissingChildError:
                # This child does not exists yet
                # We will need to create and store it (if it is a registered mapped name)
                pass

#---OLD
        else:
            raise WIPException(
                ' Not sure why I was doing this instead of just looking in self._mng'
            )
            # #FIXME: this should not return classic attribute
            # try:
            #     # If something here exists by that name, let's hope it's a mapped item and return it
            #     return Object.__getattribute__(self, name)
            # except AttributeError:
            #     # This child does not exists (neither does an attribute of the same name :/ )
            #     # We will need to create and store it
            #     #print(err)
            #     pass

        if not self.has_mapped_name(name):
            # We use to do this:
            # raise MissingChildError(self.oid(), name)
            # but the child is not missing, it is actually not registered....
            # so:
            raise ValueError('No %r mapped item declared under %s' %
                             (name, self.oid()))
            # BN: Shouldn't this raise an Exception from flow.exceptions instead of ValueError ???

        is_hidden, object_qualified_type_name = self._get_mapped_info(name)
        return self._create_mapped(name, object_qualified_type_name)

#---OLD
    def xx__getattr__(self, name):
        raise WIPException(
            'I dont think I use that, nor I think it is a good idea')
        return self.get_mapped(name)

    def _bake_children_type(self):
        '''
        When the mapped_type's name has changed, every entry in self._items
        will have the wrong type stored.
        You can call this to update the whole list.

        Warning: this will instantiate all children!
        '''
        new_items = {}
        for name in self.mapped_names():
            child = self.get_mapped(name)
            object_qualified_type_name = child._mng.object_qualified_type_name()
            new_items[name] = object_qualified_type_name
        self._items.set(new_items)


'''


    - ComputedMap - 

    - Do we force MemoryValueStore ? or do we have two flavors ?
    - New names: ComputedMap and CachedComputedMap
        (the only diff should be the _items config, and the action to refresh)
    - Refactor to match the modifications in Map, and clean it up.



'''


# class RefreshDynamicMapAction(Action):

#     _map = Parent()

#     def get_buttons(self):
#         return self.oid(), [] # no buttons => no dialog, direct exec

#     def run(self, button):
#         self.message.set('Refreshing')
#         self._map._refresh(self.show_progress)
#         self.message.set('Done.')

#     def show_progress(self, nb_step, curr_step, msg):
#         self.message.set('Refreshing: %s (%s/%s'%(nb_step, curr_step, msg))

# class DynamicMap(Map):

#     refresh = Child(RefreshDynamicMapAction)

#     _items = Computed(dict) # overrides base class relation by creating a one with same name

#     @classmethod
#     def _create_value_store(cls, parent, name):
#         return MemoryValueStore()

#     def __init__(self, *args, **kwargs):
#         super(DynamicMap, self).__init__(*args, **kwargs)
#         self._refreshing = False
#         self._refresh(self.refresh.show_progress)

#     def child_touched(self, child):
#         '''
#         !!! Subclasses MUST call this base implementation if they override !!!
#         '''
#         super(DynamicMap, self).child_touched(child)

#     def compute_child_value(self, child_value):
#         if child_value == self._items:
#             if not self._refreshing:# and self._auto_refresh:
#                 self._refresh(self.refresh.show_progress)
#         else:
#             super(DynamicMap, self).compute_child_value(child_value)

#     def _refresh(self, progress=None):
#         self._refreshing = True

#         progress = progress or (lambda nb_step, curr_step, msg: None)

#         self.clear()

#         entries = self._fetch_entries(progress)

#         nb = len(entries)
#         for i, (name, data) in enumerate(entries.iteritems()):
#             progress(nb, i, 'Creating %r'%(name,))
#             #print('--->', (name,))
#             item = self.add(name, self._get_child_type(name, data))
#             self._configure_child(item, data)

#         self._refreshing = False
#         self._set_clean()
#         self.touch()

#     def _fetch_entries(self, progress):
#         '''
#         Subclasses must implement this to return a dict of child_name:child_data

#         The child_infos will later be passed to self._configure_child().
#         '''
#         raise NotImplementedError()

#     def _get_child_type(self, name, data):
#         '''
#         Subclass may override this to refine each new child type.
#         Default is to use mapped_type()
#         '''
#         return self.mapped_type()

#     def _configure_child(self, child, data):
#         '''
#         Subclasses must implement this to configure a newly created child.

#         The data arguments is the one returned for this child by _fetch_entries().
#         '''
#         raise NotImplementedError()


# class RefreshDirtyMapAction(Action):

#     _map = Parent()

#     def get_buttons(self):
#         return self.oid(), [] # no buttons => no dialog, direct exec

#     def run(self, button):
#         self.message.set('Forcing Refresh.')
#         self._map._set_clean()
#         self._map.touch()
#         self.message.set('Done.')

#     def show_progress(self, nb_step, curr_step, msg):
#         self.message.set('Refreshing: %s (%s/%s'%(nb_step, curr_step, msg))


# class DirtyMap(Map):
#     '''
#     A DirtyMap updates it content every time it is read (by calling the rows() method).
#     (In a similarly way a Dirty relation updates at every value get)

#     Subclasses MUST call self._refresh() at the beginning of rows() when overriding it.
#     '''

#     refresh = Child(RefreshDirtyMapAction)

#     @classmethod
#     def _create_value_store(cls, parent, name):
#         return MemoryValueStore()

#     def __init__(self, *args, **kwargs):
#         self._refreshing = False
#         super(DirtyMap, self).__init__(*args, **kwargs)
#         self._loaded = False

#     def rows(self):
#         '''
#         BEWARE: subclasses overridding this MUST call self._refresh(self.refresh.show_progress)
#         before accessing the items to fetch the rows data.
#         '''
#         self._refresh(self.refresh.show_progress)
#         return super(DirtyMap, self).rows()

#     def _refresh(self, progress=None):
#         self._refreshing = False#True
#         self._loaded = True

#         progress = progress or (lambda nb_step, curr_step, msg: None)

#         self.clear()

#         entries = self._fetch_entries(progress)

#         nb = len(entries)
#         for i, (name, data) in enumerate(entries.iteritems()):
#             progress(nb, i, 'Creating %r'%(name,))
#             #print('--->', (name,))
#             item = self.add(name, self._get_child_type(name, data))
#             self._configure_child(item, data)

#         self._refreshing = False

#     def _fetch_entries(self, progress):
#         '''
#         Subclasses must implement this to return a dict of child_name:child_data

#         The child_infos will later be passed to self._configure_child().
#         '''
#         raise NotImplementedError()

#     def _get_child_type(self, name, data):
#         '''
#         Subclass may override this to refine each new child type.
#         Default is to use mapped_type()
#         '''
#         return self.mapped_type()

#     def _configure_child(self, child, data):
#         '''
#         Subclasses must implement this to configure a newly created child.

#         The data arguments is the one returned for this child by _fetch_entries().
#         '''
#         raise NotImplementedError()

#     def get_mapped(self, name):
#         if not self._loaded:
#             print('!!!!!!!!!!!!!!')
#             print('!!!!!!!!!!!!!! AUTO FIRST REFRESH S', self._items.get())
#             print('!!!!!!!!!!!!!!')
#             self._refresh()
#             print('!!!!!!!!!!!!!! AUTO FIRST REFRESH E', self._items.get())
#         return super(DirtyMap, self).get_mapped(name)
#
