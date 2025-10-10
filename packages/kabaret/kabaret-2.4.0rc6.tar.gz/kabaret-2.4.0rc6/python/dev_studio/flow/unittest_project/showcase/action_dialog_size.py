from kabaret import flow

class CheckSizeAction(flow.Action):

    _parent = flow.Parent()

    def allow_context(self, context):
        return context.endswith('.details')

    def needs_dialog(self):
        return True

    def get_buttons(self):
        size = self._parent.default_size.get()
        min_size = self._parent.minimum_size.get()
        max_size = self._parent.maximum_size.get()

        if size == min_size == max_size == 'disabled':
            msg = (
                "<p>This Action dialog has been resized according to its content "
                "since no option was provided.</p>"
            )
        else:
            msg = ""

            if size is not None and size != (-1, -1):
                if (min_size is not None and size < min_size) or (max_size is not None and size > max_size):
                    msg += (
                        "<p>The size of this Action dialog has been computed to "
                        "fit its content (out of provided range)."
                    )
                else:
                    msg += f"<p>The default size of this Action dialog is <b>{str(size)}</b>.</p>"
            else:
                msg += (
                    f"<p>The size of this Action dialog has been computed to "
                    "fit its content (default size).</p>"
                )
            if min_size is not None and min_size != (-1, -1):
                msg += f"<p>You cannot resize it below <b>{str(min_size)}</b>.</p>"
            if max_size is not None and max_size != (-1, -1):
                msg += f"<p>You cannot resize it beyond <b>{str(max_size)}</b>.</p>"
        
        self.message.set(f"<html>{msg}</html>")
        
        return ['Nice']

    def run(self, button):
        return None

    def _fill_ui(self, ui):
        size = self._parent.default_size.get()

        if size is not None:
            ui['dialog_size'] = size

        min_size = self._parent.minimum_size.get()

        if min_size is not None:
            ui['dialog_min_size'] = min_size

        max_size = self._parent.maximum_size.get()

        if max_size is not None:
            ui['dialog_max_size'] = max_size

class EditSizeAction(flow.Action):

    width = flow.SessionParam(0).ui(editor='int')
    height = flow.SessionParam(0).ui(editor='int')

    _size = flow.Parent()
    _options = flow.Parent(2)

    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def needs_dialog(self):
        size = self._size.get() or self._size._default_value
        self.width.set(size[0])
        self.height.set(size[1])
        
        return True

    def get_buttons(self):
        return ['Save', 'Reset', 'Cancel']
    
    def run(self, button):
        if button == 'Cancel':
            return
        
        if button == 'Reset':
            self._size.revert_to_default()
        else:
            self._size.set((self.width.get(), self.height.get()))

class DisableSizeAction(flow.Action):

    _size = flow.Parent()

    def allow_context(self, context):
        return context and context.endswith('.inline')
    
    def needs_dialog(self):
        return False
    
    def run(self, button):
        self._size.set(None)

class EditableSizeValue(flow.values.SessionValue):

    edit = flow.Child(EditSizeAction)
    disable = flow.Child(DisableSizeAction)

class DialogSizeOptions(flow.Object):

    doc = flow.Label(
        "You can tweak the different size options below and "
        "see their effects on the behaviour of the Action dialog."
    )
    
    default_size = flow.SessionParam((256, 256), EditableSizeValue).watched().ui(editable=False)
    minimum_size = flow.SessionParam((128, 128), EditableSizeValue).watched().ui(editable=False)
    maximum_size = flow.SessionParam((512, 512), EditableSizeValue).watched().ui(editable=False)

    code = flow.Computed().ui(editor='textarea', html=True, editable=False)

    check_size_result = flow.Child(CheckSizeAction)

    def child_value_changed(self, child_value):
        if child_value in (self.default_size, self.minimum_size, self.maximum_size):
            self.code.touch()

    def compute_child_value(self, child_value):
        if child_value is self.code:
            ui = {}
            if self.default_size.get() is not None:
                ui['dialog_size'] = self.default_size.get()
            if self.minimum_size.get() is not None:
                ui['dialog_min_size'] = self.minimum_size.get()
            if self.maximum_size.get() is not None:
                ui['dialog_max_size'] = self.maximum_size.get()
            
            code = "<pre>action = Child(Action)"
            if ui:
                code += ".ui(<br>{}<br>)".format(',<br>'.join([f'    {k}={v}' for k, v in ui.items()]))
            
            self.code.set(code + "</pre>")