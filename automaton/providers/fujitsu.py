import logging

import pyfujitseu.api
import pyfujitseu.splitAC

logger = logging.getLogger(__name__)

# see https://docs.aylanetworks.com/reference/getting_started

class FujitsuProvider(object):

    def __init__(self, username, password, tokenpath='/tmp/token.txt'):
        self.fujitsu = pyfujitseu.api.Api(username, password, tokenpath=tokenpath)

    def get_device(self, device_id):
        device = pyfujitseu.splitAC.splitAC(dsn=device_id, api=self.fujitsu)
        return FujitsuDevice(device)

class FujitsuDevice(object):

    def __init__(self, device):
        self.device = device

    def turn_on(self):
        self.device.turnOn()

    def turn_off(self):
        self.device.turnOff()

    def switch(self):
        logger.debug('switch action not implemented for fujitsu device')
