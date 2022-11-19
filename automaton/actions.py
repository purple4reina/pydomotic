from .utils import Nameable

class TurnOnAction(Nameable):

    # TODO: add target (name of the device)

    def __init__(self, device):
        self.device = device

    def run(self):
        self.device.turn_on()

class TurnOffAction(Nameable):

    def __init__(self, device):
        self.device = device

    def run(self):
        self.device.turn_off()
