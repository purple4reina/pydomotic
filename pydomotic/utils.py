import abc
import functools
import importlib
import logging
import re
import time

from .exceptions import PyDomoticMethodImportError

logger = logging.getLogger(__name__)

class _timed_cache(object):

    def __init__(self):
        self.reset()

    def set(self, last_call, value):
        self.last_call = last_call
        self.value = value

    def reset(self):
        self.last_call = 0
        self.value = None

def cache_value(hours=0, minutes=0, seconds=0, fallback_on_error=False):
    # XXX: cache stored per class rather than per instance
    seconds += 60 * 60 * hours + 60 * minutes
    cache = _timed_cache()
    def _rate_limit(fn):
        @functools.wraps(fn)
        def _call(*args, **kwargs):
            now = time.time()
            if now - cache.last_call < seconds:
                return cache.value
            try:
                cache.set(now, fn(*args, **kwargs))
            except Exception as e:
                if not fallback_on_error or cache.last_call == 0:
                    raise e
                logger.info(f'falling back to cached value: [{e.__class__.__name__}] {e}')
            return cache.value
        _call.clear_cache = cache.reset
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

def import_method(import_path):
    names = import_path.rsplit('.', 1)
    if len(names) == 1:
        raise PyDomoticMethodImportError(
                f'import path must include module and method name')
    package_name, method_name = names
    try:
        package = importlib.import_module(package_name)
        return getattr(package, method_name)
    except Exception as e:
        raise PyDomoticMethodImportError(
                f'unable to import code "{import_path}": '
                f'[{e.__class__.__name__}] {e}')
