'''


'''


class Navigator(object):

    def __init__(self, session, root_oid=None, current_oid=None):
        super(Navigator, self).__init__()

        self.session = session

        self._root_oid = root_oid
        self._current_oid = current_oid or root_oid
        self._prev_list = []
        self._next_list = []

        self._on_current_changed = []  # list of callables
        #---OLD self._on_current_corrected = [] # list of callbles

        self._on_list_changed = []  # list of callables

        self._create_view_function = None

        self.refresh()

    def add_on_current_changed(self, callable):
        '''callable must accept no args'''
        self._on_current_changed.append(callable)

    def remove_on_current_changed(self, callable):
        self._on_current_changed.remove(callable)

#---OLD
    # def add_on_current_corrected(self, callable):
    #     self._on_current_corrected.append(callable)

    # def remove_on_current_corrected(self, callable):
    #     self._on_current_corrected.remove(callable)

    # def correct_current_oid(self, oid):
    #     self._current_oid = oid
    #     for callable in self._on_current_corrected:
    #         callable(self._current_oid)

    def add_on_list_changed(self, callable):
        '''callable must accept no args'''
        self._on_list_changed.append(callable)

    def remove_on_list_changed(self, callable):
        self._on_list_changed.remove(callable)

    def set_create_view_function(self, f):
        '''
        The callable f must accept one argument:
                the oid to load on the new view.
        '''
        self._create_view_function = f

    def create_view(self, oid):
        if self._create_view_function is None:
            raise Exception(
                'Could not create a new view, set_create_view_function() '
                'never called :/'
            )
        self._create_view_function(oid)

    def refresh(self):
        ''' -> goto current oid'''
        self.goto(self.current_oid())

    def root_oid(self):
        return self._root_oid

    def apply_new_root_oid(self, oid):
        self._root_oid = oid

    def current_oid(self):
        return self._current_oid

    def _apply_new_current_oid(self, oid):
        self._current_oid = self.session.cmds.Flow.resolve_path(oid)
        for callable in self._on_current_changed:
            callable()

    def goto(self, oid, new_view=False):
        if new_view:
            self.create_view(oid)
            return

        self._next_list = []
        if self._current_oid and oid != self._current_oid:
            self._prev_list.append(self._current_oid)
        self._apply_new_current_oid(oid)

    def history_oids(self):
        return self._prev_list

    def apply_history_oids(self, prev_list):
        self._prev_list = prev_list
        for callable in self._on_list_changed:
            callable()

    def has_prev(self):
        return self._prev_list and True or False

    def goto_prev(self):
        if not self._prev_list:
            return
        self._next_list.append(self._current_oid)
        oid = self._prev_list.pop(-1)
        self._apply_new_current_oid(oid)

    def has_next(self):
        return self._next_list and True or False

    def goto_next(self):
        if not self._next_list:
            return
        self._prev_list.append(self._current_oid)
        oid = self._next_list.pop(-1)
        self._apply_new_current_oid(oid)

    def has_parent(self):
        if self.root_oid():
            return self._current_oid != self.root_oid()
        return '/' in self._current_oid  # .lstrip('/')

    def goto_parent(self, new_view=False):
        self.goto_parent_of(self._current_oid, new_view)

    def goto_parent_of(self, oid, new_view=False):
        skip_maps = True
        parent_oid = self.session.cmds.Flow.get_parent_oid(oid, skip_maps)
        self.goto(parent_oid, new_view)

    def goto_related(self, relation_name, resolve_ref=True, new_view=False):
        related_oid = self.session.cmds.Flow.get_related_oid(
            self._current_oid, relation_name, resolve_ref
        )
        self.goto(related_oid, new_view)

    def goto_root(self):
        self.goto(self.root_oid())

    def split_current_oid(self):
        skip_maps = True
        label_to_oid = self.session.cmds.Flow.split_oid(
            self._current_oid, skip_maps, self._root_oid
        )
        return label_to_oid

    def get_navigable_oids(self, oid, send_to):
        return self.session.cmds.Flow.get_navigable_oids(oid)
