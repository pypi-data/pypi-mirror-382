
import random

from kabaret import flow

from kabaret.app import resources

class ResourceIconObject(flow.Object):

    ICON = ('icons.status', 'DONE')

    doc = flow.Label(
        'The icon must be a 2d tuple leading to an image '
        'resource (see the Icons section at the root of '
        'this project).'
    )

class MapExample(flow.DynamicMap):

    @classmethod
    def mapped_type(cls):
        return flow.Object

    def mapped_names(self, page_num=0, page_size=None):
        return ['Item{}'.format(i) for i in range(10)]

    def columns(self):
        return ['Name', 'Col1', 'Col2']

    def _fill_row_cells(self, row, item):
        row.update(dict(
            Name=item.name(),
            Col1=item.name()+'@col1',
            Col2=item.name()[-1],
        ))

    def _fill_row_style(self, style, item, row):
        statuses = resources.list_folder('icons.gui')
        status = random.choice(statuses)
        bg = '#FF8800' # may also be like (255, 127, 0)
        fg = '#008888'
        if int(row['Col2'])%3:
            bg = '#00FF00'
            fg = '#004400'
        status2 = random.choice(statuses)
        style.update({
            'icon':('icons.gui', status),
            'Col1_foreground_color':fg,
            'Col1_background_color':bg,
            'Col2_icon':('icons.gui', status2),
        })

class AlteredIconValue(flow.values.Value):

    EDITABLE = True

    def _fill_ui(self, ui):
        status = random.choice(
            resources.list_folder('icons.status')
        )
        ui['placeholder'] = 'The "icon" and "editable" properties change at each Refresh...'
        ui['icon'] = ('icons.status', status)
        ui['editable'] = self.EDITABLE
        self.EDITABLE = not self.EDITABLE


class ExpandedObject(flow.Object):

    message = flow.Label(
        """<h2>Please Don't fold me !</h2>
        <h3>The "expanded" property override the default expanded state, set it to <b>True</b> to expand automatically 
        an Object when it appear for the first time<h3>"""
    )


class NotExpandableObject(flow.Object):

    message = flow.Label(
        """
        <h2>Thanks for coming but there is nothing to see here :/</h2>
        <h2>Have a nice day !</h2>
        """
    )
    parent = flow.Parent().ui("Go Back")

class HiddenNavBarAction(flow.Action):

    sub_object = flow.Child(flow.Object)

    def allow_context(self, context):
        return 'detail' in context

    def needs_dialog(self):
        return True

    def get_buttons(self):
        self.message.set(
            "<html>"
            "<p>This Action dialog doesn't have a navigation bar.</p>"
            "<p>Sub object may still show it though...</p>"
            "</html>"
        )
        return ['Nice']

    def run(self, button):
        return None

    def _fill_ui(self, ui):
        ui['navigation_bar'] = False

class HiddenNavBar(flow.Object):

    doc = flow.Label(
        """
        <h2>Hidden Navigation Bar</h2>

        <p>
        This page does not show the navigation bar 
        which can be usefull to lighten the GUI in Action dialog
        and custom pages for example...
        </p>
        <p>
        You can use 
        <pre>   Relation.ui(navigation_bar=False)</pre>
        to control it,
        and you can also set it in 
        <pre>   Object._fill_ui()</pre>
        </p>
        <p><font color=cyan>
        You can use the <b>Option</b> menu to 
        <b>toggle</b> the navigation bar back on.
        </p></font>
        """
    )

    parent_page = flow.Parent()

    hidden_nav_bar_action = flow.Child(HiddenNavBarAction)

class UIConfigGroup(flow.Object):

    doc = flow.Label(
        '''
        <hr><h2>There are a few options to configure the look and
        interface for your Objects.</h2>
        '''
    )

    icon_doc = flow.Label(
        '''
        <hr><h3>The <b>ICON</b> class attribute will associate an icon with your
        Object or Action class. This icon will appear in most place in the GUI
        where your Object appears.</h2>
        '''
    )
    object_with_icon = flow.Child(ResourceIconObject)

    relation_doc = flow.Label(
        '''
        <hr><h3>When defining a relation to another object, you can specify 
        some ui options</h3>
        Those are:
        <pre>
            icon, editor_type, editable, label, hidden
        </pre>
        The icon will override the one defined in the Object class:<br>
        <pre>
            object_with_icon = flow.Child(MyObject).ui(another)
        </pre>
        Note that you can chain the call to Relation.ui():
        <pre>
            my_object = flow.Child(MyObject).ui(
                icon=my_icon
            ).ui(
                label='This Label Is Overriden'
            )
                
        </pre>
        </h3>
        '''
    )
    object_with_overridden_icon = flow.Child(ResourceIconObject).ui(
        icon=('icons.status', 'WIP')
    )

    fill_doc = flow.Label(
        '''
        <hr><h3>
        Sometime you need to have an icon or other ui properties changing
        over time or per instance.
        </h3>
        To achieve this, you can override the `Object._fill_ui(ui)` method
        and alter the default ui passed to it.<br>
        The ui argument is a dict containing all ui properties set on the 
        relation. Just change a value to after the ui (Beware: changes will only
        show after a GUI refresh or navigation !). 
        '''
    )
    altered_icon = flow.Param('', AlteredIconValue)

    map_doc = flow.Label(
        '''
        <hr><h3>The Map items can be styles with icons and colors. There are many 
        option, please refer to the docstring of `DynamicMap.rows()` method.</h3>
        (refresh to see new random colors/icons)
        '''
    )
    map_example = flow.Child(MapExample)

    expanded_example = flow.Child(ExpandedObject).ui(expanded=True)

    expandable_doc = flow.Label(
        "<hr><h3>You can set the `expandable` property to forbid the expanding of an Object, "
        "forcing the user to display it in a new page (by double clicking)</h3>"
    )
    not_expandable = flow.Child(NotExpandableObject).ui(expandable=False)

    hidden_nav_bar = flow.Child(HiddenNavBar).ui(
        navigation_bar=False,
        expandable=False,
    )
