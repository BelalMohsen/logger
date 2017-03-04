import datetime
import operator

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from logger.utils import format_timedelta
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


class TableCell(object):
    EMPTY = 0
    START = 1
    END = 3
    FULL = 4
    PARTIAL = 5

    def __init__(self):
        self.state = self.EMPTY
        self.value = "?"
        self.start_factor = 0.0
        self.end_factor = 0.0
        self.color = "#222222"

        self.set_empty()

    def set_full(self):
        self.state = self.FULL
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def set_empty(self):
        self.value = ""
        self.state = self.EMPTY
        self.color = "#FFFFFF00"

    def set_start(self, factor):
        self.state = self.START
        self.start_factor = factor
        self.end_factor = 1.0
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def set_end(self, factor):
        self.state = self.END
        self.start_factor = 0.0
        self.end_factor = factor
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def set_partial(self, start_factor, end_factor):
        self.state = self.PARTIAL
        self.start_factor = start_factor
        self.end_factor = end_factor
        self.value = ""
        self.color = "rgba(0, 150, 0, 1)"

    def render(self):
        style = ""
        attributes = ""
        if self.state == self.EMPTY:
            style = "background-color: {};".format(self.color)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.FULL:
            styles = [
                "border-left: none;",
                "background-color: {};".format(self.color)
            ]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.START:
            styles = [
                "background-image: linear-gradient(to left, {self.color} 0%, {self.color} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-position: 100% 100%;",
                "background-size: {}% 100%".format(int((1-self.start_factor)*100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.END:
            styles = [
                "border-left: none;",
                "background-image: linear-gradient(to right, {self.color} 0%, {self.color} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-size: {}% 100%".format(int(self.end_factor*100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)
        elif self.state == self.PARTIAL:
            fill = self.end_factor - self.start_factor
            styles = [
                "background-image: linear-gradient(to right, {self.color} 0%, {self.color} 100%);".format(self=self),
                "background-repeat: no-repeat;",
                "background-position: {}% 100%;".format(int(self.start_factor*100)),
                "background-size: {}% 100%".format(int(fill * 100))]
            style = " ".join(styles)
            attributes = 'style="{}"'.format(style)

        return '<td class="day_cell" {}>{}</td>'.format(attributes, self.value)


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
    from_date = datetime.date.today() - datetime.timedelta(days=7)
    from_date -= datetime.timedelta(days=datetime.date.today().weekday())

    for day_index, row in enumerate(day_table_rows):
        day = from_date + datetime.timedelta(days=day_index)
        values = Value.objects.filter(timestamp__gte=from_date, timestamp__date=day).order_by('timestamp')

        started = False
        for cell_index, cell in enumerate(row):
            for value in values:
                if value.timestamp.hour == cell_index:
                    ts = value.timestamp
                    if not started:
                        cell.set_start(ts.minute/60)
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

    start = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=12, minute=0, second=0, microsecond=0)
    end = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=12, minute=duration, second=0, microsecond=0)

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
