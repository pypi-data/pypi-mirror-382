
from __future__ import print_function

import sys
import traceback

from qtpy import QtWidgets, QtGui, QtCore

from qtpy.QtGui import QTextCursor

from kabaret.app.ui.gui.widgets.widget_view import DockedView
from kabaret.app.ui.gui.widgets.flow.navigator import Navigator
from kabaret.app.ui.gui.widgets.flow.navigation_control import (
    NavigationOIDControls,
    NavigationHistoryControls
)


from .pythoneditor import CodeEditor
from . import syntax, syntaxstyles

def register_pyscript_editor():
    from ..pyscript_editor import PyScriptEditor
    from kabaret.app.ui.gui.widgets.editors import editor_factory
    factory = editor_factory()
    if PyScriptEditor not in factory._editor_types:
        factory.register_editor_type(PyScriptEditor)

# Autmatically register our nice pyscript editor:
register_pyscript_editor()


class ScriptEditor(QtWidgets.QTextEdit):

    def __init__(self, view, parent):
        super(ScriptEditor, self).__init__(parent)
        self.view = view
        self.session = view.session

    def dropEvent(self, event):
        md = {}
        mime_data = event.mimeData()
        for format in mime_data.formats():
            md[format] = mime_data.data(format).data()
        oids, urls = self.session.cmds.Flow.from_mime_data(md)

        if not oids:
            return super(ScriptEditor, self).dropEvent(event)

        self.view.goto(oids[0])


class StdCapture(object):

    def __init__(self, outputtextedit):
        super(StdCapture, self).__init__()
        self.outputtextedit = outputtextedit
        self._revert_stdout = None
        self._revert_stderr = None

    def start_capture(self):
        if self._revert_stdout is not None:
            print('Already Capturing !')

        self._revert_stdout = sys.stdout
        self._revert_stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def stop_capture(self):
        sys.stdout = self._revert_stdout
        sys.stderr = self._revert_stderr
        self._revert_stdout = None
        self._revert_stderr = None

    def write(self, text, view=None):
        try:
            doc = self.outputtextedit.document()
            cursor = QTextCursor(doc)
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(text)
            self.outputtextedit.ensureCursorVisible()
        except:
            import traceback
            m = traceback.format_exc()
            self._revert_stderr.write('ERROR !\n' + m)


class OutPutTextEdit(QtWidgets.QPlainTextEdit):

    INTRO_TEXT = (
        'CTRL+Enter on selected text to run it.\n'
        'CTRL+Enter without selection to run the whole script.\n'
        '\n'
        'CTRL+Backspace to clear output\n'
        'CTRL+Wheel to Zoom In/Out in a text area\n'
        'CTRL++ / CTRL+- to Zoom In/Out both text area\n'
    )

    def __init__(self, view, parent=None):
        super(OutPutTextEdit, self).__init__(parent)
        self.view = view

        self.setReadOnly(True)
        doc = self.document()
        font = doc.defaultFont()
        font.setFamily('Monospace')
        doc.setDefaultFont(font)

        self.setAcceptDrops(True)

        self._std_capture = StdCapture(self)
        self.clear()

    def clear(self):
        super(OutPutTextEdit, self).clear()
        try:
            self.setPlaceholderText(self.INTRO_TEXT)
        except AttributeError:
            # Not available before Qt5.3
            self.setPlainText(self.INTRO_TEXT)

    def dragEnterEvent(self, event):
        # this is so that dropEvent(event) is called even with setReadOnly(True)
        self.setReadOnly(False)
        super(OutPutTextEdit, self).dragEnterEvent(event)

    def dropEvent(self, event):
        try:
            handled = self.view.process_drop(event.mimeData())
        finally:
            self.setReadOnly(True)
        if not handled:
            super(CodeEditor, self).dropEvent(event)

    def dragLeaveEvent(self, event):
        self.setReadOnly(True)
        super(OutPutTextEdit, self).dragLeaveEvent(event)

    def start_capture_std(self):
        self._std_capture.start_capture()
        return self._std_capture

    def stop_capture_std(self):
        self._std_capture.stop_capture()


