import abc
import functools
import re
import time

def cache_value(seconds):
    cached = [0, None]
    def _rate_limit(fn):
        @functools.wraps(fn)
        def _call(*args, **kwargs):
            now = time.time()
            if now - cached[0] < seconds:
                return cached[1]
            cached[:] = now, fn(*args, **kwargs)
            return cached[1]
        def clear_cache():
            cached[:] = [0, None]
        _call.clear_cache = clear_cache
        return _call
    return _rate_limit

_camel_to_snake_re_1 = re.compile('(.)([A-Z][a-z]+)')
_camel_to_snake_re_2 = re.compile('([a-z0-9])([A-Z])')
def _camel_to_snake(name):
    name = _camel_to_snake_re_1.sub(r'\1_\2', name)
    return _camel_to_snake_re_2.sub(r'\1_\2', name).lower()

class _Nameable(object):

    @property
    def name(self):
        if not hasattr(self, '_name'):
            self._name = _camel_to_snake(self.__class__.__name__)
        return self._name

class ObjectMetaclass(abc.ABCMeta):

    extra_bases = (_Nameable,)

    def __new__(cls, clsname, bases, dct):
        return super().__new__(cls, clsname, bases + cls.extra_bases, dct)

    def __call__(cls, *args, **kwargs):
        # acts as __init__ for any objects using this metaclass
        obj = super().__call__(*args, **kwargs)
        obj.required_class_attrs = getattr(cls, 'required_class_attrs', [])
        for attr in obj.required_class_attrs:
            if not hasattr(obj, attr):
                raise TypeError(
                        "Can't instantiate abstract class "
                        f'{cls.__name__} with abstract instance '
                        f'variable {attr}')
        return obj
