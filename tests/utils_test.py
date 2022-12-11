import pytest
import time

from automaton.utils import cache_value, _camel_to_snake, ObjectMetaclass

_test_cache_value = (
        {'seconds': 3600},
        {'minutes': 60},
        {'seconds': 1800, 'minutes': 30},
        {'hours': 1},
        {'hours': 0.5, 'minutes': 30},
)

@pytest.mark.parametrize('kwargs', _test_cache_value)
def test_cache_value(kwargs, monkeypatch):
    call_count = [0]

    @cache_value(**kwargs)
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

    test_fn.clear_cache()

    for _ in range(3):
        actual = test_fn()
        assert actual == 3, 'wrong value returned'

_test__camel_to_snake = (
        ('ABCTrigger', 'abc_trigger'),
        ('AbcTrigger', 'abc_trigger'),
        ('_ABCTrigger', '_abc_trigger'),
        ('ABC123Trigger', 'abc123_trigger'),
        ('Abc123Trigger', 'abc123_trigger'),
        ('MyABCTrigger', 'my_abc_trigger'),

        pytest.param('_AbcTrigger', '_abc_trigger',
            marks=pytest.mark.xfail(strict=True)),
)

@pytest.mark.parametrize('name,expect', _test__camel_to_snake)
def test__camel_to_snake(name, expect):
    assert expect == _camel_to_snake(name)

def test_ObjectMetaclass__Nameable():
    class MyClass(metaclass=ObjectMetaclass): pass
    assert MyClass().name == 'my_class', 'wrong name returned'

    class MySubClass(MyClass): pass
    assert MySubClass().name == 'my_sub_class', 'wrong name returned'
