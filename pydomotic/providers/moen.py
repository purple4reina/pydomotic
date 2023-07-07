import pyflowater

from .base import Provider, Device

class MoenProvider(Provider):

    def __init__(self, username, password):
        self.flo = pyflowater.PyFlo(username, password)

    def get_device(self, device_id, device_name, device_description):
        device = MoenDevice.API(self.flo, device_id)
        return MoenDevice(device, device_name, device_description)

class MoenDevice(Device):

    def turn_on(self):
        self.device.open_valve()

    def turn_off(self):
        self.device.close_valve()

    class API(object):

        def __init__(self, flo, device_id):
            self.flo = flo
            self.device_id = device_id

        def open_valve(self):
            self.flo.open_valve(self.device_id)

        def close_valve(self):
            self.flo.close_valve(self.device_id)
