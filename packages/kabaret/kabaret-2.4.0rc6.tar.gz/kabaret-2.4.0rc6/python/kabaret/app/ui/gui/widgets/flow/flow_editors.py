

raise Exception("OBSOLETE")

# from ..editors import EditorFactory

# from ..editors.python_value import PythonValueEditor


# _FACTORY = None


# class FlowPythonValueEditor(PythonValueEditor):

#     def fetch_value(self):
#         '''
#         Must be implemented to return the value to show.
#         '''
#         return self.session.cmds.Flow.get_value(self.value_id)

#     def apply_edited_value(self):
#         '''
#         Must be implemented to apply the value returned 
#         by self.get_edited_value()
#         '''
#         self.session.cmds.Flow.set_value(
#             self.value_id, self.get_edited_value()
#         )


# class FlowEditorFactory(EditorFactory):

#     def __init__(self, session):
#         super(FlowEditorFactory, self).__init__()
#         self.session = session

#     def create(self, value_id, editor_type_name, options, parent):
#         editor = super(FlowEditorFactory, self).create(
#             value_id, editor_type_name, options, parent
#         )
#         editor.session = self.session
#         return editor

# def flow_editor_factory(session):
#     global _FACTORY
#     if _FACTORY is None:
#         _FACTORY = FlowEditorFactory(session)
#         _FACTORY.register_editor_type(FlowPythonValueEditor)
#     else:
#         # we never know (which is a desing flaw, I know :p)
#         _FACTORY.session = session 
#     return _FACTORY