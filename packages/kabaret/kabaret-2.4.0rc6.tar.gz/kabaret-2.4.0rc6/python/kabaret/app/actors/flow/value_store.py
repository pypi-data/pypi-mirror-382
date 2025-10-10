from __future__ import print_function

import six
import json

from kabaret import flow


class RedisValueStore(flow.AbstractValueStore):

    def __init__(self, redis_db, cluster_name, project_name):
        super(RedisValueStore, self).__init__()
        import redis
        self._redis_version = [int(i) for i in redis.__version__.split('.')]
        self._db = redis_db
        self._cluster_name = cluster_name
        self._project_name = project_name
        self._namespace = ':'.join((
            self._cluster_name, 'Flow', self._project_name
        ))

    def _key(self, key):
        return '%s:%s' % (self._namespace, key)

    def _d(self, value):
        return json.dumps(value)

    def _l(self, string):
        try:
            return json.loads(string)
        except ValueError as err:
            raise KeyError(str(err))

    def get(self, key):
        return self._l(self._db[self._key(key)])

    def set(self, key, value):
        self._db[self._key(key)] = self._d(value)

    def delete(self, key):
        try:
            del self._db[self._key(key)]
        except KeyError:
            return

    def incr(self, key, by):
        self._db.incr(self._key(key), by)

    def decr(self, key, by):
        self.incr(key, -by)

    #--- Ordererd Sting Set

    def oss_get(self, key):
        return self.oss_get_range(key, 0, -1)

    def oss_get_range(self, key, first, last):
        return self._db.zrange(self._key(key), first, last)

    def oss_has(self, key, member):
        return self._db.zscore(self._key(key), member) is not None

    def oss_add(self, key, member, score):
        self.oss_set_score(key, member, score)

    def oss_remove(self, key, member):
        return self._db.zrem(self._key(key), member)

    def oss_len(self, key):
        return self._db.zcard(self._key(key))

    def oss_get_score(self, key, member):
        return self._db.zscore(self._key(key))

    def oss_set_score(self, key, member, score):
        if self._redis_version[0] < 3:
            self._db.zadd(self._key(key), **{member: score})
        else:
            self._db.zadd(
                self._key(key),
                mapping={member:score}
            )

    #--- HASH

    def hash_get_key(self, key, hash_key):
        # hget
        to_load = self._db.hget(self._key(key), hash_key)
        if to_load is None:
            raise KeyError(
                "{} Could not find key '{}' in hash '{}'".format(
                    self.__class__.__name__, hash_key, key
                )
            )
        return self._l(to_load)

    def hash_has_key(self, key, hash_key):
        # hexists
        return self._db.hexists(self._key(key), hash_key)
        # try:
        #     return hash_key in self.store[key]
        # except:
        #     return False

    def del_hash_key(self, key, hash_key):
        # hdel
        self._db.hdel(self._key(key), hash_key)

    def get_hash(self, key):
        # not the same as get_hash_as_dict bc it keep order
        keys = self.get_hash_keys(key)
        return [
            (k, self.hash_get_key(key, k))
            for k in keys
        ]

    def get_hash_as_dict(self, key):
        # hgetall
        d = self._db.hgetall(self._key(key))
        d = dict([
            (k, self._l(v))
            for k, v in six.iteritems(d)

        ])
        return d

    def get_hash_keys(self, key):
        # hkeys
        return self._db.hkeys(self._key(key))
        # try:
        #     return self.store[key].keys()
        # except:
        #     return []

    def get_hash_len(self, key):
        # hlen
        return self._db.hlen(self._key(key))
        # try:
        #     return len(self.store[key])
        # except KeyError:
        #     return 0

    def update_hash(self, key, mapping):
        # hmset
        mapping = [
            (k, self._d(v))
            for k, v in six.iteritems(mapping)
        ]
        self._db.hmset(self._key(key), mapping)

    def set_hash(self, key, mapping):
        k = self._key(key)
        self._db.delete(k)
        if mapping:
            # mapping can be a 2d list or a dict:
            if isinstance(mapping, dict):
                mapping = mapping.items()
            mapping = [
                (mk, self._d(v))
                for mk, v in mapping]
            # looks like redis dont want to set {} as mapping...
            self._db.hmset(k, mapping)

    def set_hash_key(self, key, hash_key, value):
        # hset
        return self._db.hset(
            self._key(key), hash_key, self._d(value)
        )
