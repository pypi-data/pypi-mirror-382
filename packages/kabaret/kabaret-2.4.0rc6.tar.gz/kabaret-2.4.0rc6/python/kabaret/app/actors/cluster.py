import redis.commands
import six
import redis
import os

from .._actor import Actor, Cmd, Cmds



class ReadWriteRedis:
    '''
    This is a wrapper around two `redis.Redis`
    which redirect commands to one of the two connection
    if it's a read command.
    '''

    _overridden_methods = {'ping', 'set_name'}

    #TODO: probably add more commands !!!
    _read_commands = {
        # redis.commands.core.BasicKeyCommands:
        'bitcount', 'bitfield', 'bitfield_ro', 'bitop', 'bitpos', 
        'dump', 'exists', 'expiretime', 
        'get', 'getbit', 'getrange', 'keys', 
        'mget', 
        'pexpiretime', 'pttl', 'hrandfield', 'randomkey', 
        'strlen', 'substr', 
        'ttl', 'type', 
        #FIXME: do we want to get these from read replicat?:  watch, unwatch,
        'lcs',
        # redis.commands.core.HyperlogCommands
        # redis.commands.core.HashCommands
        'hexists', 'hget', 'hgetall', 'hkeys', 'hlen', 'hmget', 'hvals', 'hstrlen',
        # redis.commands.core.GeoCommands
        # redis.commands.core.ListCommands
        'lindex', 'llen', 'lrange', 
        # redis.commands.core.ScanCommands
        # redis.commands.core.SetCommands
        'scard', 'sdiff', 'sinter', 'sintercard', 'sismember', 'smembers', 'smismember', 'srandmember', 'sunion', 
        # redis.commands.core.StreamCommands
        # redis.commands.core.SortedSetCommands
        'zcard', 'zcount', 'zdiff', 'zinter', 'zintercard', 'zlexcount', 'zrandmember', 
        'zrange', 'zrevrange', 'zrangebylex', 'zrevrangebylex', 'zrangebyscore', 'zrevrangebyscore', 
        'zrank', 'zrevrank', 'zscore', 'zunion', 'zmscore', 
    }
    def __init__(self, logger, read_db: redis.Redis, db: redis.Redis):
        super().__init__()
        self._logger = logger
        self._read_db = read_db
        self._db = db

    def __getitem__(self, name):
        self._logger(f'Using read replica for `get` command.')
        return self._read_db.__getitem__(name)
    
    def __setitem__(self, name, value):
        self._logger(f'Using master DB for `set` command.')
        self._db[name] = value

    def __delitem__(self, name):
        self._logger(f'Using master DB for `del` command.')
        return self._db.__delitem__(name)
    
    def __getattribute__(self, name: str):
        if name.startswith('_') or name in self._overridden_methods:
            return super().__getattribute__(name)
        
        if name in self._read_commands:
            self._logger(f'Using read replica for {name!r} command.')
            return getattr(self._read_db, name)
        self._logger(f'Using master DB for {name!r} command.')
        return getattr(self._db, name)
    
    def ping(self, **kwargs):
        self._logger('Pinging both db.')
        self._read_db.ping(**kwargs)
        self._db.ping(**kwargs)

    def client_setname(self, name, **kwargs):
        self._logger('Setting name on both db.')
        self._read_db.client_setname(name, **kwargs)
        self._db.client_setname(name, **kwargs)

class ClusterCmds(Cmds):

    pass


@ClusterCmds.cmd
class Connect(Cmd):

    def _decode(self, host, port, cluster_name, db_index, password=None, read_replica_host=None, read_replica_port=None):
        self.host = host
        self.port = port
        self.cluster_name = cluster_name
        self.db_index = db_index
        self.password = password
        self.read_replica_host = read_replica_host
        self.read_replica_port = read_replica_port

    def _execute(self):
        actor = self.actor()
        actor.log(
            "Connecting to %s port:%r, index:%r" % (self.host, self.port, self.db_index)
        )

        actor.host = self.host
        actor.port = self.port
        actor.db_index = self.db_index
        actor.password = self.password
        actor.read_replica_host = self.read_replica_host
        actor.read_replica_port = self.read_replica_port

        # We add those to environment so that subprocesses' session can use connect_from_env():
        os.environ.update(
            dict(
                KABARET_HOST=self.host,
                KABARET_PORT=self.port,
                KABARET_CLUSTER_NAME=self.cluster_name,
                KABARET_DB=self.db_index,
                KABARET_PASS=self.password or "",
                KABARET_READ_REPLICA_HOST=self.read_replica_host or "",
                KABARET_READ_REPLICA_PORT=self.read_replica_port or "",
            )
        )

        import redis.cluster, redis.sentinel

        # NOTE: decode_responses is needed with python 3 who wont accept bytes as string.

        db = redis.StrictRedis(
            host=self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
        )
        if self.read_replica_host is not None:
            actor.log(
                "Using replica to %s port:%r, index:%r" % (self.read_replica_host, self.read_replica_port, self.db_index)
            )

            read_db = redis.StrictRedis(
                host=self.read_replica_host,
                port=self.read_replica_port,
                password=self.password,
                decode_responses=True,
            )
            db = ReadWriteRedis(actor._session.log_debug, read_db, db)

        actor.set_db(
            db,
            self.cluster_name,
        )


