import gosundpy

from .base import Provider, Device

class GosundProvider(Provider):

    def __init__(self, username, password, access_id, access_key):
        self.gosund = gosundpy.Gosund(username, password, access_id, access_key)

    def get_device(self, device_id):
        device = self.gosund.get_device(device_id)
        return GosundDevice(device)

class GosundDevice(Device):

    # TODO: add name of device

    def __init__(self, device):
        self.device = device

    def turn_on(self):
        self.device.turn_on()

    def turn_off(self):
        self.device.turn_off()

    def switch(self):
        self.device.switch()
