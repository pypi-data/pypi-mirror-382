import os
import base64
from .interface import Editor_Interface

from six import text_type as unicode

from qtpy import QtWidgets, QtCore, QtGui
from kabaret.app import resources


class FileDialog(QtWidgets.QFileDialog):

    def __init__(self, options):
        QtWidgets.QFileDialog.__init__(self, caption="Select Image")

        # Force to select only one file
        self.setFileMode(self.FileMode.ExistingFile)
        # Set filters to images only
        self.setNameFilters(['Images (*.bmp *gif *.jpg *.png *.svg)'])
       
        # Select the current directory path
        if options.get('start_path'):
            self.setDirectory(options.get('start_path'))


class ImageViewer(QtWidgets.QWidget):
    '''
    This widget shows a preview of the image
    '''

    def __init__(self, pixmap=None):
        super().__init__()
        self.pixmap = None
        self.setPixmap(pixmap)

        self._sizeHint = QtCore.QSize()
        self.ratio = QtCore.Qt.KeepAspectRatio
        self.transformation = QtCore.Qt.SmoothTransformation

        self.setMaximumHeight(149)

    def setPixmap(self, pixmap):
        if self.pixmap != pixmap:
            self.pixmap = pixmap
            if isinstance(pixmap, QtGui.QPixmap):
                self._sizeHint = pixmap.size()
            else:
                self._sizeHint = QtCore.QSize()
            self.updateGeometry()
            self.updateScaled()

    def updateScaled(self):
        if self.pixmap:
            self.scaled = self.pixmap.scaled(self.size(), self.ratio, self.transformation)
        self.update()

    def sizeHint(self):
        return self._sizeHint

    def resizeEvent(self, event):
        self.updateScaled()

    def paintEvent(self, event):
        if not self.pixmap:
            return
        qp = QtGui.QPainter(self)
        r = self.scaled.rect()
        r.moveCenter(self.rect().center())
        qp.drawPixmap(r, self.scaled)


