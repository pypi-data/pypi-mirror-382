import six
from qtpy import QtWidgets, QtCore



class EatEnterKeys(QtCore.QObject):

    def eventFilter(self, obj, evt):
        if evt.type() == QtCore.QEvent.KeyPress:
            key = evt.key()
            if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
                return True  # mark the event as handled
        return False


class IgnoreMouseButton(QtCore.QObject):

    def __init__(self, parent):
        super(IgnoreMouseButton, self).__init__(parent)

        self.buttons = QtCore.Qt.MidButton
        self._events = (
            QtCore.QEvent.MouseButtonPress,
            QtCore.QEvent.MouseMove,
            QtCore.QEvent.MouseButtonRelease,
        )

    def eventFilter(self, obj, e):
        if e.type() in self._events and e.buttons() & self.buttons:
            e.ignore()
            return False # mark handled
        return False

class MouseResizer(QtCore.QObject):
    '''
    Resize the widget with self.button (Defaults to QtCore.Qt.MidButton).
    Optional on_resized(target) is called after each resize.
    
    If aspect_ratio is not None, both horizontal and vertical are considered True.


    '''
    def __init__(self, target, on_resized=None, horizontal=True, vertical=True, aspect_ratio=None):
        super(MouseResizer, self).__init__(target)
        self.propagate_events = True
        
        self._on_resized = on_resized
        self.horizontal = horizontal
        self.vertical = vertical
        self.aspect_ratio = aspect_ratio

        self.target = target
        self.down_pos = None
        self.down_size = None

        self.buttons = QtCore.Qt.MidButton
        self.min_w = 32
        self.min_h = 32

        self._has_resized = None
        self._mns = self.target.minimumSize()
        self._mxs = self.target.maximumSize()
        self._sp = self.target.sizePolicy()

    def _do_on_resized(self):
        if self._on_resized is None:
            return
        self._on_resized(self.target)

    def apply_resize(self, from_width, from_height, x_move, y_move):
        if self.aspect_ratio is not None:
            h = max(
                self.min_h,
                from_height+y_move
            )
            w = int(h*self.aspect_ratio)
            self.target.setFixedSize(w,h)
        else:
            if self.horizontal:
                self.target.setFixedWidth(
                    max(
                        self.min_w,
                        from_width+x_move
                    )
                )
            if self.vertical:
                self.target.setFixedHeight(
                    max(
                        self.min_h,
                        from_height+y_move
                    )
                )
        self._do_on_resized()

    def eventFilter(self, obj, e):
        if e.type() == QtCore.QEvent.MouseButtonPress and e.buttons() & self.buttons:
            self._has_resized = False
            self.down_pos = e.pos()
            self.down_size = self.target.size()

        elif (
            self.down_pos is not None and 
            e.type() == QtCore.QEvent.MouseMove and 
            e.buttons() & self.buttons
        ):
            self._has_resized = True
            o = e.pos() - self.down_pos
            self.apply_resize(
                self.down_size.width(), self.down_size.height(), 
                o.x(), o.y()
            )
            if not self.propagate_events:
                return True
            # we should always return True, but returning None
            # gives a pretty cool side effect on flow action dialog:
            # the dialog resize too and it gives a good feeling :P

        elif e.type() == QtCore.QEvent.MouseButtonRelease and e.buttons() & self.buttons:
            self.down_pos = None
            self.down_size = None
            if not self._has_resized:
                self.target.setMinimumSize(self._mns)
                self.target.setMaximumSize(self._mxs)
                self.target.setSizePolicy(self._sp)
                self._do_on_resized()


        return False
