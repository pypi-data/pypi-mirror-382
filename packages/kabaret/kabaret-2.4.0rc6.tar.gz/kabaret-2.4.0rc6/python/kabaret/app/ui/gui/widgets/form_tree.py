from qtpy import QtWidgets, QtCore, QtGui
import kabaret.app.resources
import kabaret.app.ui.gui.styles


class FormItem(QtWidgets.QTreeWidgetItem):
    '''
    Base class for all Form items (FormFields and internal stuff)

    Sublcass must implement the build() method to build the item widgets.
    '''

    _LAST_EXPANDED_STATES = {}
    _DEFAULT_EXPANDED_STATE = False

    def build(self):
        raise NotImplementedError()

    def level(self):
        p = self.parent()
        if p is None:
            return 0
        return p.level()+1

    def _pref_id(self):
        """ Returns an id used to manage preferences """
        fid = ''
        p = self.parent()
        if p is not None:
            fid = p._pref_id() + '.'
        fid += self.text(0)
        return fid

    def auto_expand(self):
        try:
            expanded = self.__class__._LAST_EXPANDED_STATES[self._pref_id()]
        except KeyError:
            expanded = self.__class__._DEFAULT_EXPANDED_STATE
        # if expanded:
        #     self.ensure_children_built()
        self.setExpanded(expanded)

    #FIXME: this triplet setExpanded/expanded/collapsed should be reduced to setExpanded only.
    def setExpanded(self, b):
        super(FormItem, self).setExpanded(b)
        self.__class__._LAST_EXPANDED_STATES[self._pref_id()] = b

    def expanded(self):
        self.__class__._LAST_EXPANDED_STATES[self._pref_id()] = True

    def collapsed(self):
        self.__class__._LAST_EXPANDED_STATES[self._pref_id()] = False

    def clicked(self, col):
        pass

    def activated(self, col):
        pass

    def apply_edit(self):
        pass

    def apply_all_edits(self):
        for i in range(self.childCount()):
            child = self.child(i)
            child.apply_all_edits()
        self.apply_edit()


class _PreloadItem(FormItem):
    '''
    The _PreloadItem is used by FormField to show a [+] (has children indicator) before
    having actually build the children.
    '''

    def __init__(self, parent):
        super(_PreloadItem, self).__init__(parent, ['_PRELOAD_ITEM_'])

    def build(self):
        '''Nothing to build here...'''
        pass

class FormField(FormItem):
    '''
    Base Class for all Form fields.
    FormField is responsible of managing its children:
        delete_all_children()
        build_children()
        ensure_children_built()

    The build_children() method must be implemented by subclasses.


    '''

    def __init__(self, parent):
        super(FormField, self).__init__(parent)
        self._preload_child = None
        self._children_built = False
        # self.setFlags(QtCore.Qt.NoItemFlags)

        if kabaret.app.ui.gui.styles.StylesManager.get().get_default_style().get_property('alternate_child_color', False):
            if self.level():
                color = self.parent().background(0).color()
                if self.level() % 2 == 0:
                    color = QtGui.QColor.fromHsl(color.hue(), color.saturation(), max(0, color.lightness()-5))
                    self.setBackground(0, color)
                else:
                    color = QtGui.QColor.fromHsl(color.hue(), color.saturation(), min(255, color.lightness()+10))
                    self.setBackground(0, color)
            else:
                self.setBackground(0, self.treeWidget().palette().color(QtGui.QPalette.Window))

        self.build()
        self.auto_expand()

    def setExpanded(self, b):
        if b:
            self._clear_preload_child()
        super(FormField, self).setExpanded(b)

    def expanded(self):
        self.ensure_children_built()
        super(FormField, self).expanded()

    def update_height(self, w):
        size = QtCore.QSize(32, 32).expandedTo(w.sizeHint())
        self.setSizeHint(1, size)
        self.treeWidget().scheduleDelayedItemsLayout()

    def show_may_have_children(self):
        if self._children_built:
            return
        if self._preload_child is None:
            self._preload_child = _PreloadItem(self)

    def _clear_preload_child(self):
        if self._preload_child is not None:
            index = self.indexOfChild(self._preload_child)
            c = self.takeChild(index)
            del c
            self._preload_child = None

    def delete_all_children(self):
        while self.childCount():
            c = self.takeChild(0)
            del c
        self._children_built = False

    def build_children(self):
        raise NotImplementedError()

    def ensure_children_built(self):
        if not self._children_built:
            self._clear_preload_child()
            self.build_children()
            self._children_built = True

    def wrap(self, w, box_direction=QtWidgets.QBoxLayout.LeftToRight, additionnal_widget=None):
        """
        :return: a widget with a QBoxLayout containing the widget w and the item name
        """
        tree = self.treeWidget()
        wrapper = QtWidgets.QWidget(tree)
        layout = QtWidgets.QBoxLayout(box_direction, wrapper)
        layout.setContentsMargins(0, 4, 0, 6)
        layout.setSpacing(0)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setContentsMargins(2, 0, 0, 0)
        hlayout.setSpacing(10)

        title = QtWidgets.QWidget(wrapper)
        title.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QtWidgets.QLabel()
        icon_lbl.setPixmap(self._get_config_icon().pixmap(QtCore.QSize(32, 32)))
        icon_lbl.setAlignment(QtCore.Qt.AlignVCenter)
        hlayout.addWidget(icon_lbl)
        title_lbl = QtWidgets.QLabel(self._label)
        title_lbl.setAlignment(QtCore.Qt.AlignVCenter)
        title_lbl.setWordWrap(True)
        hlayout.addWidget(title_lbl)
        if additionnal_widget:
            hlayout.addWidget(additionnal_widget)
        hlayout.addStretch()
        title.setLayout(hlayout)
        title.setMinimumSize(32, 32)

        layout.addWidget(title)
        layout.addWidget(w)
        wrapper.setLayout(layout)
        return wrapper

    def setItemWidget(self, col, w, alignment=QtCore.Qt.AlignLeft):
        tree = self.treeWidget()
        tree.setItemWidget(self, col, w)
        if col == 0:
            self.setFirstColumnSpanned(True)
        self.setTextAlignment(col, alignment)


