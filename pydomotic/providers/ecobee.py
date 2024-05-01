import logging
import requests

from pydomotic.providers.base import Provider, Device

logger = logging.getLogger(__name__)

class EcobeeProvider(Provider):

    def __init__(self, app_key, refresh_token):
        self.api = EcobeeAPI(app_key, refresh_token)

    def get_device(self, device_id, device_name, device_description):
        device = self.api.get_device(device_id)
        return EcobeeDevice(device, device_name, device_description)

class EcobeeDevice(Device):

    def turn_on(self):
        self.device.turn_fan_on()
        logger.debug('device "%s" turned on', self.name)

    def turn_off(self):
        self.device.turn_fan_off()
        logger.debug('device "%s" turned off', self.name)

    def current_temperature(self):
        return self.device.get_temperature()

class EcobeeAPI(object):

    api_url = 'https://api.ecobee.com'
    token_url = api_url + '/token'
    thermostat_url = api_url + '/1/thermostat'

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
    }

    def __init__(self, app_key, refresh_token):
        self._refresh_token = refresh_token
        self._app_key = app_key
        self._expires_at = 0

    def get_device(self, device_id):
        return self.device(device_id, self)

    def get_thermostat(self):
        return self._make_request('GET', self.thermostat_url, params={
            'format': 'json',
            'body': """{
                "selection": {
                    "selectionType": "registered",
                    "selectionMatch": "",
                    "includeSensors": true
                }
            }""",
        })

    def get_sensor_data(self, sensor_id):
        for thermostat in self.get_thermostat()['thermostatList']:
            for sensor in thermostat['remoteSensors']:
                if sensor['id'] == sensor_id:
                    return sensor
        raise EcobeeError(f'sensor "{sensor_id}" not found')

    def set_fan_hold(self, mode):
        self._make_request('POST', self.thermostat_url, params={
            'format': 'json',
            'body': f"""{{
                "selection": {{
                    "selectionType":"registered",
                    "selectionMatch":""
                }},
                "functions": [
                    {{
                        "type":"setHold",
                        "params":{{
                            "holdType":"indefinite",
                            "fan":"{mode}"
                        }}
                    }}
                ]
            }}""",
        })

    def _authenticate(self):
        resp = self._make_request('POST', self.token_url, params={
            'grant_type': 'refresh_token',
            'client_id': self._app_key,
            'code': self._refresh_token,
        })
        self._expires_at = time.time() + resp.get('expires_in')
        access_token, token_type = resp.get('access_token'), resp.get('token_type')
        self.headers['Authorization'] = f'{token_type} {access_token}'

    def _make_request(self, method, url, params=None):
        if time.time() > self._expires_at and url != self.token_url:
            self._authenticate()
        resp = requests.request(method, url, params=params, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    class device(object):

        def __init__(self, device_id, api):
            self.device_id = device_id
            self.api = api

        def turn_fan_on(self):
            self.api.set_fan_hold('on')

        def turn_fan_off(self):
            self.api.set_fan_hold('auto')

        def get_temperature(self):
            data = self.api.get_sensor_data(self.device_id)
            for cap in data['capability']:
                if cap['type'] == 'temperature':
                    return int(cap['value']) / 10
            raise EcobeeError(f'temperature sensor not found for device "{self.device_id}"')

        def get_humidity(self):
            data = self.api.get_sensor_data(self.device_id)
            for cap in data['capability']:
                if cap['type'] == 'humidity':
                    return int(cap['value'])
            raise EcobeeError(f'humidity sensor not found for device "{self.device_id}"')

class EcobeeError(Exception):
    pass
