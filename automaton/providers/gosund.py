from gosundpy import Gosund

class GosundProvider(object):

    def __init__(self, username, password, access_id, access_key):
        self.gosund = Gosund(username, password, access_id, access_key)

    def get_device(self, device_id):
        device = self.gosund.get_device(device_id)
        return GosundDevice(device)

class GosundDevice(object):

    def __init__(self, device):
        self.device = device

    def turn_on(self):
        return self.device.turn_on()

    def turn_off(self):
        return self.device.turn_off()
