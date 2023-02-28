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
from django.db.models import Q
from django_generate_series.models import generate_series
from calendarik.models import CalendarEvent, Contact, Artist, Opera, Role, Promoter, LastSession, Event, City
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from .forms import SearchForm, TravelForm, OtherForm, EngagementForm, ContactForm
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
    is_artists = request.GET.get("artist")
    if is_artists:
        artists = [int(x) for x in request.GET.get("artist").split(",")]
    user_groups = request.user.groups.all()
    if not user_groups or user_groups[0].name.lower() == "artist":
        artists = (request.user.id,)
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
    return render(request, "../templates/search.html", context)

def get_roles(request):
    if request.method == "GET":
        opera_id = request.GET.get("opera")
        roles = Role.objects.filter(opera__title__icontains=opera_id).values("name").all()
        return JsonResponse(list(roles), safe=False)

@login_required
def edit_event(request):
    if request.method == "GET":
        event_id = request.GET.get("id")
        event = CalendarEvent.objects.get(id=event_id)
        # TODO: select form depends on type of event
        if event.event.event_type == "travel":
            form = TravelForm()
            template = "../templates/travel.html"
        elif event.event.event_type == "engagement":
            template="../templates/engagement.html"
            form = EngagementForm()
        else:
            template = "../templates/other.html"
            form = OtherForm()
        return render(request, template, {"form": form, "instance": event})
    else:
        event_id = request.POST.get("event_id")
        event = CalendarEvent.objects.get(id=event_id)
        # TODO: select form depends on type of event
        if event.event.event_type == "travel":
            form = TravelForm(request.POST)
        elif event.event.event_type == "engagement":
            form = EngagementForm(request.POST)
        else:
            form = OtherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
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
    all_cities = City.objects.only("name").all()
    context = {"form": form, "start_date": start_date, "all_cities": all_cities, "artists": get_artists_from_session(request.user)}
    return context


def fill_calendar(event, periods):
    for period in periods:
        for date in rrule(DAILY, dtstart=period[0], until=period[1]):
            CalendarEvent.objects.create(
                event=event,
                date=date,
                artist=event.artist,
                status=event.status,
                title=event.title,
                engagement_type=period[2] if len(period) > 2 else None,
            )

def separate_form_data(request, form):
    periods = []
    for i in range(10):
        if f"event_start_{i}" in request.POST.keys():
            season_start = datetime.datetime.strptime(request.POST[f"event_start_{i}"], "%Y-%m-%d").date()
            season_end = request.POST[f"event_end_{i}"]
            if season_end=="":
                season_end = season_start
            else:
                season_end = datetime.datetime.strptime(season_end, "%Y-%m-%d").date()
            event_type = request.POST.get(f"event_type_{i}",None)
            periods.append((season_start, season_end, event_type))
    happening = form.cleaned_data.pop("happening")
    artist = Artist.objects.get(id=form.cleaned_data.pop("artist"))
    return periods, happening, artist


@login_required
def event(request):
    ttype = request.GET.get("type", "other")
    if ttype == "other":
        form_type = OtherForm
        event_type= 3
        template = "../templates/other.html"
    elif ttype == "travel":
        form_type = TravelForm
        event_type= 2
        template = "../templates/travel.html"
    else:
        form_type = EngagementForm
        event_type=4
        template = "../templates/engagement.html"
    context = create_context(form_type(), request)
    if request.method == "POST":
        form = form_type(request.POST)
        if form.is_valid():
            periods, happening, artist = separate_form_data(request, form)
#            inner_files = request.FILES.getlist("inner_files")
#            artist_files = request.FILES.getlist("artist_files")
            _ = form.cleaned_data.pop("inner_files")
            _ = form.cleaned_data.pop("artist_files")
            _ = form.cleaned_data.pop("engagement_type", None)
            if form.cleaned_data.get("city","") != "":
                form.cleaned_data["city"] = City.objects.get_or_create(name=form.cleaned_data["city"])[0]
            else:
                form.cleaned_data["city"] = None
            if form.cleaned_data.get("opera","") != "":
                form.cleaned_data["opera"] = Opera.objects.get_or_create(title=form.cleaned_data["opera"])[0]
            else:
                form.cleaned_data["opera"] = None
            if form.cleaned_data.get("role","") != "":
                form.cleaned_data["role"] = Role.objects.get_or_create(name=form.cleaned_data["role"], opera=form.cleaned_data["opera"])[0]
            else:
                form.cleaned_data["role"] = None
            if form.cleaned_data.get("promoter","") != "":
                form.cleaned_data["promoter"] = Promoter.objects.get_or_create(name=form.cleaned_data["promoter"])[0]
            else:
                form.cleaned_data["promoter"] = None
            if form.cleaned_data.get("contact","") != "":
                form.cleaned_data["contact"] = Contact.objects.get_or_create(name=form.cleaned_data["contact"])[0]
            else:
                form.cleaned_data["contact"] = None
            event = Event.objects.create(**form.cleaned_data)
            event.artist = artist
            event.last_edited = f"{request.user.username} {datetime.datetime.now()}"
            event.event_type = event_type
            if happening:
                event.status = "happening"
            event.save()
            fill_calendar(event, periods)
            return redirect("/")
    return render(request, template, context)

@login_required
def contact_list(request):
    if request.method == "POST":
        query = request.POST.get("query", "")
        contacts = Contact.objects.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query) | Q(position__icontains=query) | Q(organization__name__icontains=query)).all()
    else:
        contacts = Contact.objects.all()
    return render(request, "../templates/contact_list.html", {"contacts": contacts})

@login_required
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/contact_list")
    else:
        form = ContactForm()
    return render(request, "../templates/contact.html", {"form": form})
