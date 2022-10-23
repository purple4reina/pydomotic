import os

from gosundpy import GosundSwitchDevice, GosundLightBulbDevice

from .actions import TurnOnAction, TurnOffAction
from .components import Component
from .devices import SwitchDevice, LightBulbDevice
from .providers.gosund import GosundProvider
from .triggers import AQITrigger, IsoWeekdayTrigger, TimeTrigger

def parse_yaml(config_file):

    # TODO: implement

    username = os.environ.get('GOSUND_USERNAME', 'username')
    password = os.environ.get('GOSUND_PASSWORD', 'password')
    access_id = os.environ.get('GOSUND_ACCESS_ID', 'access_id')
    access_key = os.environ.get('GOSUND_ACCESS_KEY', 'access_key')

    gosund_manager = GosundProvider(username, password, access_id,
            access_key).gosund.manager

    switch = SwitchDevice('switch-A', GosundSwitchDevice(
            '3460050570039f61e488', gosund_manager))
    bulb = LightBulbDevice('bulb-A', GosundLightBulbDevice(
            'eb46f5bc889a96fe4ecray', gosund_manager))

    return [
            Component(
                ifs=[
                    AQITrigger(lambda aqi: aqi > 100),
                ],
                thens=[
                    TurnOnAction(switch),
                ],
                elses=[
                    TurnOffAction(switch),
                ],
            ),
            Component(
                ifs=[
                    IsoWeekdayTrigger(5, 6),
                    TimeTrigger(hour=15, minute=0),
                ],
                thens=[
                    TurnOnAction(bulb),
                ],
            ),
            Component(
                ifs=[
                    IsoWeekdayTrigger(5, 6),
                    TimeTrigger(hour=20, minute=0),
                ],
                thens=[
                    TurnOffAction(bulb),
                ],
            )
    ]
