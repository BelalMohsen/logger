import datetime


def format_timedelta(delta):
    days, seconds = delta.days, delta.seconds
    hours = int((seconds - (seconds % 3600))/3600)
    seconds %= 3600
    minutes = int((seconds - (seconds % 60)) / 60)
    seconds %= 60
    if days:
        return "{:d}d {:d}h {:d}m {:d}s".format(days, hours, minutes, seconds)
    else:
        return "{:d}h {:d}m {:d}s".format(hours, minutes, seconds)


def monday_this_week(today=None):
    if today is None:
        today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())

    return monday
