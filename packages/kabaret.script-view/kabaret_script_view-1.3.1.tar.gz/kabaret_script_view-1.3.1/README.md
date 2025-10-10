# kabaret.script_view

The kabaret.script_view package is a kabaret GUI extension.

It defines a "Script" view where you can edit and execute python scripts using 'self' as a selected flow Object.

It also defines the handy "pyscript" editor that you can use to show/edit python code in your `flow.Param`
(it is registered automatically by importing `kabaret.script_view`).

And finally, it defines `kabaret.pyscript_flow.PyScriptValue` which is a `flow.values.Value` with the "pyscript" 
editor and an browsable history of every edits (with time, author, location, editable comments...)


