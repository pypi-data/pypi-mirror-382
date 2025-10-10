

from kabaret import flow

from kabaret.app.ui.gui.widgets.flow.flow_view import CustomPageWidget, QtWidgets, QtCore
from kabaret.app.ui.gui.widgets.editors import editor_factory


class MyCustomPage(CustomPageWidget):

    def create_editor(self, value_oid):
        '''
        This is a rather generic example of using the editor factory
        and the editor class

        :param value_oid: the edited Value Object oid.
        :return: the editor widget.
        '''
        #--- Create the editor based on the ui_config
        ui_config = self.session.cmds.Flow.get_object_ui(value_oid)
        editor_type = ui_config.get('editor_type', None)
        editor = editor_factory().create(
            self, editor_type, ui_config
        )
        #--- Apply Options from ui_config
        editor.apply_options(ui_config)
        editable = ui_config.get('editable', False)
        editor.set_editable(editable)

        #--- Configure the editor setter/getter
        # You may not need to test needs_choices, but
        # this is the generic way to configure
        # the getter for editors:
        value_getter = lambda oid=value_oid: self.session.cmds.Flow.get_value(oid)
        if editor.needs_choices():
            choices_getter = lambda oid=value_oid: self.session.cmds.Flow.get_value_choices(oid)
            getter = lambda: (value_getter(), choices_getter())
        else:
            getter = value_getter
        setter = None
        if editable:
            setter = lambda value, oid=value_oid:self.session.cmds.Flow.set_value(oid, value)
        editor.configure(getter, setter)

        return editor

    def build(self):
        self.label = QtWidgets.QLabel(self)

        self.start_oid = self.oid+'/start'
        self.start_editor = self.create_editor(self.start_oid)

        self.end_oid = self.oid+'/end'
        self.end_editor = self.create_editor(self.end_oid)

        self.scroll_bar = QtWidgets.QScrollBar(QtCore.Qt.Horizontal, self)
        self.scroll_bar.setEnabled(False)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.start_editor)
        hlayout.addWidget(self.end_editor)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.label)
        self.layout().addLayout(hlayout)
        self.layout().addWidget(self.scroll_bar)

        self.start_editor.update()
        self.end_editor.update()
        self.update_label()
        self.update_scroll_bar()

    def nb_frames(self):
        start = self.session.cmds.Flow.get_value(self.start_oid)
        end = self.session.cmds.Flow.get_value(self.end_oid)
        return end - start + 1

    def update_label(self):
        self.label.setText(
            '<h2><font color=#0088FF>Ranges for "{}({} Frames)"</font></h2>'.format(
                self.oid.rsplit('/',1)[-1],
                self.nb_frames()
            )
        )

    def update_scroll_bar(self):
        start = self.session.cmds.Flow.get_value(self.start_oid)
        length = self.nb_frames()
        self.scroll_bar.setPageStep(length)
        self.scroll_bar.setMinimum(1)
        self.scroll_bar.setMaximum(100-length)
        self.scroll_bar.setValue(start)

    def on_touch_event(self, oid):
        '''
        Will be called to receive flow touch events.
        It's up to you do react on not, depending on the oid.

        :param oid: oid of the touched Object
        :return: None
        '''
        update = False
        if oid == self.start_oid:
            self.start_editor.update()
            update = True
        if oid == self.end_oid:
            self.end_editor.update()
            update = True
        if update:
            self.update_label()
            self.update_scroll_bar()

    def die(self):
        pass

class MyObject(flow.Object):

    start = flow.IntParam(1)
    end = flow.IntParam(100)

class CustomPageGroup(flow.Object):

    doc = flow.Label(
        '''
        <hr><h2>
        Using a Custom Page for your object.
        </h2>
        It is possible to show a custom Widget in the Flow View 
        for your objects:
        <pre>
           my_object = flow.Child(MyObject).ui(custom_page="my_studio.gui.MyCustomPage")
        </pre>
        The string "my_studio.gui.MyCustomPage" must point to a subclass of
        "kabaret.app.ui.gui.widgets.flow.flow_view.CustomPageWidget".<br>
        '''
    )
    doc2 = flow.Label(
        '''
        <HR>
        In the example below, you can double click the "My Object" label to show
        its custom page.<br>
        You can still explore the Object relations if you click the [+] 
        (or expand by double click in an empty space on the right).  
        '''
    )

    my_object = flow.Child(MyObject).ui(
        custom_page='dev_studio.flow.unittest_project.showcase.custom_page.MyCustomPage'
    )

    nb_doc = flow.Label(
        '''
        ! Notice how in this example the values and the label gets updated 
        whenever someone changes the values !
        '''
    )

    err_doc = flow.Label(
        '''
        <HR>
        When an error occurs while creating your custom page, a detailed report will
        show up.
        '''
    )
    object_with_module_error = flow.Child(MyObject).ui(
        custom_page='unexisting_module.MyCustomPage'
    )
    object_with_class_name_error = flow.Child(MyObject).ui(
        custom_page='dev_studio.flow.unittest_project.showcase.custom_page.UnexistingClass'
    )
