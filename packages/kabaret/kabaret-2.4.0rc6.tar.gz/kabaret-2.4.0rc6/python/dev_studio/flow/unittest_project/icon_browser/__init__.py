from kabaret.flow import (
    values,
    Object, DynamicMap, ThumbnailInfo,
    Action, ConnectAction,
    ChoiceValueSetAction, ChoiceValueSelectAction,
    Child, Parent, Computed, Connection,
    Param, IntParam, BoolParam, HashParam,
    Label
)

from kabaret.app import resources


class IconThumbnailInfo(ThumbnailInfo):

    _icon = Parent()
    _folder = Parent(2)

    def is_resource(self):
        return True

    def get_resource(self):
        return self._folder.get_icon_ref(self._icon)


class Icon(Object):

    icon_name = Param().ui(editable=False)
    _thumbnail_info = Child(IconThumbnailInfo)

    def get_thumbnail_object(self):
        return self._thumbnail_info


class Icons(DynamicMap):

    _icon_folder = Parent()

    @classmethod
    def mapped_type(cls):
        return Icon

    def __init__(self, parent, name):
        super(Icons, self).__init__(parent, name)
        self._items = dict(
            [
                ('i_' + n.replace('.', '_').replace('-', '_'), n)
                for n in resources.list_folder(self.folder_name())
            ]
        )

    def mapped_names(self, page_num=0, page_size=None):
        return list(self._items.keys())

    def _create_child(self, name, object_type):
        '''
        Creates and return a new child object of the given type.
        '''
        child = object_type(self, name)
        icon_name = self._items[name]
        child.icon_name.set(icon_name)
        return child

    def folder_name(self):
        return self._icon_folder.folder_name.get()

    def get_icon_ref(self, icon_item):
        folder_name = self.folder_name()
        icon_name = icon_item.icon_name.get()
        return (folder_name, icon_name)

    def columns(self):
        return ['Name', 'Ref']

    def _fill_row_cells(self, row, item):
        row['Name'] = ''
        row['Ref'] = repr((self.folder_name(), item.icon_name.get()))

    def _fill_row_style(self, style, item, row):
        style['icon'] = self.get_icon_ref(item)


class IconFolder(Object):

    folder_name = Param().ui(editable=False)

    icons = Child(Icons).ui(expanded=True)


class IconFolders(DynamicMap):

    @classmethod
    def mapped_type(cls):
        return IconFolder

    def __init__(self, parent, name):
        super(IconFolders, self).__init__(parent, name)
        self._items = dict(
            [
                (n.replace('.', '_').replace('-', '_'), n)
                for n in resources.get_folder_names()
            ]
        )

    def mapped_names(self, page_num=0, page_size=None):
        return list(self._items.keys())

    def _create_child(self, name, object_type):
        '''
        Creates and return a new child object of the given type.
        '''
        child = object_type(self, name)
        folder_name = self._items[name]
        child.folder_name.set(folder_name)
        return child


class IconBrowserGroup(Object):

    doc = Label('<H2>Here you can browse icons from the resources folder.</H2>')
    folder_names = Child(IconFolders).ui(expanded=True)
