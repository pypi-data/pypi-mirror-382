


import sys
import logging

def _tornado_import_object(name):
    '''code from tornado.util.import_object'''
    # py2 avoid unicodes:
    name = str(name)

    if name.count('.') == 0:
        return __import__(name, None, None)

    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    try:
        return getattr(obj, parts[-1])
    except AttributeError:
        raise ImportError("No module named %s" % parts[-1])


def import_object(
    object_qualified_name, reload_modules=True, clear_linecache=True
):
    # print('#------#')
    # print('#------# IMPORT OJECT', object_qualified_name)
    # print('#------#')
    if reload_modules:
        module_name = object_qualified_name.split('.', 1)[0]
        if 'KABARET' in module_name.upper():
            logging.getLogger('kabaret.flow').info('\n'.join((
                '[WARNING] CANNOT IMPORT PROJECT TYPE FROM KABARET',
                ' WITH reload_modules OPTION!'
            )))
        else:
            # print('#-----# reload modules', reload_modules, '->', module_name)
            for k in sorted(sys.modules.keys()):
                if k.startswith(module_name):
                    # print('[-]', k)
                    del sys.modules[k]
                else:
                    # print('[ ]', k)
                    pass

    if clear_linecache:
        # this is needed because of a bug in inspect which does not do
        # linecache.checkcache() in getsource()
        # fixed in py3k (I think)
        # It could be skipped for release... I guess. but needed for now
        # to have the flow run the reloaded code in client actions.
        import linecache
        linecache.clearcache()

    return _tornado_import_object(object_qualified_name)

