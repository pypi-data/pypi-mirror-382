import time
import getpass
import socket 

from kabaret import flow


class EventLogEntry(flow.Object):

    log = flow.Parent(2)

    comments = flow.Param('').ui(editor='textarea')

    time = flow.Param().ui(editable=False, editor="datetime")
    by = flow.Param('').ui(editable=False)
    on = flow.Param('').ui(editable=False)
    event = flow.Param('').ui(editable=False)
    data = flow.Param('').ui(editable=False, editor="textarea")

class EventLog(flow.Map):

    @classmethod
    def mapped_type(cls):
        return EventLogEntry

    def mapped_names(self, *args, **kwargs):
        return tuple(
            reversed(
                super(EventLog, self).mapped_names(*args, **kwargs)
            )
        )

    def columns(self):
        return ['Time', 'By', 'On', 'Event', 'Comments']

    def _fill_row_cells(self, row, item):
        row.update(dict(
            Time=time.ctime(item.time.get()),
            By=item.by.get(),
            On=item.on.get(),
            Event=item.event.get(),
            Comments=item.comments.get().replace('\n', ' | ')
        ))

class ValueEditLog(flow.Object):

    back = flow.Parent(2)
    _value = flow.Parent()
    events = flow.Child(EventLog).ui(expanded=True)

    def add_event(self, event_name, event_data):
        name = 'E{:04}'.format(len(self.events)+1)
        event = self.events.add(name)
        event.time.set(time.time())
        event.by.set(getpass.getuser())
        event.on.set(socket.getfqdn())
        event.event.set(event_name)
        event.data.set(event_data)
        self.events.touch()
        return event

class ShowLogAction(flow.Action):

    _value = flow.Parent()

    def needs_dialog(self):
        return False
    
    def run(self, button):
        return self.get_result(goto=self._value.log.oid())

class PyScriptValue(flow.values.Value):

    DEFAULT_EDITOR = 'pyscript'

    log = flow.Child(ValueEditLog)
    show_log = flow.Child(ShowLogAction)

    def set(self, value):
        print('!!!!', value)
        self.log.add_event('edit', value)
        super(PyScriptValue, self).set(value)
