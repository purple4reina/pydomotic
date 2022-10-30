import pytest
import time

from automaton.utils import cache_value

def test_cache_value(monkeypatch):
    call_count = [0]

    @cache_value(seconds=3600)
    def test_fn():
        call_count[0] += 1
        return call_count[0]

    for _ in range(3):
        actual = test_fn()
        assert actual == 1, 'wrong value returned'

    now = time.time()
    monkeypatch.setattr('time.time', lambda: now + 3601)

    for _ in range(3):
        actual = test_fn()
        assert actual == 2, 'wrong value returned'
