import datetime
import operator

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from logger.timestamp_table import TableCell
from logger.utils import format_timedelta, monday_this_week
from .models import Value, Datum


@login_required
def index(request):
    datums = Datum.objects.filter(user=request.user)
    context = {'datums': datums}
    return render(request, "logger/index.html", context)


@login_required
def datum(request, datum_id):
    datum = get_object_or_404(Datum, user=request.user, pk=datum_id)
    context = {'datum': datum}

    template = 'logger/datum.html'

    if datum.type == Datum.TIMESTAMP:
        template = 'logger/datum_timestamp.html'
        context = timestamp_datum(request, datum, context)

    return render(request, template, context)


def timestamp_datum(request, datum, context):
    values = Value.objects.filter(datum=datum).order_by('timestamp')

    days = {}

    for value in values:
        day = value.timestamp.date().strftime("%Y-%m-%d")

        if day not in days:
            days[day] = []

        days[day].append(value)

    zero_delta = datetime.timedelta()

    for day, entries in days.items():
        start = None
        for entry in entries:
            if start is None:
                start = entry
                entry.diff = zero_delta
                continue
            else:
                diff = entry.timestamp - start.timestamp
                entry.diff = diff
                start = None

    hours = range(24)

    day_table_rows = []
    for day in range(7):
        day_table_rows.append([])
        for hour in range(24):
            day_table_rows[day].append(TableCell())

    from_date = monday_this_week()

    for day_index, row in enumerate(day_table_rows):
        day = from_date + datetime.timedelta(days=day_index)
        values = Value.objects.filter(timestamp__gte=from_date, timestamp__date=day).order_by('timestamp')

        started = False
        for cell_index, cell in enumerate(row):
            for value in values:
                if value.timestamp.hour == cell_index:
                    ts = value.timestamp
                    if not started:
                        cell.set_start(ts.minute / 60)
                        started = True
                    else:
                        if cell.state == TableCell.START:
                            cell.set_partial(cell.start_factor, ts.minute / 60)
                        else:
                            cell.set_end(ts.minute / 60)
                        started = False
            if started and cell.state == TableCell.EMPTY:
                cell.set_full()

    days = sorted(days.items(), key=operator.itemgetter(0))
    sums = []
    for _, entries in days:
        sums.append(sum(entry.diff.total_seconds() for entry in entries))

    days_with_sums = []
    for i in range(len(days)):
        days_with_sums.append((days[i][0], days[i][1], format_timedelta(datetime.timedelta(seconds=sums[i]))))

    context['days'] = days_with_sums
    context['hours'] = hours
    context['day_table_rows'] = day_table_rows

    return context


def add_lunch(request, slug, date, duration):
    datum = get_object_or_404(Datum, slug=slug)
    duration = int(duration)

    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except Exception as e:
        return Http404(e)

    start = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=12, minute=0, second=0,
                              microsecond=0)
    end = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=12, minute=duration, second=0,
                            microsecond=0)

    Value.objects.create(datum=datum, timestamp=start)
    Value.objects.create(datum=datum, timestamp=end)

    return redirect('datum', datum_id=3)


def log_value(request, slug, value):
    datum = get_object_or_404(Datum, slug=slug)

    if datum.type == Datum.FLOAT:
        try:
            val = float(value)
        except Exception:
            return HttpResponse("bad val")
        value = Value(datum=datum, float_value=val)
        value.save()
    elif datum.type == Datum.TIMESTAMP:
        if value != "timestamp":
            return HttpResponse('timestamp datum but value was not "timestamp"')

        value = Value(datum=datum)
        value.save()
    else:
        raise NotImplementedError('handling for {} datums not implemented yet'.format(datum.type))

    return HttpResponse("saved: slug: {}, value: {}".format(slug, value))
