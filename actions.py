import os
import time

from gosundpy import Gosund

USERNAME = os.environ['GOSUND_USERNAME']
PASSWORD = os.environ['GOSUND_PASSWORD']
ACCESS_ID = os.environ['GOSUND_ACCESS_ID']
ACCESS_KEY = os.environ['GOSUND_ACCESS_KEY']

gosund = Gosund(USERNAME, PASSWORD, ACCESS_ID, ACCESS_KEY)
light_bulb = gosund.get_device('eb46f5bc889a96fe4ecray')
switch = gosund.get_device('3460050570039f61e488')

def turn_on_corn_bulb():
    switch.turn_on()

def turn_off_corn_bulb():
    switch.turn_off()