class ImageValueEditor(QtWidgets.QWidget, Editor_Interface):
    '''
    This editor lets you put a image using the file explorer or by drag and drop a file.

    Editor Type Names:
        image

    Options:
        start_path:      str - Open file explorer from a specific path
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('image',)

    def __init__(self, parent, options):
        QtWidgets.QWidget.__init__(self, parent)
        Editor_Interface.__init__(self, parent)

        self.options = options
        self.read_only = None

        self.setAcceptDrops(True)
        self.setFixedHeight(150)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.build()
        self.apply_options(options)

    def build(self):
        # Draw a background for the editor
        self.frame = QtWidgets.QFrame()
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setObjectName('ImageEditor')

        # Layout when no image is setted
        self.input = QtWidgets.QWidget()
        input_layout = QtWidgets.QVBoxLayout()

        icon = QtGui.QIcon(resources.get_icon(('icons.gui', 'picture')))
        pixmap = icon.pixmap(QtCore.QSize(128, 128))
        icon_lbl = QtWidgets.QLabel('')
        icon_lbl.setPixmap(pixmap)
        
        self.label = QtWidgets.QLabel('Click or drop your image')

        input_layout.addWidget(icon_lbl, 0, QtCore.Qt.AlignCenter)
        input_layout.addWidget(self.label, 1, QtCore.Qt.AlignCenter)
        self.input.setLayout(input_layout)

        # Layout for ImageViewer
        preview_layout = QtWidgets.QVBoxLayout()
        preview_layout.setContentsMargins(5,5,5,5)
        self.preview = ImageViewer()
        preview_layout.addWidget(self.preview)

        # Buttons
        buttons_layout = QtWidgets.QVBoxLayout()
        buttons_layout.setContentsMargins(5,5,5,5)

        self.apply_button = QtWidgets.QToolButton()
        self.apply_button.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'correct-symbol'))))
        self.apply_button.setFixedSize(20,20)
        self.apply_button.setIconSize(QtCore.QSize(10,10))
        self.apply_button.clicked.connect(self._apply_edit)
        self.apply_button.setShortcut(QtGui.QKeySequence("Ctrl+Return"))

        self.clear_button = QtWidgets.QToolButton()
        self.clear_button.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'remove-symbol'))))
        self.clear_button.setFixedSize(20,20)
        self.clear_button.setIconSize(QtCore.QSize(10,10))
        self.clear_button.clicked.connect(self._on_clear_button_clicked)
        self.clear_button.setShortcut(QtGui.QKeySequence("Escape"))

        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.clear_button)
        
        # Build main layout
        self.setLayout(QtWidgets.QGridLayout())
        self.layout().setContentsMargins(0,0,0,0)

        self.layout().addWidget(self.frame, 0, 0, 3, 0)
        self.layout().addWidget(self.input, 1, 0, QtCore.Qt.AlignCenter)
        self.layout().addLayout(preview_layout, 1, 0)
        self.layout().addLayout(buttons_layout, 0, 0, 3, 0, QtCore.Qt.AlignRight)

        self.preview.hide()
        self.apply_button.hide()
        self.clear_button.hide()

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.read_only = not b
        if b is False:
            self.label.setText('No image')

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        # Check value type for start_path option
        if options.get("start_path") and type(options.get("start_path")) is not str:
            raise Exception('start_path option should be setted with a str value.')

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''

        # Set current value on ImageViewer widget
        if self.fetch_value() is not None and unicode(self.fetch_value()):
            ba = QtCore.QByteArray.fromBase64(bytes(unicode(self.fetch_value()).split(',')[1], "utf-8"))
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(ba, unicode(self.fetch_value()).split(';')[0].split('/')[1])
            self.preview.setPixmap(pixmap)

            self.preview.show()
            if self.read_only is False:
                self.clear_button.show()
            self.apply_button.hide()
            self.input.hide()
        else:
            self.preview.setPixmap(None)
            self.preview.hide()
            self.clear_button.hide()
            self.apply_button.hide()
            self.input.show()

        self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        value = self.value
        if not value.isalpha():     # to avoid python keywords
            try:
                value = eval(value)
            except Exception:
                pass
        return value
 
    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        self.frame.setProperty('edited', True)
        self.frame.setProperty('applying', False)
        self.frame.style().polish(self.frame)

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        self.frame.setProperty('applying', True)

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is 
        up to date.
        '''
        self.frame.setProperty('edited', False)
        self.frame.setProperty('applying', False)
        self.frame.setProperty('error', False)
        self.frame.style().polish(self.frame)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self.frame.setProperty('error', True)
        self.frame.style().polish(self.frame)
        self.setToolTip('!!!\nERROR: %s' % (error_message,))

    def _on_clear_button_clicked(self):
        self.value = ''
        self.apply()

    def _apply_edit(self):
        self.apply()

    def setImage(self, path):
        # Encode image into base64 value
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            _, ext = os.path.splitext(path)
            self.value = f'data:image/{ext};base64,{encoded_string}'
        
        self.preview.setPixmap(QtGui.QPixmap(path))
        
        self.preview.show()
        self.clear_button.show()
        self.apply_button.show()
        self.input.hide()
        
        self._on_edited()

    def mousePressEvent(self, event):
        '''
        Open file explorer on mouse click
        '''
        if self.input.isVisible() and self.read_only is False:
            fd = FileDialog(self.options)
            if fd.exec_():
                paths = fd.selectedFiles()
                self.setImage(paths[0])
        
        super(ImageValueEditor, self).mousePressEvent(event)

    def dragEnterEvent(self, event):
        '''
        Only accept a image file on drag and drop
        '''
        if event.mimeData().hasUrls and self.read_only is False:
            if len(event.mimeData().urls()) == 1:
                formatCheck = QtGui.QImageReader.imageFormat(
                    event.mimeData().urls()[0].toLocalFile()
                )
                if formatCheck:
                    return event.accept()
        return event.ignore()

    def dropEvent(self, event):
        '''
        Set dropped image
        '''
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.setImage(file_path)
