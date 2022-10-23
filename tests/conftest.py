import datetime
import pytest
import random

class _MockDevice(object):
    def __init__(self):
        self.turn_on_called = False
        self.turn_off_called = False
    def turn_on(self):
        self.turn_on_called = True
    def turn_off(self):
        self.turn_off_called = True

@pytest.fixture
def mock_device():
    return _MockDevice()

class _MockTrigger(object):
    def __init__(self, returns):
        self.returns = returns
        self.check_called = False
    def check(self):
        self.check_called = True
        return self.returns

@pytest.fixture
def mock_true_trigger():
    return _MockTrigger(True)

@pytest.fixture
def mock_false_trigger():
    return _MockTrigger(False)

class _MockAction(object):
    def __init__(self):
        self.run_called = False
    def run(self):
        self.run_called = True

@pytest.fixture
def mock_action_1():
    return _MockAction()

@pytest.fixture
def mock_action_2():
    return _MockAction()

class _MockProvider(object):
    def __init__(self):
        self.turn_on_called = False
        self.turn_off_called = False
    def turn_on(self):
        self.turn_on_called = True
    def turn_off(self):
        self.turn_off_called = True

@pytest.fixture
def mock_provider():
    return _MockProvider()

class _MockComponent(object):
    def __init__(self, enabled):
        self.enabled = enabled
        self.run_called = False
    def run(self):
        self.run_called = True

@pytest.fixture
def mock_enabled_component():
    return _MockComponent(True)

@pytest.fixture
def mock_disabled_component():
    return _MockComponent(False)

class _MockAQISensor(object):
    def __init__(self):
        self.aqi = 0
        self.get_aqi_called = False
    def get_aqi(self):
        self.get_aqi_called = True
        return self.aqi

@pytest.fixture
def mock_aqi_sensor():
    return _MockAQISensor()

@pytest.fixture
def patch_datetime(monkeypatch):
    def patch(dt):
        class _datetime(datetime.datetime):
            @classmethod
            def now(self):
                return dt
        monkeypatch.setattr(datetime, 'datetime', _datetime)
    return patch

@pytest.fixture
def patch_random(monkeypatch):
    def patch(num):
        def _random():
            return num
        monkeypatch.setattr(random, 'random', _random)
    return patch
