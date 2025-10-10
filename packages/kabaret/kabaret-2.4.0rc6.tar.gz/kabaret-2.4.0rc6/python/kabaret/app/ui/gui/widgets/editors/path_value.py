import os
import re
from .interface import Editor_Interface

from six import text_type as unicode

from qtpy import QtWidgets, QtCore, QtGui
from kabaret.app import resources


class FileDialog(QtWidgets.QFileDialog):

    def __init__(self, options):
        QtWidgets.QFileDialog.__init__(self)

        # Select multiple files
        if options.get('files_only') is True:
            self.setFileMode(self.FileMode.ExistingFiles)
            # Select only one file
            if options.get('max_count') == 1:
                self.setFileMode(self.FileMode.ExistingFile)
        # Select only one directory
        elif options.get('dirs_only') is True and options.get('max_count') == 1:
            self.setFileMode(self.FileMode.Directory)
        # Select multiple files and directories or multiple directories
        else:
            self.setFileMode(self.FileMode.Directory)
            self.setOption(self.Option.DontUseNativeDialog, True)
            self.setViewMode(self.ViewMode.Detail)

            # Allow multi selection in views
            self.list = self.findChild(QtWidgets.QListView)
            self.list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

            self.tree = self.findChild(QtWidgets.QTreeView)
            self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

            # Redefine clicked signal for main button
            # To fix a issue when the first item is a file
            btns = self.findChildren(QtWidgets.QPushButton)
            self.chooseBtn = [x for x in btns if 'choose' in str(x.text()).lower()][0]
            self.chooseBtn.installEventFilter(self)
            self.chooseBtn.clicked.disconnect()
            self.chooseBtn.clicked.connect(self.openClicked)
            
            if options.get('dirs_only') is True:
                self.setOption(self.Option.ShowDirsOnly, True)
        
        # Select the current directory path
        if options.get('start_path'):
            self.setDirectory(options.get('start_path'))
        
        # Sets the filters
        if options.get('filters'):
            self.setNameFilters(options.get('filters'))

    def eventFilter(self, source, event):
        # Keep enabled main button
        if isinstance(source, QtWidgets.QPushButton) and event.type() is QtCore.QEvent.EnabledChange:
            if source.isEnabled() is False:
                source.setEnabled(True)
                return True
        
        return False

    def openClicked(self):
        # Fetch selected files
        indexs = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in indexs:
            if i.column() == 0:
                files.append(os.path.normpath(
                    os.path.join(self.directory().absolutePath(), str(i.data()))
                ))
        
        # Set dialog result to Accepted
        if files:
            self.setResult(1)

        self.selectedFiles = files
        self.hide()


