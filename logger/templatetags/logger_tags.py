from django import template

register = template.Library()


def __to_weekday_number(number):
    if isinstance(number, str):
        if number.isdigit():
            return int(number)
    elif isinstance(number, int):
        return number
    else:
        return -1


@register.filter
def number_to_weekday(number):
    number = __to_weekday_number(number)
    if not 0 <= number <= 6:
        return "SOMEDAY"

    # should use datetime parsing or something, but meh
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[number]


@register.filter
def number_to_short_weekday(number):
    return number_to_weekday(number)[:3]


