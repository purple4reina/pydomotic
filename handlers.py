import actions
import triggers

def corn_bulb(event, context):
    if triggers.is_day_of_week('sunday'):
        if triggers.is_between_hours(10, 11):
            actions.turn_on_corn_bulb()
        else:
            actions.turn_off_corn_bulb()

if __name__ == '__main__':
    corn_bulb({}, {})
