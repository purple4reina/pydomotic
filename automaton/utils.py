import functools
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