class ScriptView(DockedView):

    @classmethod
    def view_type_name(cls):
        return 'Script'

    def __init__(
        self, session, view_id, hidden=False, area=None, oid=None
    ):
        self.output = None
        self._show_events = False
        self._start_oid = oid
        super(ScriptView, self).__init__(session, view_id, hidden=hidden, area=area)
        self._globals_dict = {"__name__": "__kabaret_script_view__"}
        self._clear_output()
        
    def receive_event(self, event, data):
        if self._show_events and self.output is not None:
            self.output._std_capture.write('[EVENT: %s] %r\n' % (event, data))
        if event == "focus_changed":
            # Update dock title bar background color depending on the active view status
            view_id = data["view_id"]
            self.dock_widget().setProperty(
                "current", True if view_id == self.view_id() else False
            )
            self.dock_widget().style().polish(self.dock_widget())
            self.dock_widget().update()

    def dropEvent(self, event):
        print(event)

    def _build(
        self,
        top_parent, top_layout, main_parent, header_parent, header_layout
    ):
        self.add_header_tool('*', '*', 'Duplicate View', self.create_view)

        # ---- View Menu Actions
        a = self.view_menu.addAction('Font Size +', self._font_size_incr)
        a.setShortcut(
            QtGui.QKeySequence(
                QtCore.Qt.CTRL | QtCore.Qt.Key_Plus
            )
        )
        a = self.view_menu.addAction('Font Size -', self._font_size_decr)
        a.setShortcut(
            QtGui.QKeySequence(
                QtCore.Qt.CTRL | QtCore.Qt.Key_Minus
            )
        )

        a = self.view_menu.addAction('Clear Output', self._clear_output)
        a.setShortcut(
            QtGui.QKeySequence(
                QtCore.Qt.CTRL | QtCore.Qt.Key_Backspace
            )
        )

        self.view_menu.addAction('Clear Script', self._clear_script)

        self._toggle_events_action = self.view_menu.addAction(
            'Log Events', self._toggle_event_logging
        )
        self._toggle_events_action.setCheckable(True)
        self._toggle_events_action.setChecked(self._show_events)

        # -----

        self._navigator = Navigator(
            self.session, None, self._start_oid
        )
        self._navigator.set_create_view_function(self.create_view)
        self._navigator.add_on_current_changed(self._on_nav_changed)

        self.nav_ctrl = NavigationHistoryControls(top_parent, self._navigator)
        self.nav_oid = NavigationOIDControls(top_parent, self._navigator)

        top_layout.addWidget(self.nav_ctrl)
        top_layout.addWidget(self.nav_oid, 100)

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        main_parent.setLayout(lo)

        if 0:
            self.editor = ScriptEditor(self, main_parent)
        else:
            self._build_code_editor(main_parent)

        self._on_nav_changed()

    def _build_code_editor(self, parent):
        self.splitter = QtWidgets.QSplitter(parent)
        self.splitter.setOrientation(QtCore.Qt.Vertical)

        self.output = OutPutTextEdit(self, self.splitter)
        self.editor = CodeEditor(self, self.splitter)
        self.editor.exec_request.connect(self._exec_code)

        self.highlight = syntax.PythonHighlighter(
            self.editor.document(), syntaxstyles.BreezeDarkSyntaxStyle())
        p = self.editor.palette()
        p.setColor(QtGui.QPalette.Base, syntaxstyles.BreezeDarkSyntaxStyle()[
                   'background'].foreground().color())
        p.setColor(QtGui.QPalette.Text, syntaxstyles.BreezeDarkSyntaxStyle()[
                   'foreground'].foreground().color())
        self.editor.setPalette(p)

        parent.layout().addWidget(self.splitter)

    def _font_size_incr(self):
        self.editor.zoomIn()
        self.output.zoomIn()

    def _font_size_decr(self):
        self.editor.zoomOut()
        self.output.zoomOut()

    def _toggle_event_logging(self):
        self._show_events = not self._show_events
        self._toggle_events_action.setChecked(self._show_events)

    def _clear_script(self):
        self.editor.clear()

    def _clear_output(self):
        self.output.clear()

    def goto(self, oid):
        self._navigator.goto(oid)

    def _on_nav_changed(self):
        view_title = self.session.cmds.Flow.get_source_display(
            self.current_oid())
        self.set_view_title('Script @ %s' % (view_title,))
        self.nav_oid.update()

    def current_oid(self):
        return self._navigator.current_oid()

    def create_view(self, oid=None):
        if oid is None:
            oid = self.current_oid()
        self.duplicate_view(oid=oid)

    def process_drop(self, mime_data):
        '''
        Returns True if the mime_data were handled.
        '''
        md = {}
        for format in mime_data.formats():
            md[format] = mime_data.data(format).data()
        oids, urls = self.session.cmds.Flow.from_mime_data(md)

        if not oids:
            return False

        self.goto(oids[0])
        return True

    def _exec_code(self, script):
        output = self.output.start_capture_std()
        output.write('\n===========================\n')
        output.write('with self => %s\n' % (self.current_oid(),))

        try:
            self._globals_dict = self.session.cmds.Flow.exec_script(
                self.current_oid(), script, self._globals_dict
            )
        except:
            m = traceback.format_exc()
            output.write(m + '\n')
        finally:
            self.output.stop_capture_std()
