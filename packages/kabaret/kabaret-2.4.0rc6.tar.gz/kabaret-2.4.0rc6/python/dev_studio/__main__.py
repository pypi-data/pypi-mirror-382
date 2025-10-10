import sys

from qtpy import QtCore

from kabaret.app.ui import gui

from kabaret.app.actors.flow import Flow

_has_button_page_and_script_view = False
try:
    from kabaret.flow_button_pages import ButtonHomeRoot
    from kabaret.script_view.script_view import ScriptView
except ImportError:
    pass
else:
    _has_button_page_and_script_view = True


class MyGUISession(gui.KabaretStandaloneGUISession):

    def _create_actors(self):
        if _has_button_page_and_script_view:
            Flow(self, CustomHomeRootType=ButtonHomeRoot)
        else:
            return super()._create_actors()

    def register_view_types(self):
        if _has_button_page_and_script_view:
            type_name = self.register_view_type(ScriptView)
            self.add_view(type_name, hidden=False, area=QtCore.Qt.RightDockWidgetArea)

            self.main_window_manager.main_window.resize(3000, 2000)

        return super().register_view_types()


def start_kabaret(args):
    session_name="dev_studio"
    host = 'redis.test.com'
    port="6379"
    cluster_name="DEV_STUDIO"
    db_index="0"
    password='SUPER_SECRET_PASSWORD'
    read_replica_host = host # set None to deactivate read replica
    read_replica_port = '6378'

    debug = True
    layout_mgr = False
    layout_autosave = False
    layout_savepath = None

    if args:
        # Use -h in command line to see the flags!
        (
            session_name,
            host, port, cluster_name,
            db_index, password, debug,
            read_replica_host, read_replica_port,
            layout_mgr, layout_autosave, layout_savepath,
            remaining_args
        ) = MyGUISession.parse_command_line_args(args)
    print('Will connect using:', (
        session_name,
        host, port, cluster_name,
        db_index, password, debug,
        read_replica_host, read_replica_port,
    ))

    session = MyGUISession(
        session_name=session_name, 
        debug=debug, 
        layout_mgr=layout_mgr, layout_autosave=layout_autosave, layout_savepath=layout_savepath,
    )
    session.cmds.Cluster.connect(
        host=host,
        port=port,
        cluster_name=cluster_name,
        db_index=db_index,
        password=password,
        read_replica_host=read_replica_host,
        read_replica_port=read_replica_port,
    )
    session.start()
    session.close()


if __name__ == "__main__":
    start_kabaret(sys.argv[1:])
