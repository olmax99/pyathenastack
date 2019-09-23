from utilities.hooks import LocalHook
from utilities.hooks import HttpHook
from utilities.hooks import S3Hook
from utilities.hooks import CfnHook


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
    def create(type_hook='local'):
        assert type_hook is not None and isinstance(type_hook, str)
        if type_hook == 'local':
            return LocalHook()
        elif type_hook == 'http':
            return HttpHook()
        elif type_hook == 's3':
            return S3Hook()
        elif type_hook == 'cfn':
            return CfnHook()
        else:
            raise HookTypeException(f"'{type_hook}' is not a valid source type.")
