import datetime
import pytest
import random
import zoneinfo

from pydomotic.providers.airthings import AirthingsAPI
from pydomotic.utils import ObjectMetaclass

class _MockDevice(object):
    name = 'device_name'
    def __init__(self):
        self.turn_on_called = False
        self.turn_off_called = False
        self.switch_called = False
        self.get_temperature_called = False
        self.set_mode_called_args = None
    def turn_on(self):
        self.turn_on_called = True
    def turn_off(self):
        self.turn_off_called = True
    def switch(self):
        self.switch_called = True
    def get_temperature(self):
        self.get_temperature_called = True
        return 42
    def set_mode(self, mode, params):
        self.set_mode_called_args = (mode, params)

@pytest.fixture
def mock_device():
    return _MockDevice()

@pytest.fixture
def mock_devices():
    return _MockDevice(), _MockDevice(), _MockDevice()

@pytest.fixture
def patch_s3(monkeypatch):
    def patch(exception, body):
        class _response(dict):
            def __getitem__(self, key):
                return self
            def read(self):
                return body
        class _MockS3(object):
            def __init__(self, service_name):
                pass
            def get_object(self, Bucket=None, Key=None):
                if exception:
                    raise exception
                return _response()
        monkeypatch.setattr('boto3.client', _MockS3)
    return patch

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

class _MockRadonSensor(object):
    def __init__(self):
        self.radon = 0
        self.get_radon_called = False
    def current_radon(self):
        self.get_radon_called = True
        return self.radon

@pytest.fixture
def mock_radon_sensor():
    return _MockRadonSensor()

class _MockTimeSensor(object):
    test_datetime = None
    def get_current_datetime(self):
        return self.test_datetime

@ pytest.fixture
def test_tzinfo():
    return zoneinfo.ZoneInfo("America/Los_Angeles")

@pytest.fixture
def test_datetime(test_tzinfo):
    return datetime.datetime(1982, 2, 4, 10, 20, tzinfo=test_tzinfo)

@pytest.fixture
def mock_time_sensor(test_datetime, test_tzinfo):
    sensor = _MockTimeSensor()
    sensor.test_datetime = test_datetime
    sensor.tzinfo = test_tzinfo
    return sensor

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
        def get(url, **kwargs):
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

class _MockFujitsu(object):
    def __init__(self):
        self.provider = self._provider()
        self.device = self._device()
    class _provider(object):
        def __init__(self):
            self.username = None
            self.password = None
            self.tokenpath = None
        def __call__(self, username, password, tokenpath=None):
            class _MockFujitsuProvider(object):
                def __init__(sf, username, password, tokenpath=None):
                    self.username = username
                    self.password = password
                    self.tokenpath = tokenpath
            return _MockFujitsuProvider(
                    username, password, tokenpath=tokenpath)
    class _device(object):
        def __init__(self):
            self.dsn = None
            self.api = None
            self.turn_on_called = False
            self.turn_off_called = False
            self.switch_called = False
        def turnOn(self):
            self.turn_on_called = True
        def turnOff(self):
            self.turn_off_called = True
        def __call__(self, dsn=None, api=None):
            class _MockFujitsuDevice(object):
                def __init__(sf, dsn=None, api=None):
                    self.dsn = dsn
                    self.api = api
                turnOn = self.turnOn
                turnOff = self.turnOff
            return _MockFujitsuDevice(dsn=dsn, api=api)

@pytest.fixture
def patch_fujitsu(monkeypatch):
    fujitsu = _MockFujitsu()
    monkeypatch.setattr('pyfujitseu.api.Api', fujitsu.provider)
    monkeypatch.setattr('pyfujitseu.splitAC.splitAC', fujitsu.device)
    return fujitsu

