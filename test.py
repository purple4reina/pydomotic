import os
import time

from gosundpy import Gosund

USERNAME = os.environ['GOSUND_USERNAME']
PASSWORD = os.environ['GOSUND_PASSWORD']
ACCESS_ID = os.environ['GOSUND_ACCESS_ID']
ACCESS_KEY = os.environ['GOSUND_ACCESS_KEY']

gosund = Gosund(USERNAME, PASSWORD, ACCESS_ID, ACCESS_KEY)
light_bulb = gosund.get_device('eb46f5bc889a96fe4ecray')

def toggle(event, context):
    light_bulb.switch()

if __name__ == '__main__':
    toggle({}, {})
