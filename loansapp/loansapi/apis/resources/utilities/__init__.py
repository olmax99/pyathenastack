from loansapi.apis.resources.utilities.hooks import LocalHook
from loansapi.apis.resources.utilities.hooks import HttpHook


class Error(Exception):
    """Base class for exceptions in this module"""
    pass


class HookTypeException(Error):
    """Exception raised for errors in type_hook input"""
    def __init__(self, message, errors=None):
        super(HookTypeException, self).__init__(str(self.__class__.__name__) + ': ' + message)
        self.errors = errors

    def __repr__(self):
        return "HookTypeException"


class HookFactory(object):
    """
    Factory for all available hooks. Default is the LocalHook
    The source is expected to send JSON formatted data only.
    """
    def __repr__(self):
        return "HookFactory"

    @staticmethod
    def create(chunk_size=10, type_hook='local_file'):
        assert type_hook is not None and isinstance(type_hook, str)
        if type_hook == 'local':
            return LocalHook(chunk_size)
        elif type_hook == 'http':
            return HttpHook(chunk_size)
        else:
            raise HookTypeException(f"'{type_hook}' is not a valid source type.")
