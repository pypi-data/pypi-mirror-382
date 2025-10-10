import os
import pluggy

plugin = pluggy.HookimplMarker("kabaret.plugin")
hookspec = pluggy.HookspecMarker("kabaret.plugin")

class PluginSpec:

    @hookspec
    def install_actors(self, session):
        '''
        Install some Actors in the given session.
        '''

    @hookspec
    def install_views(self, session):
        '''
        Install some views in the given session.
        '''

    @hookspec
    def install_resources(self, session):
        '''
        Install/Activate some resources.
        '''

    @hookspec
    def install_editors(self, session):
        '''
        Install some editor factories.
        '''
    
    @hookspec
    def get_project_types(self, session):
        '''
        Must return a list of `kabaret.flow.Object` 
        subclasses intended to be used as 
        project type.
        '''

    @hookspec
    def get_flow_objects(self, session):
        '''
        Must return a list of `kabaret.flow.Object`
        subclasses intended to be used as
        project building blocks (aka, flow lib).
        '''
        

class PluginManager(object):
    """
    Usage:
    ```
    pm = PluginManager()
    pm.register(some_plugin_function)
    pm.register(some_plugin_module)
    pm.register(PluginClass) 
    pm.register(plugin_class_instance)
    pm.load_plugins() # registers plugins from installed packages

    ```
    """
    BLOCK_LIST_ENV_NAME = 'KABARET_BLOCKED_PLUGINS'

    def __init__(self, session):
        super(PluginManager, self).__init__()
        self.session = session
        self._manager = pluggy.PluginManager("kabaret.plugin")
        self._manager.add_hookspecs(PluginSpec)
        self._manager.load_setuptools_entrypoints(group="kabaret.plugin", name=None)
        self.apply_block_list()
        self._hook = self._manager.hook

    def register(self, plugin, name=None):
        """ Register a plugin and return its canonical name or ``None`` if the name
        is blocked from registering.  Raise a :py:class:`ValueError` if the plugin
        is already registered. """
        return self._manager.register(plugin, name)

    def apply_block_list(self, *names_to_block):
        self.session.log_info(
            'Applying plugin block list ("{}" env var)'.format(
                self.BLOCK_LIST_ENV_NAME,
            )
        )
        from_env = os.environ.get(self.BLOCK_LIST_ENV_NAME, '')
        for name in list(names_to_block)+from_env.split():
            name = name.strip()
            self._manager.set_blocked(name)
            self.session.log_info('Blocking Plugin named "{}"'.format(name))

    def install_actors(self, session):
        self._hook.install_actors(session=session)

    def install_views(self, session):
        self._hook.install_views(session=session)

    def install_resources(self, session):
        self._hook.install_resources(session=session)

    def install_editors(self, session):
        self._hook.install_editors(session=session)