@ClusterCmds.cmd
class Connect_From_Env(Cmd):
    """
    Will connect using the env var values.
    """

    def _decode(self):
        pass

    def _execute(self):
        actor = self.actor()
        actor.log("Connecting From Env...")
        try:
            host = os.environ["KABARET_HOST"]
            port = os.environ["KABARET_PORT"]
            cluster_name = os.environ["KABARET_CLUSTER_NAME"]
            db_index = os.environ["KABARET_DB"]
            password = os.environ.get("KABARET_PASS", None) or None
            read_replica_host = os.environ.get('KABARET_READ_REPLICA_HOST') or None
            read_replica_port = os.environ.get('KABARET_READ_REPLICA_PORT') or None
        except (KeyError, ValueError) as err:
            raise Exception(
                "Could not auto_connect the session (env value error): %s" % (err,)
            )
        else:
            actor.log(
                " => Env Connection: %s port:%r, index:%r" % (host, port, db_index)
            )

        actor.host = host
        actor.port = port
        actor.db_index = db_index
        actor.password = password
        actor.read_replica_host = read_replica_host
        actor.read_replica_port = read_replica_port

        # NOTE: decode_responses is needed with python 3 who wont accept bytes as string.
        db = redis.StrictRedis(
                host,
                port,
                db_index,
                password,
                decode_responses=True,
            )

        # This code is repeated from the Connect command :/
        # and it will be a problem on day.:
        if read_replica_host is not None:
            actor.log(
                " => Using replica to %s port:%r, index:%r" % (read_replica_host, read_replica_port, db_index)
            )

            read_db = redis.StrictRedis(
                read_replica_host,
                read_replica_port,
                db_index,
                password,
                decode_responses=True
            )
            db = ReadWriteRedis(actor._session.log_debug, read_db, db)
        
        actor.set_db(
            db, 
            cluster_name,
        )


@ClusterCmds.cmd
class Get_Connection_Info(Cmd):

    def _decode(self):
        pass

    def _execute(self):
        return self.actor().get_connection_info()


@ClusterCmds.cmd
class Disconnect(Cmd):

    def _decode(self):
        pass

    def _execute(self):
        self.actor().log("Disconnecting")


@ClusterCmds.cmd
class Broadcast(Cmd):

    def _decode(self, *words):
        self.words = words

    def _execute(self):
        self.actor().broadcast(*self.words)


@ClusterCmds.cmd
class Publish(Cmd):

    def _decode(self, **channels_messages):
        self.channels_messages = channels_messages

    def _execute(self):
        self.actor().publish(**self.channels_messages)


@ClusterCmds.cmd
class Get_Cluster_Name(Cmd):

    def _decode(self):
        pass

    def _execute(self):
        return self.actor().get_cluster_name()


