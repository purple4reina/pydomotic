import abc

from .utils import ObjectMetaclass

class _Action(metaclass=ObjectMetaclass):

    @abc.abstractmethod
    def run(self):
        pass

class _DeviceAction(_Action):

    required_class_attrs = ['device_action_method_name']

    def __init__(self, device):
        self.device = device

    def run(self):
        getattr(self.device, self.device_action_method_name)()

    @property
    def name(self):
        return f'{super().name} {self.device.name}'

class TurnOnAction(_DeviceAction):

    device_action_method_name = 'turn_on'

class TurnOffAction(_DeviceAction):

    device_action_method_name = 'turn_off'

class SwitchAction(_DeviceAction):

    device_action_method_name = 'switch'

class ExecuteCodeAction(_Action):

    def __init__(self, execute_method, context):
        self.execute_method = execute_method
        self.context = context

    def run(self):
        self.execute_method(self.context)

    @property
    def name(self):
        m = self.execute_method
        return f'{super().name} {m.__module__}.{m.__name__}'
