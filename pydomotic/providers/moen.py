import pyflowater

from .base import Provider, Device

class MoenProvider(Provider):

    def __init__(self, username, password):
        self.flo = pyflowater.PyFlo(username, password)

    def get_device(self, device_id, device_name, device_description):
        location_id = self._get_location_id(device_id)
        device = MoenDevice.API(self.flo, location_id, device_id)
        return MoenDevice(device, device_name, device_description)

    def _get_location_id(self, device_id):
        for location in self.flo.locations():
            for device in location['devices']:
                if device['id'] == device_id:
                    return location['id']

class MoenDevice(Device):

    def turn_on(self):
        self.device.open_valve()

    def turn_off(self):
        self.device.close_valve()

    def set_mode(self, mode, params):
        return self.device.set_mode(mode, params)

    class API(object):

        def __init__(self, flo, location_id, device_id):
            self.flo = flo
            self.location_id = location_id
            self.device_id = device_id

        def open_valve(self):
            self.flo.open_valve(self.device_id)

        def close_valve(self):
            self.flo.close_valve(self.device_id)

        def set_mode(self, mode, params):
            return self.flo.set_mode(self.location_id, mode, additional_params=params)
