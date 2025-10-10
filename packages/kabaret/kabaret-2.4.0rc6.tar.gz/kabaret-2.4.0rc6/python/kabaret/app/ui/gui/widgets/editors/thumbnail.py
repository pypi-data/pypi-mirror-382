import time
import os
import shutil

from qtpy import QtWidgets, QtCore, QtGui

from .interface import Editor_Interface
import kabaret.app.resources

from .default_thumbnail import DEFAULT_THUMBNAIL

class WindowMover(QtCore.QObject):
    def __init__(self, widget):
        super(WindowMover, self).__init__(widget)
        self.window = widget.window()
        self.down_pos = None
        self.start_pos = None
        
    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
            self.down_pos = event.globalPos()
            self.start_pos = self.window.pos()
            obj.grabMouse()
            return True
        elif self.down_pos is not None and event.type() == event.MouseMove:
            delta = event.globalPos() - self.down_pos
            self.window.move(self.start_pos + delta)
            return True
        elif event.type() == event.MouseButtonRelease:
            self.down_pos = None
            self.start_pos = None
            obj.releaseMouse()
            return True
        else:
            return super(WindowMover, self).eventFilter(obj, event)


class ScreenGrabDialog(QtWidgets.QDialog):
    def __init__(self, parent, hide_window=True):
        super(ScreenGrabDialog, self).__init__(parent)
        
        if hide_window:
            self.window_to_hide = parent.window()
        else:
            self.window_to_hide = None
        self.restore_geom = None

        self._decoration_height = None
        self.winframe_w = 4
        self.winframe_h = 8
        
        self.setWindowTitle('SnapShot')
        
        self.screen_pix = self.grab_screen()
        
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        
        self.view = QtWidgets.QGraphicsView(self)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setResizeAnchor(self.view.NoAnchor)
        self.view.setTransformationAnchor(self.view.NoAnchor)
        self.view.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
        self.view.setCursor(QtCore.Qt.SizeAllCursor)
        self.layout().addWidget(self.view)
        
        self.mover = WindowMover(self)
        self.view.installEventFilter(self.mover)

        b = QtWidgets.QPushButton('Capture', self)
        b.clicked.connect(self.accept)
        self.layout().addWidget(b)
        
        self.scene = QtWidgets.QGraphicsScene()
        self.pix_item = self.scene.addPixmap(self.screen_pix)
        
        self.view.setScene(self.scene)

        self.resize(100, 100)
        
    def grab_screen(self):
        if self.window_to_hide is not None:
            self.restore_geom = self.window_to_hide.geometry()
            self.window_to_hide.hide()
            time.sleep(0.2)
        desktop = QtWidgets.QApplication.desktop()
        screen_pix = QtGui.QPixmap.grabWindow(
            desktop.winId(), 0, 0, desktop.width(), desktop.height()
        )        
        return screen_pix
    
    def moveEvent(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        if self._decoration_height is None:
            style = self.style()
            self._decoration_height = style.pixelMetric(style.PM_TitleBarHeight)
            self.winframe_w = 3
        self.pix_item.setPos(-x -self.winframe_w, -y -self._decoration_height -self.winframe_h)
        
    def get_croped_pix(self):
        return QtGui.QPixmap.grabWidget(self.view)
    
    def exec_(self):
        ret = super(ScreenGrabDialog, self).exec_()

        if self.window_to_hide is not None:
            self.window_to_hide.show()
            if self.restore_geom is not None:
                self.window_to_hide.setGeometry(self.restore_geom)
        
        return ret


class ThumbnailWidget(QtWidgets.QToolButton):

    def __init__(self, parent):
        super(ThumbnailWidget, self).__init__(parent)
        self._force_height = None
        self.maximum_height = 126

        self.path = None
        self.pix = QtGui.QPixmap()
        self._load()

        self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.setAutoRaise(False)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setArrowType(QtCore.Qt.NoArrow)

        # self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        # self.setFrameShadow(QtWidgets.QFrame.Plain)
        # self.setLineWidth(2)
    
        self._menu = QtWidgets.QMenu()
        self._menu.addAction('Take a snapshot', self._on_snapshot_menu)
        self._menu.addAction('Copy path to clipboard', self._on_copy_path_to_clipboard)
        self.setMenu(self._menu)

    def force_height(self, height, maximum_height=None):
        if maximum_height:
            self.maximum_height = maximum_height
        self._force_height = height
        self._load()

    def set_path(self, path):
        self.path = path
        self._load()
            
    def _load(self):
        if self.path:
            self.pix.load(self.path)
        else:
            self.pix = QtGui.QPixmap(DEFAULT_THUMBNAIL)
        pix = self._get_scaled_pix()
        self.setIcon(QtGui.QIcon(pix))
        self.setIconSize(pix.size())
        self.setMinimumSize(pix.size())
    
    def _move_to_backup(self):
        bak_base = self.path+'.bak_'+str(time.time())
        bakpath = bak_base
        for i in range(10):
            if not os.path.exists(bakpath):
                break
            bakpath = bak_base+'_'+str(i)
        os.rename(self.path, bakpath)
    
    def update_from_path(self, path):
        '''
        Updates the content of the thumbnail using
        the given file.
        
        A copy of the current thumbnail file is made 
        before overwriting it.
        '''

        if not self.path:
            raise Exception('Cannot update thumnail: path not set')
        
        if not os.path.exists(path):
            raise Exception('Cannot update thumbnail from unexisting source %r.'%(path,))
                
        _, my_extension = os.path.splitext(self.path)
        _, in_extension = os.path.splitext(path)
        if my_extension != in_extension:
            raise Exception('Cannot, update thumbnail from %r: wrong extension.'%(path,))
        
        dir, base = os.path.split(self.path)
        if os.path.exists(self.path):
            self._move_to_backup()
        else:
            if not os.path.exists(dir):
                os.makedirs(dir)
        
        shutil.copy(path, self.path)
        self._load()

    def _on_copy_path_to_clipboard(self):
        cp = QtWidgets.QApplication.clipboard()
        cp.setText(self.path)
        
    def _on_snapshot_menu(self):
        self._do_snapshot(hide_window=False)
        
    def _on_hide_and_snapshot_menu(self):        
        self._do_snapshot()
        
    def _do_snapshot(self, hide_window=True):
        dialog = ScreenGrabDialog(self, hide_window=hide_window)
        result = dialog.exec_()
        if result == dialog.Accepted:
            pix = dialog.get_croped_pix()
            if pix is not None:
                self.update_from_pix(pix)
        dialog.deleteLater()
    
    def _get_scaled_pix(self):
        if self._force_height is None:
            if self.pix.height() > self.maximum_height:
                return self.pix.scaledToHeight(self.maximum_height, QtCore.Qt.SmoothTransformation)
            return self.pix
        return self.pix.scaledToHeight(min(self.maximum_height, self._force_height), QtCore.Qt.SmoothTransformation)

    def update_from_pix(self, pix):
        if not self.path:
            raise Exception('Cannot update thumbnail: path not set')
        
        dir, base = os.path.split(self.path)
        
        if os.path.exists(self.path):
            self._move_to_backup()
        else:
            if not os.path.exists(dir):
                os.makedirs(dir)
        
        pix.save(self.path)
        self._load()


class ThumbnailEditor(QtWidgets.QWidget, Editor_Interface):

    @classmethod
    def can_edit(cls, editor_type_name):
        return editor_type_name in ('thumbnail',)

    def __init__(self, parent, options):
        QtWidgets.QWidget.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self._build()
        self.apply_options(options)

    def _build(self):
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

        self._tn = ThumbnailWidget(self)
        self.layout().addWidget(self._tn, 1, QtCore.Qt.AlignLeft)

        self._summary_lb = QtWidgets.QLabel(self)
        self._summary_lb.hide()
        self.layout().addWidget(self._summary_lb)

    def set_editable(self, b):
        pass

    def apply_options(self, options):
        pass

    def update(self):
        value = str(self.fetch_value() or '')
        self._tn.set_path(value)
        self._on_updated()

    def get_edited_value(self):
        return self._tn.path

    def _show_edited(self):
        self._tn.setProperty('edited', True)
        self._tn.setProperty('applying', False)
        self._tn.style().polish(self)

    def _show_applied(self):
        self._tn.setProperty('applying', True)

    def _show_clean(self):
        self._tn.setProperty('edited', False)
        self._tn.setProperty('applying', False)
        self._tn.style().polish(self)

    def _show_error(self, error_message):
        self._tn.setProperty('error', True)
        self._tn.style().polish(self)
        self.setToolTip('!!!\nERROR: %s' % (error_message,))
