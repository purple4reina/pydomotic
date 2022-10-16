import datetime

def is_between_hours(start, end):
    now = datetime.datetime.now()
    return now.hour >= start and now.hour < end

days = {
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6,
        'sunday': 7,
}

def is_day_of_week(day):
    day_num = days.get(day.lower())
    now = datetime.datetime.now()
    return now.isoweekday() == day_num
