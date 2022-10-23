class TurnOnAction(object):

    def __init__(self, device):
        self.device = device

    def run(self):
        self.device.turn_on()

class TurnOffAction(object):

    def __init__(self, device):
        self.device = device

    def run(self):
        self.device.turn_off()
