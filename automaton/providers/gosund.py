from gosundpy import Gosund

class GosundProvider(object):

    def __init__(self, username, password, access_id, access_key):
        self.gosund = Gosund(username, password, access_id, access_key)

    def get_device(self, device_id):
        return self.gosund.get_device(device_id)
