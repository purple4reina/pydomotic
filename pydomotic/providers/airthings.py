import requests

from .base import Provider, Device
from ..utils import cache_value

class AirthingsAPI(object):

    _auth_token_url = 'https://accounts-api.airthings.com/v1/token'
    _auth_token_data = {
            'grant_type': 'client_credentials',
            'scope': 'read:device:current_values',
    }
    _auth_headers = {}
    _samples_url = 'https://ext-api.airthings.com/v1/devices/{}/latest-samples'

    def __init__(self, client_id, client_secret, data_cache_seconds=None, timeout=None):
        self._auth_credentials = (client_id, client_secret)
        self._timeout = timeout
        if data_cache_seconds:
            self.fetch_data = cache_value(seconds=data_cache_seconds)(self.fetch_data)

    def _get_auth_headers(self):
        resp = requests.post(
                self._auth_token_url,
                data=self._auth_token_data,
                auth=self._auth_credentials,
                timeout=self._timeout,
        )
        resp.raise_for_status()
        self._auth_headers['Authorization'] = f'Bearer {resp.json().get("access_token")}'
        return self._auth_headers

    def fetch_data(self, device_id):
        resp = requests.get(
                url=self._samples_url.format(device_id),
                headers=self._get_auth_headers(),
                timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get('data')

    def get_device(self, device_id):
        return self.device(device_id, self)

    class device(object):

        def __init__(self, device_id, api):
            self.device_id = device_id
            self.api = api

        def fetch_data(self):
            return self.api.fetch_data(self.device_id)

        def get_radon(self):
            return self.fetch_data()['radonShortTermAvg'] / 37  # convert Bq/m3 to pCi/L

        def get_temperature(self):
            return self.fetch_data()['temp'] * 1.8 + 32  # convert C to F

        def get_humidity(self):
            return self.fetch_data()['humidity']

        def get_battery(self):
            return self.fetch_data()['battery']

class AirthingsProvider(Provider):

    def __init__(self, client_id, client_secret, data_cache_seconds=None, timeout=None):
        self.api = AirthingsAPI(client_id, client_secret,
                data_cache_seconds=data_cache_seconds, timeout=timeout)

    def get_device(self, device_id, device_name, device_description):
        device = self.api.get_device(device_id)
        return AirthingsDevice(device, device_name, device_description)

class AirthingsDevice(Device):

    def current_radon(self):
        return self.device.get_radon()

    def current_temperature(self):
        return self.device.get_temperature()

    def current_humidity(self):
        return self.device.get_humidity()
