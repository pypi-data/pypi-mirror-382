"""
Defines the kabaret plugin that will automatically declare the view in all sessions.
"""

from kabaret.app import plugin

from .script_view import ScriptView


class ScriptViewPlugin:
    @plugin(trylast=True)
    def install_views(session):
        if not session.is_gui():
            return

        from qtpy import QtCore

        type_name = session.register_view_type(ScriptView)
        session.add_view(type_name, hidden=True, area=QtCore.Qt.RightDockWidgetArea)
