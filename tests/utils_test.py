import pytest
import time

from pydomotic.utils import (cache_value, _camel_to_snake, ObjectMetaclass,
        import_method)

import testdata.custom_code

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

def test_cache_value_fallback():
    def test_fn(fails_on):
        call_count = [0]

        @cache_value(fallback_on_error=True)
        def _test_fn():
            call_count[0] += 1
            if call_count[0] in fails_on:
                1 / 0
            return call_count[0]
        return _test_fn

    # first call succeeds, second fails, third succeeds
    fn = test_fn([2])
    assert fn() == 1, 'wrong value returned'
    assert fn() == 1, 'wrong value returned'
    assert fn() == 3, 'wrong value returned'

    # first call fails, second succeeds, third fails
    fn = test_fn([1, 3])
    with pytest.raises(ZeroDivisionError):
        fn()
    assert fn() == 2, 'wrong value returned'
    assert fn() == 2, 'wrong value returned'

    # first call fails, second fails, third succeeds
    fn = test_fn([1, 2])
    with pytest.raises(ZeroDivisionError):
        fn()
    with pytest.raises(ZeroDivisionError):
        fn()
    assert fn() == 3, 'wrong value returned'

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

def test_import_method():
    expect = testdata.custom_code.custom_function
    actual = import_method('testdata.custom_code.custom_function')
    assert expect == actual, 'wrong method returned'
