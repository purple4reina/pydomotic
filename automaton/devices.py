class Device(object):

    def __init__(self, name, provider_device):
        self.name = name
        self.provider_device = provider_device

    # TODO: __str__

class DeviceOnOffMixin(object):

    def turn_on(self):
        self.provider_device.turn_on()

    def turn_off(self):
        self.provider_device.turn_off()

class SwitchDevice(Device, DeviceOnOffMixin):
    pass

class LightBulbDevice(Device, DeviceOnOffMixin):
    pass
