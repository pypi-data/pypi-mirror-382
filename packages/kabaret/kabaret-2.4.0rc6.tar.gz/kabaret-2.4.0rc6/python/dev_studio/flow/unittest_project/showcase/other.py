from kabaret import flow


class OtherFeaturesGroup(flow.Object):

    override_home_oid = flow.Label(
'''
<h3>Override Home oid</h3>
You can override the object to show as the "Home".
This can be usefull when your session only has one project, 
if you want to programmatically decide/restrict which project to show from the current user, or 
if you just want to use a custom "landing" flow with actions to navigate to other projects.

<pre>session.cmds.Flow.set_home_oid('/MyLandingPage')</pre>

Note that the real "Home" page will not be accessible anymore using standart GUI.
Also note that your flows can use this command and dynamically change the oid to use 
(set it to None to revert to default behavior).
''' 
)

    custom_flow_object = flow.Label(
'''
<h3>Custom Home Object</h3>
The default Home page is used to create and access projects. It's not the sexiest
because it's really generic. If you want to provide a better experience, you can
define a custom home flow for that.<br>
<br>
(This is what <i>kabaret.flow_button_pages</i>  uses to give you a nicer Home page
with big project buttons instead of the default projects Map, get it at
https://pypi.org/project/kabaret.flow-button-pages )

<pre>
# Import stuff you will need:
from kabaret.app.ui.gui.standalone import KabaretStandaloneGUISession
from kabaret.app.actors.flow import Flow
from kabaret.app.actors.flow.generic_home_flow import AbstractHomeRoot

# Define the flow to use as Home:
class MyHomeFlow(flow.Object):
    [blah...]
    [blah...]
    [blah...]

# Define a new HomeRoot using your home flow:
class MyHomeRoot(AbstractHomeRoot):
    Home = flow.Child(MyHomeFlow)  # ! it MUST be named "Home"

# In your session, override the Flow actor with one using your root:
class MySession(KabaretStandaloneGUISession):

    def _create_actors(self):
        # dont call the base class here since you're
        # defining the Flow yourself.
        Flow(self, MyHomeRoot)
<pre>
'''
)