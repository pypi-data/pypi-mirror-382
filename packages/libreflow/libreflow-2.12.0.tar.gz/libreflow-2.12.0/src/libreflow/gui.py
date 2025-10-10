import sys
import os
import argparse

from kabaret.app.ui import gui
from kabaret.app.ui.gui.styles import Style
from kabaret.app.ui.gui.styles.gray import GrayStyle
from qtpy import QtWidgets, QtGui, QtCore
from kabaret.subprocess_manager import SubprocessManager

from .resources.icons import libreflow
from .resources import file_templates, fonts

CUSTOM_HOME = True
if CUSTOM_HOME:
    from kabaret.app.actors.flow import Flow
    from .custom_home import MyHomeRoot

DEBUG = False

GrayStyle()


class MyStudioGUISession(gui.KabaretStandaloneGUISession):

    def _create_actors(self):
        """
        Instanciate the session actors.
        Subclasses can override this to install customs actors or
        replace default ones.
        """
        if CUSTOM_HOME:
            Flow(self, CustomHomeRootType=MyHomeRoot)
        else:
            return super(MyStudioGUISession, self)._create_actors()
        subprocess_manager = SubprocessManager(self)


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Session Arguments'
    )
    parser.add_argument(
        '-u', '--user', dest='user'
    )
    parser.add_argument(
        '-s', '--site', default=os.getenv('LIBREFLOW_SITE', 'lfs'), dest='site'
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
        '--layout-savepath', default=os.getenv('KABARET_LAYOUT_SAVEPATH', None), dest='layout_savepath', help='Specify Layout Saves Path'
    )
    values, _ = parser.parse_known_args(args)

    if values.site:
        os.environ["KABARET_SITE_NAME"] = values.site
    if values.user:
        os.environ["USER_NAME"] = values.user

    return (
        values.layout_mgr,
        values.layout_autosave,
        values.layout_savepath
    )


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        read_replica_host,
        read_replica_port,
        remaining_args,
    ) = MyStudioGUISession.parse_command_line_args(argv)
    
    layout_mgr, layout_autosave, layout_savepath = process_remaining_args(remaining_args)

    session = MyStudioGUISession(
        session_name=session_name, debug=debug,
        layout_mgr=layout_mgr, layout_autosave=layout_autosave, layout_savepath=layout_savepath
    )
    session.cmds.Cluster.connect(host, port, cluster_name, db, password, read_replica_host, read_replica_port)

    session.start()
    session.close()


if __name__ == "__main__":
    main(sys.argv[1:])
