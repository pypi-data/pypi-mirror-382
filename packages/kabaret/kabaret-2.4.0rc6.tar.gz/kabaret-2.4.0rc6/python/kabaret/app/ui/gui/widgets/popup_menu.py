from qtpy import QtWidgets, QtGui, QtCore


class PopupMenuItem(QtWidgets.QListWidgetItem):

    def __init__(self, text, action=None):
        super(PopupMenuItem, self).__init__(text)
        self._action = action


class PopupMenuListWidget(QtWidgets.QListWidget):

    def sizeHint(self):
        s = QtCore.QSize()
        margins = self.contentsMargins()
        count = self.count()
        list_size = count * (self.sizeHintForRow(0)+self.spacing()*2) + margins.top() + margins.bottom()

        # Cannot explain why I add more spacing but it's needed for avoiding unnecessary scrollbar
        s.setHeight(list_size+self.spacing()*2)
        s.setWidth(self.sizeHintForColumn(0) + margins.left() + margins.right())
        return s


class PopupMenu(QtWidgets.QDialog):

    def __init__(self, parent):
        super(PopupMenu, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Popup)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(15, 3, 5, 3)
        layout.setSpacing(0)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Base, palette.color(QtGui.QPalette.Window))
        self.setPalette(palette)

        self.setLayout(layout)

        self._lists = []
        self._add_new_list()

    def addAction(self, text, icon=None, callback=None):
        action = QtGui.QAction(self)
        item = PopupMenuItem(text, action)
        item.setData(QtCore.Qt.UserRole, text)
        self._lists[-1].addItem(item)
        if callback:
            action.triggered.connect(callback)
        if icon:
            item.setIcon(icon)
        return action

    def addItem(self, text, icon=None):
        item = PopupMenuItem(text)
        item.setData(QtCore.Qt.UserRole, text)
        self._lists[-1].addItem(item)
        if icon:
            item.setIcon(icon)
        return item

    def addSeparator(self):
        if not self._lists[-1].count():
            return
        list = self._lists[-1]
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.NoItemFlags)
        frame = QtWidgets.QFrame(list)
        frame.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Plain)
        list.addItem(item)
        list.setItemWidget(item, frame)

    def addMenu(self):
        if not self._lists[-1].count():
            return
        frame = QtWidgets.QFrame(self)
        frame.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Plain)
        self.layout().addWidget(frame)
        self._add_new_list()

    def _add_new_list(self):
        list = PopupMenuListWidget(self)
        list.setSpacing(3)
        list.setFrameStyle(QtWidgets.QFrame.NoFrame)
        list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        list.itemClicked.connect(self._onItemClicked)

        self._lists.append(list)
        self.layout().addWidget(list, 1)

    def clear(self):
        layout = self.layout()
        child = layout.takeAt(0)
        while child:
            widget = child.widget()
            if isinstance(widget, QtWidgets.QListWidget):
                child.widget().clear()
            child = layout.takeAt(0)
            widget.deleteLater()
        self._lists = []
        self._add_new_list()

    def popup(self, pos):
        for list in self._lists:
            size = list.sizeHint()
            list.setMinimumWidth(size.width())
            list.setMaximumHeight(size.height())
        self.move(pos)
        self.show()
        self.adjustSize()

    def _onItemClicked(self, item):
        if item._action:
            item._action.trigger()
            self.setVisible(False)
