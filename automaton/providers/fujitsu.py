import pyfujitseu.api
import pyfujitseu.splitAC

class FujitsuProvider(object):

    def __init__(self, username, password, tokenpath='/tmp/token.txt'):
        self.fujitsu = pyfujitseu.api.Api(username, password, tokenpath=tokenpath)

    def get_device(self, device_id):
        return FujitsuDevice(dsn=device_id, api=self.fujitsu)

class FujitsuDevice(object):

    def __init__(self, device):
        self.device = device

    def turn_on(self):
        return self.device.turnOn()

    def turn_off(self):
        return self.device.turnOff()
