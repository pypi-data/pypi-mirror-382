
import os, sys

# make kabaret available:
KABARET_INSTALL_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
         '..', '..', '..', '..',
         'kabaret', 'python'
    )
)
if not KABARET_INSTALL_PATH in sys.path:
    sys.path.append(KABARET_INSTALL_PATH)

SCRIPTVIEW_INSTALL_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', '..'
    )
)
if not SCRIPTVIEW_INSTALL_PATH in sys.path:
    sys.path.append(SCRIPTVIEW_INSTALL_PATH)

import kabaret.app.ui.gui as gui
import kabaret.script_view as script_view


class TestSession(gui.KabaretStandaloneGUISession):

    def register_view_types(self):
        super(TestSession, self).register_view_types()
        
        type_name = self.main_window_manager.register_view_type(script_view.ScriptView)
        self.main_window_manager.add_view(type_name)


def run_test_session():
    
    host = '192.168.1.215'
    port = '6379'
    cluster_name = 'SMKS_DEV'
    db_index = '3'
    password = None

    session_name = 'ScripView_Test'

    session = TestSession(session_name=session_name)
    session.cmds.Cluster.connect(host, port, cluster_name, db_index, password)
    session.start()
    session.close()


if __name__ == '__main__':
    run_test_session()