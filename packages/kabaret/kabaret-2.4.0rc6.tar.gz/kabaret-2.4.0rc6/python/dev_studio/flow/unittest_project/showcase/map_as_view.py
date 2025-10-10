

from kabaret import flow



class Item(flow.Object):

    status = flow.Param('NYS').watched()

    def child_value_changed(self, child_value):
        if child_value is self.status:
            self.touch()

class BackLog(flow.DynamicMap):

    @classmethod
    def mapped_type(cls):
        return Item

    def mapped_names(self, page_num=0, page_size=None):
        return [ 'Item{}'.format(i) for i in range(10) ]

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Status'] = item.status.get()

class Filtered(flow.DynamicMap):

    _group = flow.Parent()

    @classmethod
    def mapped_type(cls):
        return Item

    def source_map(self):
        return self._group.get_backlog()

    def mapped_names(self, page_num=0, page_size=None):
        src = self.source_map()
        return [
            i.name()
            for i in src.mapped_items(page_num, page_size)
            if int(i.name()[-1])%2
        ]

    def get_mapped(self, name):
        return self.source_map().get_mapped(name)

    def columns(self):
        return ['Name', 'Status']

    def _fill_row_cells(self, row, item):
        row['Name'] = item.name()
        row['Status'] = item.status.get()

class SubGroup(flow.Object):

    _group = flow.Parent()

    another_view = flow.Child(Filtered)

    def get_backlog(self):
        return self._group.get_backlog()

class MapAsViewGroup(flow.Object):

    doc = flow.Label(
        'A DynamicMap can also be used as a "View" on another Map, '
        'i.e to filter a map or gather item from different parents...<br>'
        'In this example, the "backlog" contains item and the "filtered" '
        'shows only the even numbered items from the backlog.<br>'
        '<ul>'
        '<li>'
            'Double clicking an item in "filtered" opens the page of the '
            '"backlog" item.'
        '</li>'
        '<li>'
            'Changing the status of an item in "backlog" update both '
            'map editors.'
        '</li>'
        '<li>'
            'Changing the status of an item in "backlog" also update a '
            'map editor under another group (see sub_group).'
        '</li>'
        '</ul>'
    )

    def get_backlog(self):
        return self.backlog

    backlog = flow.Child(BackLog)
    filtered = flow.Child(Filtered)
    sub_group = flow.Child(SubGroup)