class _MockGosund(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.access_id = None
        self.access_key = None
        self.cache_secs = None
        self.timeout = None
        self.device = _MockDevice()
    def __call__(self, username, password, access_id, access_key,
            status_cache_seconds=None, timeout=None):
        class _MockGosundProvider(object):
            device = self.device
            def __init__(sf, username, password, access_id, access_key,
                    status_cache_seconds=None, timeout=None):
                self.username = username
                self.password = password
                self.access_id = access_id
                self.access_key = access_key
                self.cache_secs = status_cache_seconds
                self.timeout = timeout
            def get_device(sf, device_id):
                return sf.device
        self.provider = _MockGosundProvider(
                username, password, access_id, access_key,
                status_cache_seconds=status_cache_seconds, timeout=timeout)
        return self.provider

@pytest.fixture
def patch_gosundpy(monkeypatch):
    gosund = _MockGosund()
    monkeypatch.setattr('gosundpy.Gosund', gosund)
    return gosund

class _MockAirthings(object):
    def __init__(self):
        self.device_id = None
        self.device = self._MockDevice()
        self.cache_secs = None
        self.timeout = None
    class _MockDevice(AirthingsAPI.device):
        name = 'device_name'
        radon = 123
        temperature = 456
        humidity = 789
        def __init__(self):
            self.data = {
                    'radonShortTermAvg': self.radon * 37,  # convert to Bq/m3
                    'temp': (self.temperature - 32) * 5 / 9, # convert to celcius
                    'humidity': self.humidity,
            }
        def fetch_data(self):
            return self.data
    def __call__(self, client_id, client_secret, data_cache_seconds=None, timeout=None):
        class _MockAirthingsProvider(object):
            device = self.device
            def __init__(sf, client_id, client_secret, data_cache_seconds=None,
                    timeout=None):
                self.client_id = client_id
                self.client_secret = client_secret
                self.cache_secs = data_cache_seconds
                self.timeout = timeout
            def get_device(sf, device_id):
                return sf.device
        self.provider = _MockAirthingsProvider(client_id, client_secret,
                data_cache_seconds=data_cache_seconds, timeout=timeout)
        return self.provider

@pytest.fixture
def patch_airthings(monkeypatch):
    airthings = _MockAirthings()
    monkeypatch.setattr('pydomotic.providers.airthings.AirthingsAPI', airthings)
    return airthings

class _MockMoen(object):
    location_id = 'location_id'
    device_id = 'device_id'
    def __init__(self):
        self.username = None
        self.password = None
        self.open_valve_called = False
        self.close_valve_called = False
        self.set_mode_called_args = None
    def __call__(self, username, password):
        class _MockMoenProvider(object):
            _locations = [
                {
                    'id': 'wrong location_id',
                    'devices': [
                        {'id': 'wrong device_id', 'macAddress': 'macAddress'},
                    ],
                    'account': {'id': 'account_id'},
                },
                {
                    'id': self.location_id,
                    'devices': [
                        {'id': self.device_id, 'macAddress': 'macAddress'},
                    ],
                    'account': {'id': 'account_id'},
                },
            ]
            def __init__(sf, username, password):
                self.username = username
                self.password = password
            def open_valve(sf, device_id):
                self.open_valve_called = True
            def close_valve(sf, device_id):
                self.close_valve_called = True
            def set_mode(sf, location_id, mode, additional_params={}):
                self.set_mode_called_args = (location_id, mode, additional_params)
            def locations(sf):
                return sf._locations
        self.provider = _MockMoenProvider(username, password)
        return self.provider

@pytest.fixture
def patch_moen(monkeypatch):
    moen = _MockMoen()
    monkeypatch.setattr('pyflowater.PyFlo', moen)
    return moen

class _MockEcobee(object):
    def __init__(self):
        self.app_key = None
        self.refresh_token = None
        self.device_id = None
        self.device = self.device()
    class device(object):
        def __init__(self):
            self.temperature = 0
            self.humidity = 0
            self.turn_fan_on_called = False
            self.turn_fan_off_called = False
            self.get_temperature_called = False
        def turn_fan_on(self):
            self.turn_fan_on_called = True
        def turn_fan_off(self):
            self.turn_fan_off_called = True
        def get_temperature(self):
            self.get_temperature_called = True
            return self.temperature
    def __call__(self, app_key, refresh_token):
        class _MockEcobeeProvider(object):
            device = self.device
            def __init__(sf, app_key, refresh_token):
                self.app_key = app_key
                self.refresh_token = refresh_token
            def get_device(sf, device_id):
                return sf.device
        self.provider = _MockEcobeeProvider(app_key, refresh_token)
        return self.provider

@pytest.fixture
def patch_ecobee(monkeypatch):
    ecobee = _MockEcobee()
    monkeypatch.setattr('pydomotic.providers.ecobee.EcobeeAPI', ecobee)
    return ecobee
