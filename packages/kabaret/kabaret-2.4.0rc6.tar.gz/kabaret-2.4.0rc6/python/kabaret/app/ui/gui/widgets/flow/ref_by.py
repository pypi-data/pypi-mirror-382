from qtpy import QtWidgets


class AutoHeightTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, *args, **kwargs):
        self._min_h = 100
        super(AutoHeightTreeWidget, self).__init__(*args, **kwargs)

        # self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum )

    def updateAutoHeight(self):
        height = self.header().height() + 2

        for it in QtWidgets.QTreeWidgetItemIterator(self, QtWidgets.QTreeWidgetItemIterator.All):
            height += self.visualItemRect(it.value()).height()

        height = max(self._min_h, height)
        self.setFixedHeight(height)


class RefByWidget(QtWidgets.QWidget):

    def __init__(self, parent, oids, leaf_callback, group_callback, hide_callback=None):
        super(RefByWidget, self).__init__(parent)

        self.oids = []

        self._is_open = False

        self._open_bt = QtWidgets.QToolButton(self)
        self._open_bt.setText('Show References')
        self._open_bt.clicked.connect(self.toggle_open)

        self._is_compact = False

        self._compact_cb = QtWidgets.QCheckBox(self)
        self._compact_cb.setText('Compact')
        self._compact_cb.setChecked(self._is_compact)
        self._compact_cb.toggled.connect(self._on_compact_cb)

        self._tree = AutoHeightTreeWidget(self)
        self._tree.setColumnCount(1)
        self._tree.setHeaderLabels(['Connected to'])
        self._tree.itemDoubleClicked.connect(self._on_tree_dble_click)
        self._tree.hide()

        hlo = QtWidgets.QHBoxLayout()
        hlo.addWidget(self._open_bt)
        hlo.addWidget(self._compact_cb)
        hlo.addStretch(100)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addLayout(hlo)
        self.layout().addWidget(self._tree)

        self._leaf_callback = leaf_callback
        self._group_callback = group_callback
        self._hide_callback = hide_callback

        self.set(oids)

        self.open()

    def set_togglable(self, b):
        self._open_bt.setVisible(b)

    def is_open(self):
        return self._is_open

    def is_compact(self):
        return self._is_compact

    def set(self, oids):
        self.oids = oids
        if oids:
            self._open_bt.setText('Show %d References' % (len(self.oids),))
        else:
            self._open_bt.setText('No Reference.')
        self.refresh()

    def _load_tree(self):

        tree = dict(oid='', name='', children=[])
        oid_to_item = {'': tree}

        def add_item(oid):
            try:
                return oid_to_item[oid]
            except KeyError:
                pass

            me = dict(oid=oid, name=oid.rsplit('/', 1)[-1], children=[])
            oid_to_item[oid] = me
            parent_oid, name = oid.rsplit('/', 1)
            parent = add_item(parent_oid)
            parent['children'].append(me)
            return me

        for oid in self.oids:
            add_item(oid)

        def compact_leaves(item):
            children = item['children']
            if not children:
                return
            if len(children) == 1:
                child = children[0]
                if not child['children']:
                    item['oid'] = child['oid']
                    item['name'] += '.' + child['name']
                    item['children'] = []
            for child in item['children']:
                compact_leaves(child)

        compact_leaves(tree)

        if self._is_compact:
            def compact_items(item):
                children = item['children']
                if not children:
                    return

                if len(children) == 1:
                    child = children[0]
                    if child['children']:
                        item['oid'] = child['oid']
                        item['name'] += '/' + child['name']
                        item['children'] = child['children']
                        compact_items(item)
                else:
                    for child in item['children']:
                        compact_items(child)

            compact_items(tree)

        def create_tree_item(parent, item):
            oid = item['oid']
            if oid:
                name = item['name']
                tree_item = QtWidgets.QTreeWidgetItem(parent, [name])
                tree_item.flow_id = oid
                if item['children']:
                    tree_item.action = self._group_callback
                else:
                    tree_item.action = self._leaf_callback
            else:
                tree_item = parent
            for child in item['children']:
                create_tree_item(tree_item, child)

        create_tree_item(self._tree, tree)

        self._tree.expandAll()
        self._tree.updateAutoHeight()

    def clear(self):
        self._tree.clear()

    def refresh(self):
        self.clear()
        self._load_tree()

    def open(self):
        self._is_open = True
        self._tree.show()
        self._open_bt.setText('Hide References')
        self._compact_cb.show()
        self.refresh()
        if self._hide_callback:
            self._hide_callback(False)

    def close(self):
        self._is_open = False
        self._tree.hide()
        self._open_bt.setText('Show %s References' % (len(self.oids, )))
        self._compact_cb.hide()
        self.refresh()
        if self._hide_callback:
            self._hide_callback(True)

    def toggle_open(self):
        if self._is_open:
            self.close()
        else:
            self.open()

    def _on_compact_cb(self, b):
        self._is_compact = b and True or False
        self._tree.clear()
        self._load_tree()

    def set_compact(self, b):
        self._is_compact = b and True or False
        self._compact_cb.setChecked(b)
        self._tree.clear()
        self._load_tree()

    def _on_tree_dble_click(self, item, column):
        item.action(item.flow_id)
