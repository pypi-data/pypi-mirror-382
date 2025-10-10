import os
import sys
import logging

from kabaret.app.ui.gui.embedded import MayaEmbeddedSession

from kabaret.app.ui.gui.widgets.flow.flow_view import FlowView, FlowContextView


class MyStudioMayaSession(MayaEmbeddedSession):

    def register_view_types(self):
        type_name = self.main_window_manager.register_view_type(FlowView)
        #self.main_window_manager.add_view(type_name)

        type_name = self.main_window_manager.register_view_type(
            FlowContextView
        )
        self.main_window_manager.add_view(type_name)


def install_kabaret():
    logging.getLogger('kabaret.demo').info('ACTUAL INSTALL')

    session = MyStudioMayaSession(session_name="MyStudioMaya")
    session.cmds.Cluster.connect_from_env()
    session.start()
    sys.kabaret_session = session   # What... Yes I can :p
