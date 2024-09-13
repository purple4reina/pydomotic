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

class DeviceGroup(metaclass=ObjectMetaclass):

    def __init__(self, devices, name):
        self.devices = devices
        self.group_name = name

    @property
    def name(self):
        return f'{super().name} {self.group_name}'

    def __getattr__(self, attr):
        if attr == 'devices':
            return self.devices
        if attr == 'group_name':
            return self.group_name
        if attr == 'name':
            return self.name
        if all(hasattr(d, attr) for d in self.devices):
            return lambda *a, **k: [getattr(d, attr)(*a, **k) for d in self.devices]
        super().__getattr__(attr)
