import sys, os
import logging
import platform
import getpass
import re
import traceback
import argparse
import pathlib
import json

import six

from datetime import datetime
from .plugin_manager import PluginManager
from .actors import default_actors_plugin

class SessionCmds(object):

    def __init__(self):
        super(SessionCmds, self).__init__()

class KabaretSession(object):
    '''
    This is the base class for all **kabaret** sessions.

    You can use this class directly for headless sessions,
    or use one of its subclasses (:class:`KabaretStandaloneGUISession`,
    :class:`KabaretEmbeddedGuiSession`, :class:`MayaEmbeddedSession`, ...)

    Each session created is stored in memory. You can get
    the last created one with `KabaretSession.get_session()`.

    Each session has a unique identifier returned by `session_uid()`. 
    You can get a known session with `KabaretSession.get_session(session_uid)`.

    .. note:: The function `kabaret.app.get_session()` is a alias for
        this `kabaret.app.session.KabaretSession.get_session()`.

    The session give access to commands provided by each Actors
    in `session.cmds.<ActorName>`:

    .. code-block:: python

        session.cmds.Cluster.connect(...)
        session.cmds.Flow.ls(...)


    If you want to use non-default Actors, you must subclass and
    override the :meth:`_create_actors`.

    .. note:: The logging api is a mess and will probably change.

    .. automethod:: _create_actors
    .. automethod:: _get_layout_state
    .. automethod:: _set_layout_state

    '''

    _SESSIONS = []

    @staticmethod
    def parse_command_line_args(args):
        '''
        Returns session_name, host, port, cluster_name, database
        number, password, debug mode, read_replica_host, read_replica_port, 
        and remaining arguments found in the given args.

        If -h is found or if parsing fails, a ValueError is raised with
        usage description.

        .. code-block:: python

            if __name__ == '__main__':
                # Parse command line arguments:
                (
                    values.session_name,
                    values.host, values.port, values.cluster_name,
                    values.db, values.password, values.debug,
                    values.read_replica_host, values.read_replica_port,
                    values.layout_mgr, values.layout_autosave, values.layout_savepath,
                    remaining_args
                ) = KabaretSession.parse_command_line_args(argv[1:])

                # Create the session and connect to cluster
                session = SmksGuiSession(session_name=session_name, debug=debug)
                session.cmds.Cluster.connect(
                    host, port, cluster_name, db, password
                )

                # Have fun
                do_something_awesome(session)

        .. note::

            This is subject for deprecation in favor of a more
            versatile system where each Actor handles its command line
            interface.

            If you use this method, be sure to do it so you can
            easily update in the future (DRY principle...)

        '''
        parser = argparse.ArgumentParser(
            description='Kabaret Session Arguments'
        )

        parser.add_argument(
            '-S', '--session', default=os.getenv('KABARET_SESSION', 'kabaret'), dest='session_name', help='Session Name'
        )

        parser.add_argument(
            '-H', '--host', default=os.getenv('KABARET_REDIS_HOST', 'localhost'), help='Cluster Host address'
        )
        parser.add_argument(
            '-P', '--port', default=os.getenv('KABARET_REDIS_PORT', '6379'), help='Cluster Port number'
        )
        parser.add_argument(
            '-C', '--cluster', default=os.getenv('KABARET_REDIS_CLUSTER', 'DEFAULT_CLUSTER'), dest='cluster_name', help='Cluster Name'
        )
        parser.add_argument(
            '-D', '--db', default=os.getenv('KABARET_REDIS_DB', '1'), dest='db', help='Database Index'
        )
        parser.add_argument(
            '-p', '--password', default=os.getenv('KABARET_REDIS_PASSWORD', None), dest='password', help='Database Password'
        )
        parser.add_argument(
            '--read_replica_host', default=os.getenv('KABARET_READ_REPLICA_HOST', None), help='Redis read replica Host address'
        )
        parser.add_argument(
            '--read_replica_port', default=os.getenv('KABARET_READ_REPLICA_PORT', '6378'), help='Redis read replica port number'
        )
        parser.add_argument(
            '-d', '--debug', default=os.getenv('KABARET_DEBUG', False), action='store_const', const=True, dest='debug', help='Debug Mode'
        )

        values, remaining_args = parser.parse_known_args(args)
        #FIXME: this suck bc everytime we add a new args will be a breaking change!
        # maybe returning a dict would be flexible enouth ?
        return (
            values.session_name,
            values.host, values.port, values.cluster_name,
            values.db, values.password, values.debug,
            values.read_replica_host, values.read_replica_port,
            remaining_args
        )

    @classmethod
    def get_session(cls, session_uid=None):
        '''
        Returns one of the sessions. If `session_uid` is None,
        the last created one is returned.

        Returns `None` if `session_uid` is None and no session
        has been created yet.

        Raise `ValueError` if no session exists with the given 
        `session_uid`.

        .. note:: This is also available as `kabaret.app.get_session()`.
        
        '''
        if session_uid is None:
            try:
                return cls._SESSIONS[-1]
            except IndexError:
                return None
        for session in cls._SESSIONS:
            if session.session_uid() == session_uid:
                return session
        raise ValueError(
            "No session with uid '{}' found.".format(
                session_uid
            )
        )

    def __init__(self, session_name=None, debug=False):
        super(KabaretSession, self).__init__()
        self._session_name = session_name or self.__class__.__name__
        
        self.__class__._SESSIONS.append(self)

        self._ticked = []
        self._actors = {}
        self.cmds = SessionCmds()
        self.debug_mode = debug

        # View Management
        self._view_types = {}
        self._views = {}

        self.log_formatter = logging.Formatter("%(name)s -- %(asctime)s -- %(levelname)s: %(message)s")
        self.stream_formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
        self.logger = logging.getLogger('kabaret')
        self.logger.propagate = False
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.default_log_handler = logging.StreamHandler(sys.stdout)
        self.default_log_handler.setFormatter(self.stream_formatter)
        self.logger.addHandler(self.default_log_handler)

        self._plugin_manager = PluginManager(self)
        self.register_plugins(self._plugin_manager)

        self.log_info("Plugins installed:")
        for name, plugin in self._plugin_manager._manager.list_name_plugin():
            self.log_info('    {}'.format(name))
        self._plugin_manager.apply_block_list()

        self._plugin_manager.install_resources(self)
        self._plugin_manager.install_editors(self)

        # This cannot be in self._create_actors() because we used to
        # create the Cluster actor before calling it, which was allowing
        # to override _create_actor() without calling the super() impl.
        # So we install plugin based actor first and then call the previous
        # system:
        self._plugin_manager.install_actors(self)
        self._create_actors()
        
        # The Cluster actor is mandatory, let's ensure one
        # is installed and keep a handle to it:
        try:
            self._cluster_actor = self.get_actor('Cluster')
        except KeyError:
            raise Exception(
                'No "Cluster" Actor installed, please check '
                'your plugins or let the default one install.'
            )

    def register_plugins(self, plugin_manager):
        """
        You can override this to manually register your plugins.

        You will need to call the super implementation unless
        you want to get ride of all the default plugins.
        """
        plugin_manager.register(default_actors_plugin)

    def add_log_file(self, filename, level=logging.INFO, mode="a", format=None, encoding="utf-8"):
        """
        Add a log file which will store all logging messages with level ``level``

        :param filename:
        :param level:
        :param mode: "a" for appending or "w" for cleaning file before writing
        :param encoding:
        :param format: format of the recording message, if None the default formatter is used

        :return: the created handler
        """
        handler = logging.FileHandler(filename, mode, encoding)
        if format:
            formatter = logging.Formatter(format)
        else:
            formatter = self.log_formatter
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        return handler

    def add_log_stream(self, level=logging.INFO, stream=None):
        '''
        Add a log stream for messages with level ``level``

        :param level:
        :param stream:
        :return:
        '''
        handler = logging.StreamHandler(stream)
        if format:
            formatter = logging.Formatter(format)
        else:
            formatter = self.log_formatter
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        return handler

    def is_gui(self):
        '''
        Returns True if this session has a graphical user
        interface.

        :return: bool
        '''
        return False

    def add_ticked(self, callable):
        '''
        Register a callable with no args to be called in the
        :meth:`tick` method.

        Actors can use this to setup *periodic* calls.
        '''
        try:
            self._ticked.remove(callable)
        except ValueError:
            pass
        self._ticked.append(callable)

    def tick(self):
        '''
        Trigger all ticked function (see :meth:`add_ticked`)

        The **Cluster** actor relies on this for event processing.

        GUI sessions should setup a timer to periodically call
        this. Headless sessions should call this at key moments.

        '''
        for ticked in self._ticked:
            try:
                ticked()
            except Exception as err:
                message = '\n'.join((
                    "------------------ TRACE BEGIN ----------------",
                    traceback.format_exc(),
                    "------------------ TRACE END ------------------"
                ))
                self.log_error(
                    'Error while ticking: %s',
                    message
                )

    def _create_actors(self):
        '''
        Instantiates the session actors.

        Subclasses can override this to install customs Actors.

        If you do not want to get ride of the default Actors,
        you should call the base implementation:

        .. code-block:: python

            def _create_actors(self):
                # Ensure default actors are created:
                super(MySession, self)._create_actors()

                # Add custom actors:
                MyAwesomeActor(self)
                SomeDopeExtensionActor(self)


        '''
        pass

    def session_name(self):
        '''
        Returns the session name, typically displayed in GUI.

        :return: string
        '''
        return self._session_name

    def session_uid(self):
        '''
        Returns a unique identifier for this session.

        The value is built using the current user, the session name,
        the session process id and the computer network name.

        :return: string
        '''
        # User name with non-word char and non std ascii replaced by underscores:
        user_slug = re.sub('(\W|[^\x00-\x7f])+', '_', getpass.getuser())
        
        return '%s:%s-%r@%s' % (
            user_slug,
            self._session_name,
            os.getpid(),
            platform.node(),
        )

    def _register_actor(self, actor):
        '''
        This is used upon Actor creation to bind them to the session.

        :param actor: the actor to register
        :return: None
        '''
        actor_name = actor.actor_name
        self.log(
            self._session_name,
            'Registering',
            repr(actor_name), 'Actor from', actor.__module__
        )
        self._actors[actor_name] = actor
        setattr(self.cmds, actor_name, actor.cmds)

    def get_actor_names(self):
        '''
        Returns the name of each Actor in this session.

        :return: list of strings
        '''
        return sorted(self._actors.keys())

    def get_actor(self, actor_name):
        '''
        Returns the actore with name ``actor_name``

        .. warning::

            This is intended for actor dependency, for example
            when a *Schedule* actor needs to access a *Users* actor.

            The right way to *use* actors is by call its commands,
            available in ``session.cmds.<ActorName>.<command_name>()``

            This method is a weakness in the design of kabaret and may
            disappear in the future.

        :param actor_name: name of the Actor to return
        :return: :class:`kabaret.app._actor.Actor` subclass instance.
        '''
        return self._actors[actor_name]

    #
    #       USER SETTINGS
    #
    def user_settings_folder(self):
        # Switch to specific path if argument is used
        if self.layout_savepath:
            if os.path.exists(self.layout_savepath):
                return os.path.join(
                    self.layout_savepath,
                    ".kabaret",
                    self._cluster_actor.get_cluster_name()
                )
            else:
                self.log_warning('Layout save path does not exist. Fallback to default.')
        
        # Use default path
        return os.path.join(
            pathlib.Path.home(),
            ".kabaret",
            self._cluster_actor.get_cluster_name()
        )

    #
    #       VIEW MANAGEMENT
    #
    def register_view_types(self):
        '''
        Register all the view types available in the session.

        Subclasses can override this to install customs Views.
        (This is automatically called by GUI sessions)

        If you do not want to get ride of the default Views,
        you should call the base implementation:

        .. code-block:: python

            def register_view_types(self):
                # Ensure default views are registered/created:
                super(MySession, self).register_view_types()

                # Add custom views:
                type_name = self.register_view_type(MyAwesomeView)
                default_view = self.add_view(type_name)

        '''
        self._plugin_manager.install_views(self)

    def has_view_type(self, view_type_name):
        '''
        Returns True if a ViewType is registered with the
        given view_type_name.
        '''
        return view_type_name in self._view_types
        
    def register_view_type(self, ViewType):
        '''
        Registers a View type so that the session can create
        this kind of View with :meth:`add_view`.

        You should not need to call this outside :meth:`register_view_types`
        (but who am I to judge ;) ).

        :param ViewType: the :class:`kabaret.app.ui.view.View` subclass to register.
        :return: string: the registration name.
        '''
        view_type_name = ViewType.view_type_name()
        self._view_types[view_type_name] = ViewType
        return view_type_name

    def declare_view(self, view):
        '''
        This is called by every View at initialization and should
        not be used for anything else.
        '''
        self._views[view.view_id()] = view

    def forget_view(self, view):
        '''
        This is called by View instances upon destruction and should
        not be used for anything else.
        '''
        self._views.pop(view.view_id())

    def add_view(self, view_type_name, view_id=None, *view_args, **view_kwargs):
        '''
        Adds a view to the session.

        The ``view_type_name`` must have already been registered by a call
        to :meth:`register_view_type`

        The ``view_id`` is optional. If not **None**, the value can be
        used to find a specific view with :meth:`find_view`.

        All extra arguments and keyword arguments are passed to the view
        constructor, notably the ``hidden`` and ``area`` arguments
        available for most GUI Views.

        :param view_type_name: value returned by :meth:`register_view_type`
        :param view_id: optional id to set on the view.
        :param view_args: passed to the view constructor.
        :param view_kwargs: passed to the view constructor.

        :return: the created View.
        '''
        try:
            ViewType = self._view_types[view_type_name]
        except KeyError:
            raise ValueError('Unknown view type %r (known view types are: %r)' %
                             (view_type_name, self._view_types.keys()))

        # The view ID must be unique in our registry.
        # We must fix it before creating the view:
        if view_id in self._views:
            max_attempts = 100
            index = 0
            fixed_view_id = view_id
            try:
                prefix, suffix = view_id.rsplit('_',1)
            except ValueError:
                prefix = view_id
            else:
                try:
                    index = int(suffix)
                except ValueError:
                    prefix = view_id

            while fixed_view_id in self._views:
                index += 1
                if index > max_attempts:
                    raise ValueError(
                        'Cannot create another view with id {}'.format(
                            view_id
                        )
                    )
                fixed_view_id = '{}_{}'.format(view_id, index)
            self.logger.warn(
                'Fixed view_id before creating view: {}->{}'.format(
                    view_id, fixed_view_id
                )
            )
            view_id = fixed_view_id
        view = ViewType(self, view_id, *view_args, **view_kwargs)
        view.ensure_visible()
        return view

    def view_type_count(self, view_type_name):
        '''
        Returns the number of existing views with the given ``view_type_name``

        :param view_type_name: value returned by :meth:`register_view_type`
        :return: int
        '''
        return len([
            v for v in self._views.values()
            if v.view_type_name() == view_type_name
        ])

    def find_view(self, view_type_name=None, view_id=None, create=False, *args, **kwargs):
        '''
        Returns the first view with ``view_type_name`` and/or ``view_id``.

        If ``view_id`` is **None**, any ``view_id`` will match.

        If ``create`` is **True** and no existing view is found,
        a new ``view_type_name`` view in created with ``view_id``,
        ``*args`` and ``**kwargs`` by a call to :meth:`add_view`.

        If no existing view is found and create is **False**, **None** is returned.

        '''
        if view_type_name is not None:
            try:
                self._view_types[view_type_name]
            except KeyError:
                raise ValueError(
                    'Find View: Unknown view type %r' % (
                        view_type_name,
                    )
                )

        for this_view_id, view in self._views.items():
            if view_type_name is not None and view.view_type_name() != view_type_name:
                continue
            if view_id is None or this_view_id == view_id:
                return view

        if create:
            return self.add_view(view_type_name, view_id, *args, **kwargs)

        return None

    def _get_layout_state(self):
        '''
        Subclasses with GUI must override this to return a state valid
        for :meth:`_set_layout_state`.
        (:class:`KabaretStandaloneGUISession` does.)

        :return: a json serializable object describing the current UI state.
        '''
        return None

    def _set_layout_state(self, state):
        '''
        Subclasses with GUI must implement this to restore the GUI
        state described by ``state``.
        (:class:`KabaretStandaloneGUISession` does.)

        The ``state`` argument is the return value of a call to
        :meth:`_get_layout_state`
        '''
        raise NotImplementedError()

    def _get_geometry_state(self):
        '''
        Subclasses with GUI must override this to return a state valid
        for :meth:`_get_geometry_state`.
        (:class:`KabaretStandaloneGUISession` does.)

        :return: a json serializable object describing the current UI geometry state.
        '''
        raise NotImplementedError()
    
    def _set_geometry_state(self, state):
        '''
        Subclasses with GUI must implement this to restore the GUI
        geometry state described by ``state``.
        (:class:`KabaretStandaloneGUISession` does.)

        The ``state`` argument is the return value of a call to
        :meth:`_get_geometry_state`
        '''
        raise NotImplementedError()

    def get_views_state(self, main_geometry=False):
        '''
        Returns the state of all views.

        The return value can be used as argument for
        :meth:`set_views_state` to restore all the views
        to this state.
        '''

        # Get all current views and their statuses
        views = []
        for view_id, view in six.iteritems(self._views):
            view_state = view.get_view_state()
            if view_state is not None:
                views.append((
                    view.view_type_name(), 
                    view.view_id(),
                    view.isHidden(),
                    view.areaPosition().name,
                    json.dumps(bytes(view.saveGeometry().toHex()).decode("ascii")), # ByteArray to unicode
                    view_state
                ))
        
        # Get window layout state
        layout = json.dumps(bytes(self._get_layout_state().toHex()).decode("ascii")) # ByteArray to unicode
        
        state = dict(views=views, layout=layout)
        
        # Get window position (geometry) if attribute is true
        if main_geometry:
            geometry = json.dumps(bytes(self._get_geometry_state().toHex()).decode("ascii")) # ByteArray to unicode
            state["geometry"] = geometry
        
        return state

    def set_views_state(self, state):
        '''
        Restores the views to the state described by ``state``

        The ``state`` value must be one returned by
        :meth:`get_views_state`
        '''
        from qtpy import QtCore

        # For block specific signals (such as autosave)
        self.layout_load = True

        # Clear all current views
        for view in list(self._views.values()):
            view.delete_view()
        self._views.clear()

        # Instantiate views to the state
        views = state.get('views', [])
        view_ids = []
        for view_type_name, view_id, view_hidden, view_area, view_geometry, view_state in views:
            view_ids.append(view_id)
            
            kwargs = {"area": view_area, "hidden": view_hidden}
            if "oid" in view_state:
                kwargs['oid'] = view_state['oid']

            view = self.add_view(view_type_name, view_id, **kwargs)
            view.set_view_state(view_state)

            view_geometry = QtCore.QByteArray.fromHex(bytes(view_geometry, 'ascii')) # Restore to ByteArray format
            view.restoreGeometry(view_geometry)
        
        # Restore main window geometry
        geometry = state.get('geometry')
        if geometry is not None:
            geometry = QtCore.QByteArray.fromHex(bytes(geometry, 'ascii')) # Restore to ByteArray format
            self._set_geometry_state(geometry)
        
        # Restore layout state
        layout = state.get('layout')
        if layout is not None:
            layout = QtCore.QByteArray.fromHex(bytes(layout, 'ascii')) # Restore to ByteArray format
            self._set_layout_state(layout)
        
        self.layout_load = False

    def get_layout_presets(self, autosaves=False):
        # Tmp until we have a User actor to store those things
        layout_folder = os.path.join(self.user_settings_folder(), 'layouts')
        if autosaves:
            layout_folder += '/autosaves'

        # Open and store all json files
        layouts = {}
        if os.path.exists(layout_folder):
            for file_name in os.listdir(layout_folder):
                if os.path.isfile(os.path.join(layout_folder, file_name)) and file_name.endswith('.json'):
                    layout_name = file_name.strip('.json')

                    f = open(os.path.join(layout_folder, file_name), 'r')

                    try:
                        layouts[layout_name] = json.load(f)
                    except ValueError:
                        f.close()
                        os.remove(os.path.join(layout_folder, file_name))

                    f.close()

        return layouts

    def store_layout_preset(self, layout_preset, name=None, autosave=False):
        # Tmp until we have a User actor to store those things
        
        # Set folder path
        layout_folder = os.path.join(self.user_settings_folder(), 'layouts')
        if autosave:
            layout_folder += '/autosaves'
            name = datetime.now().strftime('%Y-%m-%d %H-%M-%S') # Autosave will be named with current date and time
        
        # Create folder if not exists
        if not os.path.exists(layout_folder):
            os.makedirs(layout_folder)
        
        if autosave:
            # Use current session save if one already exists
            if self.layout_sessionpath:
                name, _ = os.path.basename(self.layout_sessionpath).split('.json')
            else:
                self.layout_sessionpath = f'{layout_folder}/{name}.json'

        # Write json file
        with open(f'{layout_folder}/{name}.json', 'w') as f:
            json.dump(layout_preset, f)

        if autosave:
            # Get all saves to keep only the last five sessions
            list_of_saves = [
                os.path.join(layout_folder, save_name)
                for save_name in os.listdir(layout_folder)
            ]

            if len(list_of_saves) >= 6:
                oldest_save = min(list_of_saves, key=os.path.getctime)
                os.remove(os.path.abspath(oldest_save))

    def delete_layout_preset(self, names):
        # Tmp until we have a User actor to store those things

        # Set folder path
        layout_folder = os.path.join(self.user_settings_folder(), 'layouts')
        
        if os.path.exists(layout_folder):
            for file_name in names:
                os.remove(os.path.join(layout_folder, f'{file_name}.json'))

    #
    #       LOGGING
    #
    def log(self, context, *words):
        self._log(logging.INFO, ' '.join([str(i) for i in words]), extra={'context': context})

    def log_info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def log_debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def log_error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def log_warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def log_critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)

    def _log(self, level, message, *args, **kwargs):
        extra = {'user': self.session_uid().split(':')[0]}
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])
            kwargs.pop('extra')
        self.logger.log(level, message, *args, extra=extra, **kwargs)

    def close(self):
        '''
        Kills all actors by calling their ``die()`` method

        '''
        for actor in self._actors.values():
            actor.die()

    def _on_cluster_connected(self):
        '''
        Called by the Cluster actor when the connection is
        first established.

        This method will notify all actors by calling their
        :meth:`on_session_connected` method.

        You should not need to call nor to override this.
        '''
        for actor in self._actors.values():
            actor.on_session_connected()

    def channels_subscribe(self, **channels_callbacks):
        '''
        Register some handlers for the given channels.

        Views use this to subscribe to events emitted by actors
        (from this session or any session in the cluster)

        The handlers will be called with one arg: ``message``.

        The message is a dict like:

        .. code-block:: python

            {
                'channel': channel_name',
                'type': subscription_type  # 'subscribe' or 'psubscribe'
                'data': message_data,

            }

        Beware that if a string was sent as data, message_data will be the 
        byte encoded string. You need to decode it with:
        ``message_data.decode('utf8')``

        Returns a callable without argument that will unregister those handlers
        when called.

        '''
        # WARNING: should'nt we use cmds only on actors ?!?
        # -> No, this it not to be used by the client code (cli, ui, gui...),
        # Only the Actors can subscibe callbacks (server side code), so there
        # is no cmd for that.
        return self._cluster_actor.channels_subscribe(**channels_callbacks)

    def broadcast(self, *words):
        '''
        Broadcasts a messages to all session in the cluster.

        :param words: the words of the message.
        '''
        # FIXME: Clarify if this should use the Cluster cmd or not. If clients
        # (cli, gui, ...) have a need for the command, etc...
        self._cluster_actor.broadcast(*words)

    def publish(self, **channels_messages):
        '''
        Published messages to channels

        :param channels_messages: a map of ``{channel:message}``

        '''
        # FIXME: Clarify if this should use the Cluster cmd or not. If clients
        # (cli, gui, ...) have a need for the command, etc...
        self._cluster_actor.publish(**channels_messages)

    def dispatch_event(self, event_type, **data):
        '''
        Sends an event to all views.

        Every view will receive the event in their
        :meth:`receive_event` method.

        :param event_type: the type of the event
        :param data: the data payload of the event
        '''
        for view_id, view in six.iteritems(self._views):
            view.receive_event(event_type, data)

