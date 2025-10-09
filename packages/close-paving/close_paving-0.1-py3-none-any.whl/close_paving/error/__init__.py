

from astartool.error import ParameterValueError

class TypeNotAllowedError(ParameterValueError):
    def __init__(self, *args, **kwargs): # real signature unknown
        super().__init__(*args)
