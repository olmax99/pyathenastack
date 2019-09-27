from utilities.hooks import (LocalHook, HttpHook, S3Hook, CfnHook, GlueHook)


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
    def create(type_hook='local', chunk_size=200):
        assert type_hook is not None and isinstance(type_hook, str)
        if type_hook == 'local':
            return LocalHook(chunk_size=chunk_size)
        elif type_hook == 'http':
            return HttpHook(chunk_size=chunk_size)
        elif type_hook == 's3':
            return S3Hook()
        elif type_hook == 'cfn':
            return CfnHook()
        elif type_hook == 'glue':
            return GlueHook()
        else:
            raise HookTypeException(f"'{type_hook}' is not a valid source type.")
