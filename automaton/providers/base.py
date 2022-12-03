import abc

from ..utils import ObjectMetaclass

class Provider(metaclass=ObjectMetaclass):

    @abc.abstractmethod
    def get_device(self, device_id):
        pass

class Device(metaclass=ObjectMetaclass):

    @abc.abstractmethod
    def turn_on(self):
        pass

    @abc.abstractmethod
    def turn_off(self):
        pass

    @abc.abstractmethod
    def switch(self):
        pass
