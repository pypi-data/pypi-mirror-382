from __future__ import print_function

from qtpy import QtWidgets, QtGui, QtCore


class ScriptLine(QtWidgets.QWidget):

    def __init__(self, parent, flow_view):
        super(ScriptLine, self).__init__(parent)
        self.flow_view = flow_view

        self.le = QtWidgets.QLineEdit(self)
        self.le.returnPressed.connect(self._on_return)
        self.le.setToolTip(
            'Enter the method to call on this object, or "?" to list them.')

        help_bt = QtWidgets.QPushButton('?')
        help_bt.clicked.connect(self._on_help_bt)

        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self.le, 100)
        self.layout().addWidget(help_bt)

    def _on_return(self):
        return self.execute_object_call(str(self.le.text()).strip())

    def _on_help_bt(self):
        callables = self.execute_object_call('?')
        m = QtWidgets.QMenu()
        for name, specs in callables:
            a = m.addAction(name)
            a.triggered.connect(lambda checked=None, n=name, s=specs: self._use(n, s))
        m.exec_(QtGui.QCursor.pos())

    def _use(self, name, specs):
        (args, varargs, kw, defaults) = specs
        args.pop(0)  # drop the 'self'
        if not args:
            cmd = name + '()'
        else:
            cmd = '%s(%s)' % (name, ', '.join(args))

        self.le.setText(cmd)

    def execute_object_call(self, call_text):
        class CallRec(object):

            def __init__(self, name):
                super(CallRec, self).__init__()

                self.name = name
                self.args = ()
                self.kwargs = {}

            def __call__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

            def __str__(self):
                return '%s(*%r, **%r)' % (self.name, self.args, self.kwargs)

        class Context(dict):

            def __init__(self):
                super(Context, self).__init__()

                self.calls = []

            def __getitem__(self, name):
                call = CallRec(name)
                self.calls.append(call)
                return call

        session = self.flow_view.session
        oid = self.flow_view.flow_page.current_oid()
        text = call_text.strip()
        for cmd in [t.strip() for t in text.split(';')]:
            if not cmd:
                continue
            if cmd == '?':
                result = session.cmds.Flow.call(oid, '?', (), {})
                for name, argspecs in result:
                    (args, varargs, kw, defaults) = argspecs
                return result

            else:
                context = Context()
                eval(cmd, context, context)
                if context.calls:
                    call = context.calls[0]
                    result = session.cmds.Flow.call(
                        oid, call.name, call.args, call.kwargs)
                    return result
