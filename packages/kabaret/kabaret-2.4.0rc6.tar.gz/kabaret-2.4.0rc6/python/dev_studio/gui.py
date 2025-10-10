
import sys
import argparse

from kabaret.app.ui import gui

from .icons import gui as _  # register our icons.gui resourses
from .icons import flow as _  # register our icons.flow resourses


from kabaret.app.ui.gui.styles import Style
from qtpy import QtWidgets, QtGui

from kabaret.app.ui.gui.widgets.session_toolbar import SessionToolBar

# To test the custom home:
CUSTOM_HOME = True
CUSTOM_HOME = False
if CUSTOM_HOME:
    from kabaret.app.actors.flow import Flow
    from .flow.custom_home import MyHomeRoot

class MyStyle(Style):
    '''
    This is to show how to add a style to the app, and make it the default one.
    Beware that a style needs more than this to be readable (tabbed dock window and
    splitters need some luvin'!)

    '''

    def __init__(self):
        super(MyStyle, self).__init__('MyStyle')

    def apply(self, widget):

        app = QtWidgets.QApplication.instance()

        if widget is app:
            # setup the palette
            palette = QtWidgets.QApplication.palette()

            # A color to indicate a selected item or the current item. By default, the highlight color is Qt.darkBlue.
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(80, 0, 0))

            QtWidgets.QApplication.setPalette(palette)

# Uncomment this to activate MyStyle
# MyStyle() # install my style (the last installed is set as default)


class MyStudioGUISession(gui.KabaretStandaloneGUISession):

    def register_view_types(self):
        super(MyStudioGUISession, self).register_view_types()

        type_name = self.register_view_type(SessionToolBar)
        self.add_view(type_name)

    def _create_actors(self):
        '''
        Instanciate the session actors.
        Subclasses can override this to install customs actors or
        replace default ones.
        '''
        if CUSTOM_HOME:
            Flow(self, CustomHomeRootType=MyHomeRoot)
        else:
            return super(MyStudioGUISession, self)._create_actors()


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Kabaret Session Arguments'
    )
    parser.add_argument(
        '--layout-mgr', default=False, action='store_true', dest='layout_mgr', help='Enable Layout Manager'
    )
    parser.add_argument(
        '--no-layout-mgr', action='store_false', dest='layout_mgr', help='Disable Layout Manager'
    )
    parser.add_argument(
        '--layout-autosave', default=False, action='store_true', dest='layout_autosave', help='Use Layout Autosave'
    )
    parser.add_argument(
        '--no-layout-autosave', action='store_false', dest='layout_autosave', help='Disable Layout Autosave'
    )
    parser.add_argument(
        '--layout-savepath', default=None, dest='layout_savepath', help='Specify Layout Saves Path'
    )
    values, _ = parser.parse_known_args(args)

    return (
        values.layout_mgr,
        values.layout_autosave,
        values.layout_savepath
    )


if __name__ == '__main__':
    argv = sys.argv[1:]  # get ride of first args wich is script filename
    (
        session_name,
        host, port, cluster_name,
        db_index, password, debug,
        read_replica_host, read_replica_port,
        remaining_args
    ) = MyStudioGUISession.parse_command_line_args(argv)

    layout_mgr, layout_autosave, layout_savepath = process_remaining_args(remaining_args)

    session = MyStudioGUISession(
        session_name=session_name, debug=debug,
        layout_mgr=layout_mgr, layout_autosave=layout_autosave, layout_savepath=layout_savepath
    )
    session.cmds.Cluster.connect(host, port, cluster_name, db_index, password, read_replica_host, read_replica_port)

    session.start()
    session.close()
