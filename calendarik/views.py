from django.shortcuts import render, redirect
import datetime
import calendar
from itertools import groupby, zip_longest
from django.db import models
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models.functions import JSONObject
from django.db.models import OuterRef
from django_generate_series.models import generate_series
from calendarik.models import CalendarEvent, Contact
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from .forms import CalendarEventForm


# Create your views here.
@login_required
def homepage(request):
    date = request.GET.get("date", datetime.date.today())
    begin_of_month = datetime.date(date.year, date.month, 1)
    six_months = begin_of_month + relativedelta(months=+6)
    six_months = six_months.replace(
        day=calendar.monthrange(six_months.year, six_months.month)[1]
    )
    artists = []
    user_groups = request.user.groups.all()
    if not user_groups or user_groups[0].name.lower() == "artist":
        artists = (request.user.id,)
    else:
        is_artists = request.GET.get("artist")
        if is_artists:
            artists = [int(x) for x in request.GET.get("artist").split(",")]
    # enrich results with data diapaned in template
    event_query = CalendarEvent.objects.filter(
        date=OuterRef("term"), contact__id__in=artists
    ).values(
        json=JSONObject(
            event_city="event__city__name",
            event_title="event__title",
            status="event__status",
            artist="contact__id",
        )
    )
    query = generate_series(
        begin_of_month, six_months, "1 day", output_field=models.DateField
    ).annotate(events=ArraySubquery(event_query))
    query = groupby(query, lambda x: x.term.strftime("%Y-%m"))
    query = [(x[0], list(x[1])) for x in query][:-1]
    periods = [x[0] for x in query]
    query = zip_longest(*[x[1] for x in query], fillvalue=None)
    art_query = Contact.objects.filter(calendar=True).values("name").all()
    return render(request, "../templates/homepage.html", {"periods": periods, "data": query, "all_artists": art_query})


@login_required
def add_event(request):
    # form with CalendarEvent
    if request.method == "POST":
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            form_data = form.clean()
            begin = form_data.pop("event_start")
            end = form_data.pop("event_end", begin)
            if end is None:
                end = begin
            for date in generate_series(begin, end, "1 day", output_field=models.DateField):
                form_data["date"] = date.term
                obj = CalendarEvent(**form_data)
                obj.save()
            return redirect("/?artist={}".format(form_data["contact"].id))
        else:
            return render(request, 'add_event.html', {"form": form})
    else:
        form = CalendarEventForm()
    return render(request, 'add_event.html', {"form": form})


