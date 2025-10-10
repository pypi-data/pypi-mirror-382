'''

    kabaret.flow.value_store

    Define the AbstractValueStore class (base for all value stores) and
    the MemoryValueStore class.

    A ValueStore is needed by Value instances to store and restore their state.

'''
import logging
import pprint
import six
from collections import OrderedDict


class AbstractValueStore(object):

    def __init__(self):
        super(AbstractValueStore, self).__init__()

    def log(self):
        logging.getLogger('kabaret.flow').info(pprint.pformat(self))

    def get(self, key):
        '''
        Must raise KeyError if not value exists for this key.
        '''
        raise NotImplementedError()

    def set(self, key, value):
        raise NotImplementedError()

    def delete(self, key):
        raise NotImplementedError()

    def incr(self, key, by=1):
        raise NotImplementedError(self)

    def decr(self, key, by=1):
        raise NotImplementedError()

    #--- Ordered String Set

    def oss_get(self, key):
        raise NotImplementedError()

    def oss_get_range(self, key, first, last):
        raise NotImplementedError()

    def oss_has(self, key, member):
        raise NotImplementedError()

    def oss_add(self, key, member, score):
        raise NotImplementedError()

    def oss_remove(self, key, member):
        raise NotImplementedError()

    def oss_len(self, key):
        raise NotImplementedError()

    def oss_get_score(self, key, member):
        raise NotImplementedError()

    def oss_set_score(self, key, member, score):
        raise NotImplementedError()

    #--- Hash

    def hash_get_key(self, key, hash_key):
        # hget
        raise NotImplementedError()

    def hash_has_key(self, key, hash_key):
        # hexists
        raise NotImplementedError()

    def del_hash_key(self, key, hash_key):
        # hdel
        raise NotImplementedError()

    def get_hash(self, key):
        # not the same as get_hash_as_dict bc it keep order
        raise NotImplementedError()

    def get_hash_as_dict(self, key):
        # hgetall
        raise NotImplementedError()

    def get_hash_keys(self, key):
        # hkeys
        raise NotImplementedError()

    def get_hash_len(self, key):
        # hlen
        raise NotImplementedError()

    def update_hash(self, key, mapping):
        # hmset
        raise NotImplementedError()

    def set_hash(self, key, mapping):
        raise NotImplementedError()

    def set_hash_key(self, key, hash_key, value):
        # hset
        raise NotImplementedError()


class MemoryValueStore(AbstractValueStore):

    def __init__(self):
        super(MemoryValueStore, self).__init__()
        self.store = {}

    def save_to(self, filename):
        with open(filename, 'w') as fh:
            fh.write('DATA = ' + pprint.pformat(self.store))
        logging.getLogger('kabaret.flow').info('MemoryValueStore saved to ' + filename)

    def load(self, filename):
        namespace = {}
        execfile(filename, namespace, namespace)
        data = namespace['DATA']
        self.store = data
        logging.getLogger('kabaret.flow').info('MemoryValueStore Loaded ' + filename)

    def log(self):
        logging.getLogger('kabaret.flow').info(pprint.pformat(self))

    def get(self, key):
        return self.store[key]

    def set(self, key, value):
        self.store[key] = value

    def delete(self, key):
        try:
            del self.store[key]
        except KeyError:
            return

    # deprecated, one must use hash
    # def update(self, key, **new_values):
    #     try:
    #         self.store[key]
    #     except KeyError:
    #         self.set(new_values)
    #     else:
    #         self.store[key].update(new_values)

    def incr(self, key, by):
        try:
            old_value = self.store[key]
        except KeyError:
            self.set(by)
        else:
            self.store[key] = old_value + by

    def decr(self, key, by):
        self.incr(-by)

    #--- Oredered String Set
    # stored as a very unefficient {string:score} 
    def oss_get(self, key):
        try:
            d = self.store[key]
        except KeyError:
            return []
        return [
            s
            for s, m in sorted(six.iteritems(d))
        ]

    def oss_get_range(self, key, first, last):
        return self.oss_get(key)[first:last]
        
    def oss_has(self, key, member):
        try:
            return member in self.store[key]
        except KeyError:
            return False

    def oss_add(self, key, member, score):
        self.oss_set_score(key, member, score)

    def oss_remove(self, key, member):
        try:
            d = self.store[key]
        except KeyError:
            d = {}
            self.store[key] = d
        del d[member]

    def oss_len(self, key):
        try:
            return len(self.store[key])
        except KeyError:
            return 0

    def oss_get_score(self, key, member):
        try:
            d = self.store[key]
        except KeyError:
            return None
        return d[member]

    def oss_set_score(self, key, member, score):
        try:
            d = self.store[key]
        except KeyError:
            d = {}
            self.store[key] = d
        d[member] = score

    #--- Hash
    # stored as a dict
    def hash_get_key(self, key, hash_key):
        # hget
        return self.store[key][hash_key]

    def hash_has_key(self, key, hash_key):
        # hexists
        try:
            return hash_key in self.store[key]
        except:
            return False

    def del_hash_key(self, key, hash_key):
        # hdel
        del self.store[key][hash_key]

    def get_hash(self, key):
        # not the same as get_hash_as_dict bc it keep order
        return (
            (k, self.hash_get_key(key, k))
            for k in self.get_hash_keys(key)
        )

    def get_hash_as_dict(self, key):
        # hgetall
        return dict(self.store[key])

    def get_hash_keys(self, key):
        # hkeys
        try:
            return self.store[key].keys()
        except:
            return []

    def get_hash_len(self, key):
        # hlen
        try:
            return len(self.store[key])
        except KeyError:
            return 0

    def update_hash(self, key, mapping):
        # hmset
        self.store[key].update(mapping)

    def set_hash(self, key, mapping):
        self.store[key] = OrderedDict(mapping)

    def set_hash_key(self, key, hash_key, value):
        # hset
        h = self.store.get(key, OrderedDict())
        h[hash_key] = value
        self.store[key] = h
