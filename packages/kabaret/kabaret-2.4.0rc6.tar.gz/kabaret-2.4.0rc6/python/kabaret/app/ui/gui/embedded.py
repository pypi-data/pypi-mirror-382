
from qtpy import QtWidgets

from ...session import KabaretSession

from .widgets.main_window import MainWindowManager, QtCore


class KabaretEmbeddedGUISession(KabaretSession):

    def __init__(
            self,
            session_name='Kabaret',
            tick_every_ms=100
    ):
        super(KabaretEmbeddedGUISession, self).__init__(session_name)
        self.main_window_manager = None
        self.tick_every_ms = tick_every_ms

    def find_main_window(self):
        raise NotImplementedError()

    def start(self):
        main_window = self.find_main_window()
        self.main_window_manager = MainWindowManager(
            self, main_window, embed_mode=True
        )
        self.main_window_manager.install()

        timer = QtCore.QTimer(self.main_window_manager.main_window)
        timer.timeout.connect(self.tick)
        timer.start(self.tick_every_ms)

    def register_view_types(self):
        '''
        Subclasses can register view types here.
        '''
        pass

    def _on_cluster_connected(self):
        '''
        Overridden to also dispatch a 'cluster_connection' event to GUI.
        '''
        super(KabaretEmbeddedGUISession, self)._on_cluster_connected()
        self.dispatch_event(
            'cluster_connection',
            cluter_name=self._cluster_actor.get_cluster_name()
        )

    # def dispatch_event(self, event_type, **data):
    #     if self.main_window_manager is not None:
    #         self.main_window_manager.dispatch_event(event_type, data)


class MayaEmbeddedSession(KabaretEmbeddedGUISession):

    def find_main_window(self):
        '''
        My attempt to get maya main window on all maya versions.
        But I only have 2015 right now so I'm kind of going blind 
        for other version :p
        '''
        try:
            from shiboken import wrapInstance
        except ImportError:
            from shiboken2 import wrapInstance

        import maya.OpenMayaUI as omui
        from qtpy import QtWidgets

        main_window_ptr = omui.MQtUtil.mainWindow()
        main_window = wrapInstance(
            long(main_window_ptr), QtWidgets.QMainWindow)
        return main_window
