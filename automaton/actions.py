import abc

from .utils import ObjectMetaclass

class _Action(metaclass=ObjectMetaclass):

    @abc.abstractmethod
    def run(self):
        pass

class _DeviceAction(_Action):

    required_class_attrs = ['device_action_method_name']

    def __init__(self, device, device_name):
        self.device = device
        self.device_name = device_name

    def run(self):
        getattr(self.device, self.device_action_method_name)()

    @property
    def name(self):
        return f'{super().name} {self.device_name}'

class TurnOnAction(_DeviceAction):

    device_action_method_name = 'turn_on'

class TurnOffAction(_DeviceAction):

    device_action_method_name = 'turn_off'

class SwitchAction(_DeviceAction):

    device_action_method_name = 'switch'