class PathValueEditor(QtWidgets.QLineEdit, Editor_Interface):
    '''
    This editor lets you enter path values using the file explorer.
    By default, the user can select any files.

    Editor Type Names:
        path

    Options:
        start_path:      str - Open file explorer from a specific path
        filters:         list of str (ex: ['Text files (*.txt)', 'Any files (*)']) - Displays files that match the patterns
        max_count:       int - Limit the maximum number of paths
        dirs_only:       bool - Can only select directories
        files_only:      bool - Can only select files
        path_format:     str ('win32' or 'linux') - Force path format to a specific operating system
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('path',)

    def __init__(self, parent, options):
        QtWidgets.QLineEdit.__init__(self, parent)
        Editor_Interface.__init__(self, parent)

        self.options = options
        
        # Default regex
        self.regexp = '^(?:[a-zA-Z]:[\\\\\/]{{1,2}}|\/{{1,2}}|\\{{1,2}})(?:[^<>:"/\\\\|?*]+[\\\\\/]{{1,2}})*(?:[^<>:"/\\\\|?*]+{filters})(?<=\S)$'

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setContentsMargins(5,5,5,5)

        self._explorer_button = QtWidgets.QToolButton(self)
        self._explorer_button.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'open-folder'))))
        self._explorer_button.setFixedSize(QtCore.QSize(20,20))
        self._explorer_button.setIconSize(QtCore.QSize(12,12))
        self._explorer_button.setCursor(QtCore.Qt.ArrowCursor)
        self._explorer_button.clicked.connect(self._open_explorer)
       
        self.layout().addStretch()
        self.layout().addWidget(self._explorer_button)

        self.apply_options(options)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.setReadOnly(not b)
        if b:
            self.textEdited.connect(self._on_edited)
            self.returnPressed.connect(self.apply)
        else:
            self._explorer_button.hide()

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        # Check value types of options
        if options.get("start_path") and type(options.get("start_path")) is not str:
            raise Exception('start_path option should be setted with a str value.')

        if options.get("max_count") and type(options.get("max_count")) is not int:
            raise Exception('max_count option should be setted with a int value.')

        if options.get("dirs_only") and type(options.get("dirs_only")) is not bool:
            raise Exception('dirs_only option should be setted with a bool value.')

        if options.get("files_only") and type(options.get("files_only")) is not bool:
            raise Exception('files_only option should be setted with a bool value.')

        if options.get("dirs_only") and options.get("files_only"):
            raise Exception('dirs_only and files_only options can\'t be used at the same time.')
        
        # Use specific regex if path_format option
        if options.get("path_format") is not None:
            if options.get("path_format") == "win32":
                self.regexp = '^(?:[a-zA-Z]:[\\\\\/]{{1,2}}|\\{{2}})(?:[^<>:"/\\\\|?*]+[\\\\\/]{{1,2}})*(?:[^<>:"/\\\\|?*]+{filters})(?<=\S)$'
            elif options.get("path_format") == "linux":
                self.regexp = '^\/(?:[^/]+\/)*[^/]+{filters}(?<=\S)$'
            else:
                raise Exception('path_format option must be "win32" or "linux".')
        
        # Update regex if filters (file extensions)
        if options.get('filters'):
            filters = re.findall('(?<=\*.)\w+|\(\*\)', str(options.get('filters')))
            if '(*)' not in filters:
                self.regexp = self.regexp.format(
                    filters='\.(?:{exts})'.format(
                        exts='|'.join(filters)
                    )
                )
                return
        
        self.regexp = self.regexp.format(filters='')

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        # Clear ToolTip if there was an error
        self.setToolTip('')

        if self.text():
            # For multiple paths
            if self.text().startswith("['") and self.text().endswith("']"):
                paths = eval(self.text())

                # Check maximum count
                if self.options.get('max_count'):
                    if len(paths) > self.options.get('max_count'):
                        word = f'path{"s" if self.options.get("max_count") > 1 else ""}'
                        return self._show_error(f'A maximum of {self.options.get("max_count")} {word} can be defined')
                
                # Validate path format
                for i, path in enumerate(paths):
                    if re.search(self.regexp, path) is None:
                        # Specify which format if path_format option
                        if self.options.get('path_format'):
                            return self._show_error(f'Path {i+1} must be in {self.options.get("path_format")} format')
                        else:
                            return self._show_error(f'Path {i+1} is not valid')
            # For single path
            else:
                # Validate path format
                if re.search(self.regexp, self.text()) is None:
                    # Specify which format if path_format option
                    if self.options.get('path_format'):
                        return self._show_error(f'Path must be in {self.options.get("path_format")} format')
                    else:
                        return self._show_error('Path is not valid')
        
        self.setText(unicode(self.fetch_value()))
        self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        value = self.text()
        if not value.isalpha():     # to avoid python keywords
            try:
                value = eval(value)
            except Exception:
                pass
        return value

    def _open_explorer(self):
        fd = FileDialog(self.options)

        if fd.exec_():
            paths = fd.selectedFiles() if callable(fd.selectedFiles) else fd.selectedFiles
            self.setText(paths[0] if len(paths) == 1 else str(paths))

            self._on_edited()

            if self.options.get('max_count'):
                if len(paths) > self.options.get('max_count'):
                    word = f'path{"s" if self.options.get("max_count") > 1 else ""}'
                    self._show_error(f'A maximum of {self.options.get("max_count")} {word} can be defined')
    
    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        self.setProperty('edited', True)
        self.setProperty('applying', False)
        self.setProperty('error', False)
        self.style().polish(self)

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        self.setProperty('applying', True)

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is 
        up to date.
        '''
        self.setProperty('edited', False)
        self.setProperty('applying', False)
        self.setProperty('error', False)
        self.style().polish(self)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self.setProperty('error', True)
        self.style().polish(self)
        self.setToolTip('!!!\nERROR: %s' % (error_message,))

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls[0].scheme() == 'file':
            event.acceptProposedAction()
            cursor_pos = self.cursorPositionAt(event.pos())
            self.setCursorPosition(cursor_pos)

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls[0].scheme() == 'file':
            filepath = str(urls[0].toLocalFile()) if len(urls) == 1 else str([url.toLocalFile() for url in urls])
            self.insert(filepath)
            self._on_edited()

