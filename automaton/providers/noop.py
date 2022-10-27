class NoopProvider(object):

    def get_device(self, device_id):
        return NoopDevice(device_id)

class NoopDevice(object):

    def __init__(self, device_id):
        self.device_id = device_id

    def turn_on(self):
        print(f'device "{self.device_id}" turned on')

    def turn_off(self):
        print(f'device "{self.device_id}" turned off')
