import logging

import pyfujitseu.api
import pyfujitseu.splitAC

from .base import Provider, Device

logger = logging.getLogger(__name__)

# see https://docs.aylanetworks.com/reference/getting_started

class FujitsuProvider(Provider):

    def __init__(self, username, password, tokenpath='/tmp/token.txt'):
        self.fujitsu = pyfujitseu.api.Api(username, password, tokenpath=tokenpath)

    def get_device(self, device_id, device_name, device_description):
        device = pyfujitseu.splitAC.splitAC(dsn=device_id, api=self.fujitsu)
        return FujitsuDevice(device, device_name, device_description)

class FujitsuDevice(Device):

    def turn_on(self):
        self.device.turnOn()
        logger.debug('device "%s" turned on', self.name)

    def turn_off(self):
        self.device.turnOff()
        logger.debug('device "%s" turned off', self.name)

    def switch(self):
        logger.debug('switch action not implemented for fujitsu device')
