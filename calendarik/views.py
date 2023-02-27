from django.shortcuts import render, redirect
import datetime
import calendar
from itertools import groupby, zip_longest
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models.functions import JSONObject
from django.db.models import OuterRef
from django.http import JsonResponse
from django_generate_series.models import generate_series
from calendarik.models import CalendarEvent, Contact, Artist, Opera, Role, Promoter, LastSession, Event
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from .forms import SearchForm, TravelForm, OtherForm, EngagementForm
from dateutil.rrule import rrule, DAILY

# Create your views here.
@login_required
def homepage(request):
    date = ""
    artists = []
    last_session = LastSession.objects.get(user=request.user)
    if last_session:
        date = last_session.date
        artists = last_session.artists
    if not artists:
        user_groups = request.user.groups.all()
        if not user_groups or user_groups[0].name.lower() == "artist":
            artists = (request.user.id,)
        else:
            is_artists = request.GET.get("artist")
            if is_artists:
                artists = [int(x) for x in request.GET.get("artist").split(",")]
    if not date:
        date = request.GET.get("date", datetime.date.today())
    # get all events for selected artists
    begin_of_month = datetime.date(date.year, date.month, 1)
    six_months = begin_of_month + relativedelta(months=+6)
    six_months = six_months.replace(
        day=calendar.monthrange(six_months.year, six_months.month)[1]
    )
    # enrich results with data in template
    event_query = CalendarEvent.objects.filter(
        date=OuterRef("term"), artist__id__in=artists
    ).values(
        json=JSONObject(
            event_id="id",
            event_title="title",
            status="status",
            artist="artist__id",
        )
    )
    query = generate_series(
        begin_of_month, six_months, "1 day", output_field=models.DateField
    ).annotate(events=ArraySubquery(event_query))
    query = groupby(query, lambda x: x.term.strftime("%Y-%m"))
    query = [(x[0], list(x[1])) for x in query][:-1]
    periods = [x[0] for x in query]
    query = zip_longest(*[x[1] for x in query], fillvalue=None)
    art_query = Artist.objects.filter(calendar=True).values("name").all()
    # TODO: record last session
    LastSession.objects.update_or_create(
        user=request.user,
        defaults={
            "date": date,
            "artists": artists,
        },
    )

    return render(request, "../templates/homepage.html", {"periods": periods, "data": query, "all_artists": art_query})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "../templates/login.html")
    return render(request, "../templates/login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("/login")

@login_required
def search(request):
    all_operas = Opera.objects.all()
    all_promoters = Promoter.objects.all()
    all_roles = Role.objects.all()
    form = SearchForm()
    context = {"all_operas": all_operas, "all_roles": all_roles, "all_promoters": all_promoters, "form": form}
    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_query = CalendarEvent.objects
            if search_form.cleaned_data["opera"]:
                search_query = search_query.filter(event__opera__title__icontains=search_form.cleaned_data["opera"])
            if search_form.cleaned_data["role"]:
                search_query = search_query.filter(event__role__name__icontains=search_form.cleaned_data["role"])
            if search_form.cleaned_data["promoter"]:
                search_query = search_query.filter(event__promoter__name__icontains=search_form.cleaned_data["promoter"])
            res = search_query.all()
            context["results"] = res
            return render(request, "../templates/search.html", context)
        else:
            return render(request, "../templates/search.html", context)
    return render(request, "../templates/search.html", context)

def get_roles(request):
    if request.method == "GET":
        opera_id = request.GET.get("opera")
        roles = Role.objects.filter(opera__title__icontains=opera_id).values("name").all()
        return JsonResponse(list(roles), safe=False)

@login_required
def edit_event(request):
    if request.method == "GET":
        event_id = request.GET.get("event_id")
        event = CalendarEvent.objects.get(id=event_id)
        # TODO: select form depends on type of event
        form = CalendarEventForm(instance=event)
        return render(request, "../templates/edit_event.html", {"form": form})
    else:
        event_id = request.POST.get("event_id")
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/?restore_session=1")
        else:
            return render(request, "../templates/edit_event.html", {"form": form})


def get_artists_from_session(user):
    last_session = LastSession.objects.get(user=user)
    if last_session is not None:
        artists = Artist.objects.filter(id__in=last_session.artists).values_list("id", "name").all()
    else:
        artists = Artist.objects.values_list("id", "name").all()
    return artists


def create_context(form, request):
    start_date = request.GET.get("date")
    context = {"form": form, "start_date": start_date, "artists": get_artists_from_session(request.user)}
    return context


def fill_calendar(event, event_start, event_end):
    if event_end is None:
        event_end = event_start
    for date in rrule(DAILY, dtstart=event_start, until=event_end):
        CalendarEvent.objects.create(
            event=event,
            date=date,
            artist=event.artist,
            status=event.status,
            title=event.title,
        )

def separate_form_data(form):
    event_start = form.cleaned_data.pop("event_start")
    event_end = form.cleaned_data.pop("event_end")
    happening = form.cleaned_data.pop("happening")
#    inner_files = form.cleaned_data.pop("inner_files")
#    artist_files = form.cleaned_data.pop("artist_files")
    artist = Artist.objects.get(id=form.cleaned_data.pop("artist"))
    return event_start, event_end, happening, artist


@login_required
def travel(request):
    context = create_context(TravelForm, request)
    if request.method == "POST":
        form = TravelForm(request.POST)
        if form.is_valid():
            event_start, event_end, happening, artist = separate_form_data(form)
            event = Event.objects.create(**form.cleaned_data)
            event.artist = artist
            event.event_type = 1
            # TODO: event title generation
            if happening:
                event.status = "happening"
            event.save()
            fill_calendar(event, event_start, event_end)
            return redirect("/")
    return render(request, "../templates/travel.html", context)




@login_required
def other(request):
    context = create_context(OtherForm(), request)
    if request.method == "POST":
        form = OtherForm(request.POST)
        if form.is_valid():
            event_start, event_end, happening, artist = separate_form_data(form)
            event = Event.objects.create(**form.cleaned_data)
            event.artist = artist
            event.event_type = 3
            # TODO: event title generation
            if happening:
                event.status = "happening"
            event.save()
            fill_calendar(event, event_start, event_end)
            return redirect("/")
    return render(request, "../templates/other.html", {"form": form})

@login_required
def engagement(request):
    context = create_context(EngagementForm(), request)
    if request.method == "POST":
        form = EngagementForm(request.POST)
        if form.is_valid():
            event_start, event_end, happening, artist = separate_form_data(form)
            event = Event.objects.create(**form.cleaned_data)
            event.artist = artist
            event.event_type = 3
            # TODO: event title generation
            if happening:
                event.status = "happening"
            event.save()
            fill_calendar(event, event_start, event_end)
            return redirect("/")
    return render(request, "../templates/engagement.html", context)