class Cluster(Actor):

    def __init__(self, session):
        super(Cluster, self).__init__(session)

        self.KABARET_DB_INDEX = 3
        self.db = None
        self.pubsub = None

        self.host = None
        self.port = None
        self.db_index = None
        self.password = None
        self.cluster_name = None
        self.read_replica_host = None
        self.read_replica_port = None

        self._pubsubs = []

    def get_connection_info(self):
        """
        Returns the info used to connect.
        """
        return self.host, self.port, self.cluster_name, self.db_index

    def _create_cmds(self):
        return ClusterCmds(self)

    def _reg_pubsub(self, pubsub):
        self._pubsubs.append(pubsub)

    def _unreg_pubsub(self, pubsub, pattern):
        self._pubsubs.remove(pubsub)
        if pattern:
            pubsub.punsubscribe()
        else:
            pubsub.unsubscribe()

    def _read_pubsub(self):
        """
        Called periodically by the session since self.set_db() called.
        """
        # nb: we copy self._pubsubs so that handlers can unsubscribe
        # their channel (and thus modify self._pubsubs)

        if 0:
            # This was nice but it fetches only one message per pubsub.
            # If there's many messages, it will take many call to consume
            # every message :/
            for pubsub in list(self._pubsubs):
                unhandled_message = pubsub.get_message(
                    timeout=0  # dont wait for messages
                )
                if unhandled_message is not None:
                    self.on_unhandled_message(unhandled_message)

        else:
            # This is better since we consume messages until there's no
            # more.
            # Maybe we should make the maximum configurable ?
            #
            # NB: this code is derived from redis.client.PubSub.get_message()
            # It might be needed to update it if redis.client changes a lot
            # in further versions.
            for pubsub in list(self._pubsubs):
                max_iterations = 20
                curr = 0
                while curr < max_iterations:
                    response = pubsub.parse_response(block=False, timeout=0)
                    if response:
                        unhandled_message = pubsub.handle_message(
                            response, ignore_subscribe_messages=True
                        )
                        if unhandled_message:
                            self.on_unhandled_message(unhandled_message)
                    else:
                        curr = max_iterations

    def channels_subscribe(self, **channels_callbacks):
        """
        Returns a a callable used to unsuscribe all those subscriptions.
        """
        cluster_channels_callbacks = {}
        for ch, cb in channels_callbacks.items():
            channel = "%s:%s" % (self.cluster_name, ch)
            cluster_channels_callbacks[channel] = cb

        pubsub = self.db.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(**cluster_channels_callbacks)
        self._reg_pubsub(pubsub)
        return lambda p=pubsub: self._unreg_pubsub(p, pattern=False)

    def patterns_subscribe(self, **patterns_callbacks):
        """
        Returns a a callable used to unsuscribe all those subscriptions.
        """
        cluster_patterns_callbacks = {}
        for pt, cb in patterns_callbacks.items():
            pattern = "%s:%s" % (self.cluster_name, pt)
            cluster_patterns_callbacks[pattern] = cb

        pubsub = self.db.pubsub(ignore_subscribe_messages=True)
        pubsub.psubscribe(**cluster_patterns_callbacks)
        self._reg_pubsub(pubsub)
        return lambda p=pubsub: self._unreg_pubsub(p, pattern=True)

    def broadcast(self, *words):
        message = " ".join([str(i) for i in words])
        self.publish(broadcast=message)

    def publish(self, **channels_messages):
        for channel, message in six.iteritems(channels_messages):
            cluster_channel = "%s:%s" % (self.cluster_name, channel)
            self.db.publish(cluster_channel, message)

    def on_unhandled_message(self, message):
        self.log("Unhandled Message:", repr(message))

    def on_broadcast_message(self, message):
        # message is a dict w/ pattern, type, channel, data
        self.log("[Broadcast Message]", repr(message["data"]))

        if 0:
            channels = self.db.pubsub_channels()
            self.log(
                "- Channels:",
                ", ".join(
                    ["%s=%i" % (c, i) for c, i in self.db.pubsub_numsub(*channels)]
                ),
            )
            self.log("- Patterns in use:", self.db.pubsub_numpat())

    def get_cluster_name(self):
        return self.cluster_name

    def get_db(self):
        if self.db is None:
            raise Exception("Cannot access the database without connection!")
        return self.db

    def set_db(self, db, cluster_name):
        if self.db is not None:
            raise Exception("The Database is already set !")

        try:
            db.ping()
        except redis.exceptions.ConnectionError as err:
            raise ValueError(
                str(err) + "\n\n" "=> Ask your administrator to check the database."
            )

        self.db = db
        self.db.client_setname(self.session().session_uid())

        self.cluster_name = cluster_name
        self.log("Connected to Cluster %r" % (self.cluster_name,))

        self.session().add_ticked(self._read_pubsub)
        self.session()._on_cluster_connected()

    def on_session_connected(self):
        self.broadcast_unsubscribe = self.channels_subscribe(
            broadcast=self.on_broadcast_message
        )
        self.broadcast("Cluster joined by", self.session().session_uid())

    def die(self):
        self.broadcast("Cluster left by", self.session().session_uid())
        self.broadcast_unsubscribe()
