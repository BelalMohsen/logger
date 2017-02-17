import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Value, Datum

@login_required
def index(request):
    context = {}
    return render(request, "logger/index.html", context)


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
