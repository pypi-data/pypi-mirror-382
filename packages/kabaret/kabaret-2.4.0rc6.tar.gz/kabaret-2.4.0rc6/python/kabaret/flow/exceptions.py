"""
    kabaret.flow.exceptions:
    all the exception raised by flow objects.
"""


class WIPException(Exception):
    '''
    Use while code update is in progress
    '''


class MissingRelationError(KeyError):

    def __init__(self, oid, relation_name):
        super(MissingRelationError, self).__init__("Could not find related object %r under %r" % (relation_name, oid))


class MissingChildError(KeyError):

    def __init__(self, oid, child_name):
        super(MissingChildError, self).__init__("Could not find child %r under %r" % (child_name, oid))
        self.oid = oid
        self.child_name = child_name


class MappedNameError(MissingChildError):

    def __init__(self, oid, mapped_name):
        super(MappedNameError, self).__init__(oid, mapped_name)
        self.message = "No mapped name %r in %r" % (mapped_name, oid)


class RefSourceTypeError(ValueError):
    pass


class RefSourceError(ValueError):

    def __init__(self, ref_oid, source_oid):
        super(RefSourceError, self).__init__("Could not find source %r for ref %r" % (source_oid, ref_oid))
        self.ref_oid = ref_oid
        self.source_oid = source_oid
