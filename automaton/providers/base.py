import abc

from ..utils import ObjectMetaclass

class Provider(metaclass=ObjectMetaclass):

    @abc.abstractmethod
    def get_device(self, device_id, device_name, device_description):
        pass

class Device(metaclass=ObjectMetaclass):

    def __init__(self, device, name, description):
        self.device = device
        self.device_name = name
        self.device_description = description

    @property
    def name(self):
        return f'{super().name} {self.device_name}'
