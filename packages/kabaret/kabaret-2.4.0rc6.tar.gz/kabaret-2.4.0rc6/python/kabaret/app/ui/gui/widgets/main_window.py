from __future__ import print_function

import traceback

from qtpy import QtWidgets, QtCore

from ..styles import StylesManager

from ..icons import gui     # noqa # just declaring resources...
from ..icons import status  # noqa # just declaring resources...
from kabaret.app import resources


class DockTitleBar(QtWidgets.QWidget):
    def __init__(self, main_window_manager, dock, view):
        super(DockTitleBar, self).__init__(dock)
        self.mwm = main_window_manager
        self.dock = dock
        self.dock.topLevelChanged.connect(self.on_floating)
        self.view = view

        self.maximize_butt = None
        self.maximized = False
        self.installed = False

        try:
            self.view.set_on_view_title_change(self.on_view_title_change)
        except Exception as err:
            self.installed = False
            raise err
        else:
            try:
                self.install_tools()
            except Exception as err:
                self.installed = False
                raise err
            else:
                self.installed = True

    def sizeHint(self):
        return QtCore.QSize(5, 5)

    def minimumSizeHint(self):
        return QtCore.QSize(5, 5)

    def install_tools(self):
        self.maximize_butt = self.view.add_header_tool(
            'titleBarMaximize',
            self.maximized and '-' or '+',
            'Toggle Maximize',
            lambda self=self: self.mwm.toggle_maximized_dock(self)
        )
        self.installed = True

    def uninstall_tools(self):
        # FIXME: shouldn't a Hide be enough?
        self.view.remove_header_tool('titleBarMaximize')

    def on_view_title_change(self):
        self.dock.setWindowTitle(self.view.view_title())

    def on_floating(self, b):
        if b:
            self.dock.setTitleBarWidget(None)
            self.uninstall_tools()
        else:
            0 and self.dock.setTitleBarWidget(self)
            self.install_tools()
        self.dock.setFocus()

    def float_dock(self):
        if self.maximized:
            self.mwm.toggle_maximized_dock(self)
        self.dock.setFloating(True)

    def hide_dock(self):
        self.dock.hide()


class DockWidget(QtWidgets.QDockWidget):

    def __init__(self, dock_closed_callback, title, parent):
        super(DockWidget, self).__init__(title, parent)
        self.closed_callback = dock_closed_callback
        self.setFeatures(self.DockWidgetFeature.DockWidgetMovable | self.DockWidgetFeature.DockWidgetClosable)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def closeEvent(self, e):
        self.closed_callback(self, self.view())

    def setFloating(self, floating):
        return False

    def view(self):
        return self.widget()

    def dock_area(self):
        mw = self.parentWidget()
        return mw.dockWidgetArea(self)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, session, parent=None):
        super(MainWindow, self).__init__(parent)
        self.session = session

    def closeEvent(self, event):
        # Save views state on exit to be restored
        if self.session.layout_manager and self.session.layout_autosave:
            self.session.store_layout_preset(
                self.session.get_views_state(main_geometry=True),
                autosave=True
            )


