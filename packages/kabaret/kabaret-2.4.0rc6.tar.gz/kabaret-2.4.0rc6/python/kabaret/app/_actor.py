



class Cmd(object):

    @classmethod
    def cmd_name(cls):
        return cls.__name__.lower()

    def __init__(self, cmds):
        super(Cmd, self).__init__()
        self._cmds = cmds

    def actor(self):
        return self._cmds.actor()

    def __call__(self, *args, **kwargs):
        self._decode(*args, **kwargs)
        return self._execute()

    def _decode(self, *args, **kwargs):
        raise NotImplementedError('This is the abstract Cmd. It cannot be called.')

    def _execute(self):
        raise NotImplementedError('This is the abstract Cmd. It cannot be executed.')


class GetCmd(object):

    def __init__(self, CMD_TYPE):
        self.CMD_TYPE = CMD_TYPE

    def __get__(self, cmds, objtype=None):
        return self.CMD_TYPE(cmds)


class Cmds(object):

    @classmethod
    def cmd(cls, cmd_type):
        setattr(cls, cmd_type.cmd_name(), GetCmd(cmd_type))
        return cmd_type

    def __init__(self, actor):
        super(Cmds, self).__init__()
        self._actor = actor

    def actor(self):
        return self._actor


class Actor(object):

    def __init__(self, session):
        super(Actor, self).__init__()
        self.actor_name = self.__class__.__name__
        
        self.cmds = self._create_cmds()
        self.views = []

        self._session = session
        self._session._register_actor(self)

    def _create_cmds(self):
        '''
        Instanciate and return an appropriate Cmds subclass.
        '''
        raise NotImplementedError()

    def _load_views(self):
        '''
        This is called when the session has a GUI.
        Must make all the actor view types available in self._views
        '''
        pass

    def session(self):
        return self._session

    def log(self, *words):
        self._session.log(self.actor_name, *words)

    def on_session_connected(self):
        '''
        Subclasses may implement this to react to session connection.
        (f.e. subscribe to some channels)
        '''
        pass

    def die(self):
        pass