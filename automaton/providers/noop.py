import logging

logger = logging.getLogger(__name__)

class NoopProvider(object):

    def get_device(self, device_id):
        return NoopDevice(device_id)

class NoopDevice(object):

    def __init__(self, device_id):
        self.device_id = device_id

    def turn_on(self):
        logger.debug('device "%s" turned on', self.device_id)

    def turn_off(self):
        logger.debug('device "%s" turned off', self.device_id)