class FormTree(QtWidgets.QTreeWidget):

    def __init__(self, parent):
        super(FormTree, self).__init__(parent)
        self.setProperty('form_tree', True)

        self.setHeaderLabels(('Name', 'Value'))
        # self.setRootIsDecorated(False)
        self.setExpandsOnDoubleClick(False)

        self.itemClicked.connect(self._on_clicked)
        self.itemActivated.connect(self._on_activated)
        self.itemExpanded.connect(self._on_expanded)
        self.itemCollapsed.connect(self._on_collapsed)

        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setAutoScroll(False)

        h = self.header()
        h.setSectionResizeMode(0, self.header().ResizeMode.ResizeToContents)
        h.hide()

        self.setIndentation(30)

        stylesheet = \
            '''
            QTreeView[form_tree="true"] {
                border: 0;
                outline: none;
                background: palette(window);
            }
            QTreeView[form_tree="true"]::item:selected {
                border: none;
            }
            QTreeView[form_tree="true"]::item:focus {
                border: none;
            }
            QTreeView[form_tree="true"]::item:hover {
                border: none;
                color: palette(highlight);
            }
            '''
        self.setStyleSheet(stylesheet)

        if kabaret.app.ui.gui.styles.StylesManager.get().get_default_style().get_property('alternate_child_color', False):
            self.drawRow = self.drawRow_alternate_child_color

    def _on_clicked(self, item, col):
        item.clicked(col)

    def _on_activated(self, item, col):
        item.activated(col)

    def _on_expanded(self, item):
        item.expanded()

    def _on_collapsed(self, item):
        item.collapsed()

    def keyPressEvent(self, event):
        '''
        Reimplemented to disable the enter key -> activate item
        '''
        if event.key() & QtCore.Qt.Key_Enter:
            event.accept()
        else:
            super(FormTree, self).keyPressEvent(event)

    def apply_all_edits(self):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            item.apply_all_edits()

    def drawRow_alternate_child_color(self, *args, **kwargs):
        '''
        This is needed because Qt4 has a bug when overriding drawRow
        '''
        painter = args[0]
        option = args[1]
        index = args[2]
        item = self.itemFromIndex(index)

        margin_rect = QtCore.QRect(option.rect)
        margin_rect.setX((item.level() - 1.5) * self.indentation())
        margin_rect.setWidth(self.indentation())
        item_rect = QtCore.QRect(option.rect)
        item_rect.setX(margin_rect.right())

        parent = item.parent()
        if parent:
            painter.fillRect(item_rect, item.background(0))
            while parent:
                painter.fillRect(margin_rect, parent.background(0))
                margin_rect.moveLeft((parent.level() - 1.5) * self.indentation())
                parent = parent.parent()

        super(FormTree, self).drawRow(*args, **kwargs)
