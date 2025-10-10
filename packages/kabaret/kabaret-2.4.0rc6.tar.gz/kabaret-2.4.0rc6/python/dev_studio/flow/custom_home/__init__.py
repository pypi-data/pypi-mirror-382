

from kabaret import flow
from kabaret.app.actors.flow.generic_home_flow import AbstractHomeRoot


class Home(flow.Object):

    congrat = flow.Param('You made your own Home !').ui(editable=False)


class MyHomeRoot(AbstractHomeRoot):
    '''
    '''

    Home = flow.Child(Home)

    def set_flow_actor(self, flow_actor):
        self.flow_actor = flow_actor
