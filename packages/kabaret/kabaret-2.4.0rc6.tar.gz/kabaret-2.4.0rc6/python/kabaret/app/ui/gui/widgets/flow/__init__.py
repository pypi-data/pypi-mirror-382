

from kabaret.app import plugin
from .flow_view import FlowView

class FlowViewPlugin:

    """
    The default Flow view.

    Will only be installed if no other view
    is registered under the "Flow" view type name.
    """

    @plugin(trylast=True)
    def install_views(session):
        if not session.is_gui():
            return

        type_name = FlowView.view_type_name()
        if not session.has_view_type(type_name):
            session.register_view_type(FlowView)
            session.add_view(type_name)
