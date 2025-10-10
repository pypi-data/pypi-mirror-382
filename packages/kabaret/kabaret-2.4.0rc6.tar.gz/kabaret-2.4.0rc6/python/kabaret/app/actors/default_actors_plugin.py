from kabaret.app import plugin

from .flow import Flow
from .cluster import Cluster

@plugin(trylast=True)
def install_actors(session):
    """
    Installs the default implementations of mandatory Actors (Cluster & Flow)
    if no such Actors are already installed.
    """

    installed_actor_names = session.get_actor_names()

    if "Cluster" not in installed_actor_names:
        # No Cluster Actor installed, install default one:
        Cluster(session)

    if "Flow" not in installed_actor_names:
        # No Flow Actor installed, install default one:
        Flow(session)
        
    