class MainWindowManager(object):

    @classmethod
    def create_window(cls, session, parent=None):
        mw = MainWindow(session, parent)
        manager = cls(session, mw, embed_mode=False)
        return manager

    def __init__(self, session, main_window, embed_mode=False):
        super(MainWindowManager, self).__init__()
        self.main_window = main_window
        self.session = session
        self.embed_mode = embed_mode

    def install(self):
        mw = self.main_window

        if not self.embed_mode:
            mw.resize(QtCore.QSize(800, 800))
            StylesManager.get().apply_default_style()
            mw.setWindowIcon(
                resources.get_icon(('icons.gui', 'kabaret_icon'))
            )

            self.update_title()

            mw.setDockOptions(
                mw.DockOption.AnimatedDocks
                | mw.DockOption.AllowNestedDocks
                | mw.DockOption.AllowTabbedDocks
            )
            mw.setTabPosition(QtCore.Qt.AllDockWidgetAreas,
                              QtWidgets.QTabWidget.North)

        #!!self._view_types = {}
        self._docks = []
        self._maximised_to_restore = None

        self.session.register_view_types()
        mw.show()

    def update_title(self):
        title = self.session.session_name() or 'Kabaret Studio'
        title += '[%s]' % self.session.cmds.Cluster.get_cluster_name()
        self.main_window.setWindowTitle(title)

    def dock_closed(self, dock, view):
        if view.delete_on_close():
            view.about_to_delete()
            self._docks.remove(dock)
            dock.deleteLater()

        # TODO: Perhaps switch to restoring the focus to the previous widget?
        for dock in self._docks:
            view = dock.view()
            if view.view_type_name() == "Flow" and view.isVisible() is True:
                view.setFocus()
                break

    def dock_visibility_changed(self, visible, dock, view):
        if not visible:
            view.hidden = True
            view.on_hide()
        else:
            view.hidden = False
            view.on_show()
            if view.view_type_name() == "Flow" and self.session.current_view() is not view:
                view.setFocus()

    def dock_location_changed(self, location, dock, view):
        view.area = location

    def register_view_type(self, Type):
        print('!!! WARNING !!!')
        print('!!! WARNING !!! session.main_window_manager.register_view_type() is deprecated !')
        print('!!! WARNING !!! (You must use session.register_view_type() instead)')
        print('!!! WARNING !!!')
        return self.session.register_view_type(Type)

    def add_view(self, type_name, area=None, visible=True, *view_args, **view_kwargs):
        print('!!! WARNING !!!')
        print('!!! WARNING !!! session.main_window_manager.add_view() is deprecated !')
        print('!!! WARNING !!! (You must use session.add_view() instead)')
        print('!!! WARNING !!!')
        if area is not None:
            print('!!! WARNING !!!')
            print('!!! WARNING !!! session.main_window_manager.add_view() is deprecated !')
            print('!!! WARNING !!! The "area" kword is not supported anymore')
            print('!!! WARNING !!!')
        if area is not None:
            print('!!! WARNING !!!')
            print('!!! WARNING !!! session.main_window_manager.add_view() is deprecated !')
            print('!!! WARNING !!! The "visible" kword is not supported anymore')
            print('!!! WARNING !!!')

        return self.session.add_view(type_name, *view_args, **view_kwargs)

    def add_toolbar_view(self, view, hidden=False, area=None):
        area = area or QtCore.Qt.TopToolBarArea
        self.main_window.addToolBar(area, view)
        view.setVisible(not hidden)

    def create_docked_view_dock(self, view, hidden=False, area=None):
        dock = DockWidget(self.dock_closed, view.view_title(), self.main_window)
        tb = DockTitleBar(self, dock, view)
        if tb.installed:
            0 and dock.setTitleBarWidget(tb)
        else:
            tb.deleteLater()

        dock.setWidget(view)
        dock.visibilityChanged.connect(
            lambda visible, dock=dock, view=view: self.dock_visibility_changed(visible, dock, view)
        )
        dock.dockLocationChanged.connect(
            lambda area, dock=dock, view=view: self.dock_location_changed(area, dock, view)
        )
        dock.setObjectName('Dock_%s_%i' % (view.view_title(), len(self._docks),))

        area = area or QtCore.Qt.LeftDockWidgetArea
        self.main_window.addDockWidget(area, dock)

        if hidden:
            dock.hide()

        # Auto tabify views of matching type name:
        target_view = self.find_docked_view(view.view_type_name(), area=area)
        if target_view is not None:
            target_view.dock_widget().show()
            dock.show()
            self.main_window.tabifyDockWidget(target_view.dock_widget(), dock)

        self._docks.append(dock)

        if len(self._docks) > 1:
            for d in self._docks:
                if d.titleBarWidget() and d.titleBarWidget().maximize_butt:
                    d.titleBarWidget().maximize_butt.setEnabled(True)
        else:
            for d in self._docks:
                if d.titleBarWidget() and d.titleBarWidget().maximize_butt:
                    d.titleBarWidget().maximize_butt.setEnabled(False)

        return dock

    def tabify_view(self, first_view, second_view):
        d1 = first_view.dock_widget()
        d2 = second_view.dock_widget()
        self.main_window.tabifyDockWidget(d1, d2)

    def toggle_maximized_dock(self, titlebar):
        button = titlebar.maximize_butt
        keeped = titlebar.dock

        if self._maximised_to_restore is None:
            button.setText('-')
            self._maximised_to_restore = self.main_window.saveState()
            for d in self._docks:
                if d is keeped:
                    d.setFocus()
                    continue
                d.hide()

        else:
            button.setText('+')

            self.main_window.restoreState(self._maximised_to_restore)
            self._maximised_to_restore = None

    def find_docked_view(self, view_type_name, area=None):
        for dock in self._docks:
            if area is not None and dock.dock_area() != area:
                continue
            view = dock.view()
            if view.view_type_name() == view_type_name:
                return view
        return None

    def find_view(self, view_type_name, create=False, area=None, *args, **kwargs):
        '''
        Returns a view with the specified type.
        If create is True and no existsing view in found, create one in the given area
        using *args and **kwargs.
        If create is False, None is returned.
        '''
        print('!!! WARNING !!!')
        print('!!! WARNING !!! session.main_window_manager.find_view() is deprecated !')
        print('!!! WARNING !!! (You must use session.find_view() instead)')
        print('!!! WARNING !!!')
        if area is not None:
            print('!!! WARNING !!!')
            print('!!! WARNING !!! session.main_window_manager.find_view() is deprecated !')
            print('!!! WARNING !!! The "area" kword is not supported anymore')
            print('!!! WARNING !!!')
        return self.session.find_view(view_type_name, create=create, *create_args, **create_kwargs)
        # try:
        #     Type = self._view_types[view_type_name]
        # except KeyError:
        #     raise ValueError('Find View: Unknown view type %r' %
        #                      (view_type_name,))

        # for dock in self._docks:
        #     if area is not None and dock.dock_area() != area:
        #         continue
        #     view = dock.view()
        #     if view.__class__ == Type:
        #         return view

        # if create:
        #     return self.add_view(view_type_name, area, *args, **kwargs)
        # else:
        #     return None

    # def receive_event(self, event_type, data):
    #     pass
    #     if event_type == 'cluster_connection':
    #         cluster_name = data['cluster_name']
    #         self._set_title(cluster_name)

    # def dispatch_event(self, event_type, data):
    #     if event_type == 'cluster_connection':
    #         cluster_name = data['cluster_name']
    #         self._set_title(cluster_name)

    #     for T in self._view_types.values():
    #         for view in T._VIEWS:
    #             view.receive_event(event_type, data)

    def resize(self, width, height):
        self.main_window.resize(width, height)

    def get_geometry_state(self):
        return self.main_window.saveGeometry()
    
    def set_geometry_state(self, state):
        self.main_window.restoreGeometry(state)
    
    def get_layout_state(self):
        return self.main_window.saveState()

    def set_layout_state(self, state):
        self.main_window.restoreState(state)
