import abc

from .utils import ObjectMetaclass, import_method

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

class SetModeAction(_Action):

    def __init__(self, device, mode, extra_params):
        self.device = device
        self.mode = mode
        self.extra_params = extra_params

    def run(self):
        self.device.set_mode(self.mode, self.extra_params)

    @property
    def name(self):
        return f'{super().name} {self.device.name} {self.mode}'

class ExecuteCodeAction(_Action):

    def __init__(self, import_path, context):
        self.import_path = import_path
        self.context = context
        self._execute_method = None

    @property
    def execute_method(self):
        if not self._execute_method:
            self._execute_method = import_method(self.import_path)
        return self._execute_method

    def run(self):
        self.execute_method(self.context)

    @property
    def name(self):
        return f'{super().name} {self.import_path}'
