
import os
import six
import getpass
import functools

from qtpy import QtWidgets, QtCore, QtGui
from datetime import datetime

from .widget_view import ToolBarView
from kabaret.app import resources


LAYOUTS = {}

class ClickLabel(QtWidgets.QLabel):

    def __init__(self, on_click, *args, **kwargs):
        super(ClickLabel, self).__init__(*args, **kwargs)
        self._on_click = on_click

    def mousePressEvent(self, event):
        self._on_click()

class SessionToolBar(ToolBarView):

    def __init__(self, *args, **kwargs):
        super(SessionToolBar, self).__init__(*args, **kwargs)

        self.user_label = QtWidgets.QLabel(self)
        self.session_id_label = QtWidgets.QLabel(self)

        stretch = QtWidgets.QWidget(self)
        stretch.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred,
        )

        self.addWidget(self.user_label)
        self.addSeparator()
        self.addWidget(self.session_id_label)
        self.addSeparator()

        # Show layout menu when manager is enabled
        if self.session.layout_manager:
            self.layouts_tb = QtWidgets.QToolButton(self)
            self.layouts_tb.setText('Layouts')
            self.layouts_tb.setPopupMode(self.layouts_tb.ToolButtonPopupMode.InstantPopup)
            self.layouts_tb.setIcon(resources.get_icon(('icons.gui','ui-layout')))
            self.layouts_tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.layout_menu = QtWidgets.QMenu(self.layouts_tb)
            self.layout_menu.addAction('TEST')
            self.layout_menu.aboutToShow.connect(self.update_layout_tb)
            self.layouts_tb.setMenu(self.layout_menu)

            self.addWidget(stretch)
            self.addSeparator()
            self.addWidget(self.layouts_tb)
            
        self.update_user_label()

    def update_user_label(self):
        label = ' <b><font size=+5>{}</font></b> '.format(
            getpass.getuser(),
        )
        self.user_label.setText(label)

        label=' {}[{}] '.format(
            self.session.session_name(),
            self.session.cmds.Cluster.get_cluster_name(),
        )
        self.session_id_label.setText(label)
        
        self.session_id_label.setToolTip(
            '<b>Session ID:</b> {}<br><b>Connection:</b> {}'.format(
                self.session.session_uid(),
                ' - '.join(self.session.cmds.Cluster.get_connection_info())
            )
        )

    def update_layout_tb(self):
        # Clear all actions of context menu
        tb = self.layouts_tb
        menu = tb.menu()
        menu.clear()

        # Split layouts by project
        project_menus = {}
        projects_info = self.session.get_actor("Flow").get_projects_info()
        for project in projects_info:
            name = project[0]
            project_menus[name] = menu.addMenu(name)

        # Add user layout presets
        self.layout_icon = resources.get_icon(('icons.gui', 'ui-layout'))
        for name, layout in sorted(six.iteritems(self.session.get_layout_presets())):
            project_found = False
            
            for project_name, project_menu in project_menus.items():
                for view_data in layout['views']:
                    view_state = view_data[-1]
                    if 'oid' in view_state:
                        if view_state['oid'].startswith(f'/{project_name}'):
                            action = QtGui.QAction(self.layout_icon, name, project_menu)
                            action.triggered.connect(functools.partial(self._on_set_layout_action, layout))
                            action.setObjectName('la')

                            project_menu.addAction(action)
                            project_found = True
                            break

            # Add directly to layout root menu if no project has been found in views
            if not project_found:
                action = QtGui.QAction(self.layout_icon, name)
                action.triggered.connect(functools.partial(self._on_set_layout_action, layout))
                action.setObjectName('la')

                menu.insertAction(project_menu.menuAction(), action)
        
        # Add a separator
        self.menu_sep = QtGui.QAction(menu)
        self.menu_sep.setSeparator(True)
        self.menu_sep.setObjectName('sep')
        menu.addAction(self.menu_sep)

        # Add store layout action
        icon = resources.get_icon(('icons.gui', 'plus-symbol-in-a-rounded-black-square'))
        store_action = QtGui.QAction(icon, 'Store Current Layout', menu)
        store_action.triggered.connect(self._on_store_current_layout_action)
        store_action.setObjectName('sa')
        menu.addAction(store_action)

        # Add delete layout action
        icon = resources.get_icon(('icons.gui', 'minus-button'))
        delete_action = QtGui.QAction(icon, 'Delete Layout', menu)
        delete_action.triggered.connect(self._on_delete_layout_action)
        delete_action.setObjectName('da')
        menu.addAction(delete_action)

        # Add layout session autosaves
        icon = resources.get_icon(('icons.gui', 'share-post-symbol'))
        recover_menu = menu.addMenu(icon, 'Recover Session Layout')

        for name, layout in sorted(six.iteritems(self.session.get_layout_presets(autosaves=True)), reverse=True):
            action = QtGui.QAction(self.layout_icon, name, self.layouts_tb.menu())
            action.triggered.connect(functools.partial(self._on_set_layout_action, layout))
            action.setObjectName('la')

            recover_menu.addAction(action)

    def _on_set_layout_action(self, layout):
        # Don't delete us inside an signal handler from us:
        QtCore.QTimer.singleShot(
            100, lambda l=layout, s=self.session: s.set_views_state(l)
        )

    def _on_store_current_layout_action(self):
        # Create dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Save Layout')
        dialog.setLayout(QtWidgets.QVBoxLayout())

        # Create title
        title = QtWidgets.QLabel('<h1>Enter preset name</h1>')
        dialog.layout().addWidget(title)

        # Create combobox selection
        cb = QtWidgets.QComboBox(dialog)
        cb.addItems(['']+list(self.session.get_layout_presets().keys()))
        cb.setEditable(True)
        cb.lineEdit().setValidator(QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('[^<>:"\/\\\|?*]+')))
        dialog.layout().addWidget(cb)

        # Create checkbox for window position
        checkbox = QtWidgets.QCheckBox("Save Window Position")
        checkbox.setChecked(False)
        dialog.layout().addWidget(checkbox)

        # Create button
        b = QtWidgets.QPushButton(dialog)
        b.setText('Save Layout')
        b.clicked.connect(dialog.accept)
        dialog.layout().addWidget(b)

        dialog.setFixedSize(350, 150)

        # Store and update menu if accepted
        cancel = dialog.exec_() != dialog.Accepted
        name = cb.currentText().strip()
        dialog.deleteLater()
        if cancel or not name:
            return

        self.session.store_layout_preset(
            self.session.get_views_state(main_geometry=checkbox.isChecked()),
            name
        )
        self.update_layout_tb()

    def _on_delete_layout_action(self):
        # Create dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Delete Layout')
        dialog.setLayout(QtWidgets.QVBoxLayout())

        # Create title
        title = QtWidgets.QLabel('<h1>Select layouts to delete</h1>')
        dialog.layout().addWidget(title)

        # Create user layout presets list
        listw = QtWidgets.QListWidget(dialog)
        for layout_name in list(self.session.get_layout_presets().keys()):
            item = QtWidgets.QListWidgetItem(layout_name)
            item.setCheckState(QtCore.Qt.Unchecked)
            listw.addItem(item)
        dialog.layout().addWidget(listw)

        # Create button
        b = QtWidgets.QPushButton(dialog)
        b.setText('Delete')
        b.clicked.connect(dialog.accept)
        dialog.layout().addWidget(b)

        dialog.setFixedSize(375, 300)

        # Delete and update menu if accepted
        cancel = dialog.exec_() != dialog.Accepted
        dialog.deleteLater()
        if cancel:
            return

        checked = []
        for row in range(listw.count()):
            item = listw.item(row)
            if item.checkState():
                checked.append(item.text())

        self.session.delete_layout_preset(checked)
        self.update_layout_tb()

    def receive_event(self, event_type, data):
        pass
