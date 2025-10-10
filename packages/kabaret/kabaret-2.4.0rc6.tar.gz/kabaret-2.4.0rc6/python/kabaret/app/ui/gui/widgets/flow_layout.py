

from qtpy import QtCore, QtWidgets
import shiboken6


class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=0):
        super(FlowLayout, self).__init__(parent)
 
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
 
        self.setSpacing(spacing)
 
        self.itemList = []
 
    def __del__(self):
        self.clear()

    def clear(self):
        while self.count():
            child = self.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addItem(self, item):
        self.itemList.append(item)

    def removeItem(self, item):
        self.itemList.remove(item)
 
    def count(self):
        return len(self.itemList)
 
    def itemAt(self, index):
        if index >= len(self.itemList):
            return None

        if index >= 0:
            return self.itemList[index]

        return None
 
    def takeAt(self, index):
        """
        Inspired from https://codebrowser.dev/qt5/qtbase/src/widgets/kernel/qboxlayout.cpp.html
        :param index:
        :return:
        """
        if index < 0 or index >= len(self.itemList):
            return None
        item = self.itemList.pop(index)

        l = item.layout()
        if l and  l.parent() is self:
            # sanity check in case the user passed something weird to QObject::
            l.setParent(None)

        if shiboken6.isValid(self) is not False:
            self.invalidate()
        return item

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))
 
    def hasHeightForWidth(self):
        return True
 
    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height
 
    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)
 
    def sizeHint(self):
        return self.minimumSize()
 
    def minimumSize(self):
        size = QtCore.QSize()
 
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
 
        margin = self.contentsMargins()
        size += QtCore.QSize(margin.left()+margin.right(), margin.top()+margin.bottom())
        return size
 
    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
 
        for item in self.itemList:
            #wid = item.widget()
            spaceX = self.spacing()#+wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing()#+wid.style().layoutSpacing(QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
 
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
 
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
 
        return y + lineHeight - rect.y()
