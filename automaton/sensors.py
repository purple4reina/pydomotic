class AQISensor(object):

    def get_aqi(self):
        # TODO: implement
        import random
        return random.randint(1, 120)

    # TODO: __str__

class SunSensor(object):

    def get_sunrise(self):
        # TODO: implement
        import datetime
        return datetime.datetime.now()

    def get_sunset(self):
        # TODO: implement
        import datetime
        return datetime.datetime.now()

    # TODO: __str__
