import datetime
import pytest
import random
import zoneinfo

from automaton.utils import ObjectMetaclass

class _MockDevice(object):
    def __init__(self):
        self.turn_on_called = False
        self.turn_off_called = False
        self.switch_called = False
    def turn_on(self):
        self.turn_on_called = True
    def turn_off(self):
        self.turn_off_called = True
    def switch(self):
        self.switch_called = True

@pytest.fixture
def mock_device():
    return _MockDevice()

class _MockTrigger(metaclass=ObjectMetaclass):
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

class _MockAction(metaclass=ObjectMetaclass):
    def __init__(self, name, raises):
        self.run_called = False
        self._name = name
        self.raises = raises
    def run(self):
        self.run_called = True
        assert not self.raises

@pytest.fixture
def mock_action_1():
    return _MockAction('__mock_action 1', False)

@pytest.fixture
def mock_action_2():
    return _MockAction('__mock_action 2', False)

@pytest.fixture
def mock_raising_action():
    return _MockAction('__mock_action raising', True)

class _MockComponent(object):
    name = '_MockComponent'
    def __init__(self, enabled, failures=None):
        self.enabled = enabled
        self.run_called = 0
        self.failures = failures or [False]
    def run(self):
        self.run_called += 1
        if self.failures.pop(0):
            raise ZeroDivisionError

@pytest.fixture
def mock_enabled_component():
    return _MockComponent(True)

@pytest.fixture
def mock_disabled_component():
    return _MockComponent(False)

@pytest.fixture
def mock_once_failing_component():
    return _MockComponent(True, [True, False, False])

@pytest.fixture
def mock_thrice_failing_component():
    return _MockComponent(True, [True, True, True])

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

class _MockTimeSensor(object):
    test_datetime = datetime.datetime(1982, 2, 4, 10, 20,
            tzinfo=zoneinfo.ZoneInfo("America/Los_Angeles"))
    tzinfo = test_datetime.tzinfo
    def get_current_datetime(self):
        return self.test_datetime

@pytest.fixture
def mock_time_sensor():
    return _MockTimeSensor()

@pytest.fixture
def patch_random(monkeypatch):
    def patch(num):
        def _random():
            return num
        monkeypatch.setattr(random, 'random', _random)
    return patch

class _MockSunSensor(object):
    def __init__(self):
        self.get_sunrise_called = False
        self.get_sunset_called = False
        self.sunrise = None
        self.sunset = None
    def get_sunrise(self):
        self.get_sunrise_called = True
        return self.sunrise
    def get_sunset(self):
        self.get_sunset_called = True
        return self.sunset

@pytest.fixture
def mock_sun_sensor():
    return _MockSunSensor()

class _MockWeatherSensor(object):
    def __init__(self):
        self.temp = 0
        self.current_temperature_called = False
    def current_temperature(self):
        self.current_temperature_called = True
        return self.temp

@pytest.fixture
def mock_weather_sensor():
    return _MockWeatherSensor()

@pytest.fixture
def patch_get_requests(monkeypatch):
    def patch(raises, resp_json):
        def get(url, params=None):
            return _response()
        class _response(object):
            def raise_for_status(self):
                if raises:
                    raise raises
            def json(self):
                return resp_json
        monkeypatch.setattr('requests.get', get)
    return patch

class _MockSleep(object):
    def __init__(self):
        self.times_slept = 0
    def __call__(self, num):
        self.times_slept += 1

@pytest.fixture
def patched_sleep(monkeypatch):
    sleep = _MockSleep()
    monkeypatch.setattr('time.sleep', sleep)
    return sleep

class _MockGosund(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.access_id = None
        self.access_key = None
        self.provider = None
    def __call__(self, username, password, access_id, access_key):
        self.username = username
        self.password = password
        self.access_id = access_id
        self.access_key = access_key
        self.provider = self._MockGosundProvider(
                username, password, access_id, access_key)
        return self.provider
    class _MockGosundProvider(object):
        def __init__(self, username, password, access_id, access_key):
            self.device = _MockDevice()
        def get_device(self, device_id):
            return self.device

@pytest.fixture
def patch_gosundpy(monkeypatch):
    gosund = _MockGosund()
    monkeypatch.setattr('gosundpy.Gosund', gosund)
    return gosund
