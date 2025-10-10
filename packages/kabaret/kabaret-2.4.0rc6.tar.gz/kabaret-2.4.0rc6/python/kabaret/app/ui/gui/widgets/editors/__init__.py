'''
    Value Editor Factory
'''

from .python_value import PythonValueEditor
from .bool_value import BoolValueEditor
from .choice_value import ChoiceValueEditor
from .multichoice_value import MultiChoiceValueEditor
from .textarea import TextAreaEditor
from .label import LabelEditor
from .password_value import PasswordEditor
from .time_value import DateTimeValueEditor, DateValueEditor
from .percent_value import PercentValueEditor
from .thumbnail import ThumbnailEditor
from .path_value import PathValueEditor
from .image_value import ImageValueEditor


_FACTORY = None


class EditorFactory(object):

    def __init__(self):
        super(EditorFactory, self).__init__()
        self._editor_types = []

    def register_editor_type(self, editor_type):
        self._editor_types.append(editor_type)

    def create(self, parent, editor_type_name, options={}):
        # (! reverse the editor type list to have the first reg as default)
        for T in reversed(self._editor_types):
            if T.can_edit(editor_type_name):
                editor = T(parent, options)
                return editor
        raise ValueError(
            'Could not find an editor for %r' % (
                editor_type_name,
            )
        )


def editor_factory():
    global _FACTORY
    if _FACTORY is None:
        _FACTORY = EditorFactory()
        # ! be sure to register this one as the first one as it is universal
        _FACTORY.register_editor_type(PythonValueEditor)
        _FACTORY.register_editor_type(PasswordEditor)
        _FACTORY.register_editor_type(BoolValueEditor)
        _FACTORY.register_editor_type(ChoiceValueEditor)
        _FACTORY.register_editor_type(MultiChoiceValueEditor)
        _FACTORY.register_editor_type(TextAreaEditor)
        _FACTORY.register_editor_type(LabelEditor)
        _FACTORY.register_editor_type(DateTimeValueEditor)
        _FACTORY.register_editor_type(DateValueEditor)
        _FACTORY.register_editor_type(PercentValueEditor)
        _FACTORY.register_editor_type(ThumbnailEditor)
        _FACTORY.register_editor_type(PathValueEditor)
        _FACTORY.register_editor_type(ImageValueEditor)

    return _FACTORY
