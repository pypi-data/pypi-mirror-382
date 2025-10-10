
from kabaret.app.ui.gui.widgets.editors.interface import Editor_Interface


from qtpy import QtWidgets, QtCore, QtGui

from six import text_type as unicode

from kabaret.app.ui.gui.widgets.event_filters import IgnoreMouseButton

from .script_view.pythoneditor import CodeEditor
from .script_view import syntax, syntaxstyles


class DropProcessor(object):

    def process_drop(self, mime_data):
        pass

class PyScriptEditor(QtWidgets.QWidget, Editor_Interface):
    '''
    This editor lets you edit python code text value.

    You can:
    - Ctrl+Return to save edits
    - Escape to revert change (No confirmation !!!)
    - Ctrl+MouseWheel to change zoom

    Editor Type Names:
        pyscript

    Options:
        buttons_side:    top/bottom/left/right - defaults to right
        default_height:  default height for the text area (middle mouse to resize)
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        return editor_type_name in ('pyscript',)

    def __init__(self, parent, options):
        QtWidgets.QWidget.__init__(self, parent)
        Editor_Interface.__init__(self, parent)

        self.default_height = 100
        self._last_loaded_txt = None

        self.build_ui()
        self.apply_options(options)
    
    def _exec_code(self):
        print("No way I'll do this.")

    def build_ui(self):
        self.drop_processor = DropProcessor()
        self._te = CodeEditor(self.drop_processor, self)
        self._te.exec_request.connect(self._exec_code)
        self._te.viewport().installEventFilter(IgnoreMouseButton(self._te))

        self.highlight = syntax.PythonHighlighter(
            self._te.document(), syntaxstyles.BreezeDarkSyntaxStyle())
        p = self._te.palette()
        p.setColor(QtGui.QPalette.Base, syntaxstyles.BreezeDarkSyntaxStyle()[
                   'background'].foreground().color())
        p.setColor(QtGui.QPalette.Text, syntaxstyles.BreezeDarkSyntaxStyle()[
                   'foreground'].foreground().color())
        self._te.setPalette(p)

        self.setLayout(QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight))
        self.layout().setContentsMargins(1, 2, 1, 2)
        self.layout().setSpacing(1)

        self.layout().addWidget(self._te)

        self.build_buttons()
    
    def build_buttons(self):
        self._apply_button = QtWidgets.QToolButton(self)
        self._apply_button.setToolTip('Ctrl+Enter')
        self._apply_button.setText('Apply')
        self._apply_button.clicked.connect(self._apply_edit)
        self._apply_button.setShortcut(QtGui.QKeySequence("Ctrl+Return"))
        self._apply_button.setEnabled(False)
        self._apply_button.setVisible(False)

        self._cancel_button = QtWidgets.QToolButton(self)
        self._cancel_button.setToolTip('Escape')
        self._cancel_button.setText('Cancel')
        self._cancel_button.clicked.connect(self._on_cancel)
        self._cancel_button.setShortcut(QtGui.QKeySequence("Escape"))
        self._cancel_button.setEnabled(False)
        self._cancel_button.setVisible(False)

        self.buttons_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(0)

        self.buttons_layout.addWidget(self._apply_button)
        self.buttons_layout.addStretch(100)
        self.buttons_layout.addWidget(self._cancel_button)
        self.layout().addLayout(self.buttons_layout)

    def sizeHint(self):
        # return QtCore.QSize(self.default_height, 100)
        return QtCore.QSize(100, self.default_height)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue should also be given to the user.
        '''
        self._te.setReadOnly(not b)
        self._apply_button.setVisible(b)
        self._cancel_button.setVisible(b)
        if b:
            self._te.textChanged.connect(self._on_edited)

    def set_button_side(self, side):
        d1, d2 = dict(
            bottom=(QtWidgets.QBoxLayout.TopToBottom, QtWidgets.QBoxLayout.LeftToRight), 
            top=(QtWidgets.QBoxLayout.BottomToTop, QtWidgets.QBoxLayout.LeftToRight),
            left=(QtWidgets.QBoxLayout.RightToLeft, QtWidgets.QBoxLayout.TopToBottom),
            right=(QtWidgets.QBoxLayout.LeftToRight, QtWidgets.QBoxLayout.TopToBottom),
        ).get(str(side).lower(), (None, None))
        if d1 is None:
            return self.set_button_side('right')

        self.layout().setDirection(d1)
        self.buttons_layout.setDirection(d2)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        self.set_button_side(options.get('buttons_side'))
        self.default_height = options.get('default_height', 100)

    def _set_buttons_enabled(self, b):
        self._apply_button.setEnabled(b)
        self._apply_button.setVisible(b)

        self._cancel_button.setEnabled(b)
        self._cancel_button.setVisible(b)

    def _on_cancel(self):
        self.update()

    def _apply_edit(self):
        self.apply()

    def update(self):
        '''
        Must be implemented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        txt = unicode(self.fetch_value() or '')
        self._last_loaded_txt = txt
        self._te.setPlainText(txt)
        self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        value = self._te.toPlainText()
        return value

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        if self.get_edited_value() == self._last_loaded_txt:
            self._show_clean()
            return
        self._set_buttons_enabled(True)
        self._te.setProperty('edited', True)
        self._te.setProperty('applying', False)
        # self.style().unpolish(self._te)
        self.style().polish(self._te)

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        self._set_buttons_enabled(False)
        self._te.setProperty('edited', False)
        self._te.setProperty('applying', True)
        # self.style().unpolish(self._te)
        self.style().polish(self._te)

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is
        up to date.
        '''
        self._set_buttons_enabled(False)
        self._te.setProperty('edited', False)
        self._te.setProperty('applying', False)
        # self.style().unpolish(self._te)
        self.style().polish(self._te)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self._set_buttons_enabled(False)
        self._te.setProperty('edited', False)
        self._te.setProperty('applying', False)
        self._te.setProperty('error', True)
        self.style().unpolish(self._te)
        self.style().polish(self._te)
        self.setToolTip('!!!\nERROR: %s' % (error_message,))

