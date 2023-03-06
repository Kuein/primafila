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
from calendarik.models import (
    CalendarEvent,
    Contact,
    Artist,
    Opera,
    Role,
    Promoter,
    LastSession,
    Event,
    City,
)
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from .forms import (
    SearchForm,
    TravelForm,
    OtherForm,
    EngagementForm,
    ContactForm,
    TravelDataSetForm,
    EngagementDataSetForm,
    TravelDataSet,
    EngagementDataSet,
)
from dateutil.rrule import rrule, DAILY
from django.forms import inlineformset_factory


# Create your views here.
@login_required
def homepage(request):
    date = datetime.date.today()
    artists = []
    last_session, created = LastSession.objects.get_or_create(user=request.user)
    if last_session and not created:
        date = last_session.date if last_session.date else date
        artists = last_session.artists
    is_artists = request.GET.get("artist")
    if is_artists:
        artists.insert(0, int(is_artists))
    artists = artists[:2] if len(artists) > 2 else artists
    user_groups = request.user.groups.all()
    if not user_groups or user_groups[0].name.lower() == "artist":
        artists = (request.user.id,)
    is_date = request.GET.get("date")
    if is_date:
        date = datetime.datetime.strptime(is_date, "%Y-%m-%d").date()
    # get all events for selected artists
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    date = datetime.date(date.year, date.month, 1)
    year_ago = date - relativedelta(years=1)
    six_months = date + relativedelta(months=+5)
    six_months_pre = six_months.replace(
        day=calendar.monthrange(six_months.year, six_months.month)[1]
    )
    six_months_ago = date - relativedelta(months=+5)
    year_ahead = date + relativedelta(years=+1)
    event_query = CalendarEvent.objects.filter(
        start_date__lte=OuterRef("term"), end_date__gte=OuterRef("term")
    )
    if 1000 in artists:
        event_query = event_query.filter(
            Q(event__isnull=True) | Q(engagement_type=1) | Q(event__artist_id__in=artists)
        )
    else:
        event_query = event_query.filter(
            Q(event__artist__id__in=artists) | Q(event__isnull=True)
        )
    event_query = event_query.values(
        json=JSONObject(
            event_id="id",
            event_title="title",
            status="event__status",
            happend="happend",
        )
    )
    query = generate_series(
        date, six_months_pre, "1 day", output_field=models.DateField
    ).annotate(events=ArraySubquery(event_query))
    query = groupby(query, lambda x: x.term.strftime("%Y-%m"))
    query = [(x[0], list(x[1])) for x in query]
    periods = [x[0] for x in query]
    query = zip_longest(*[x[1] for x in query], fillvalue=None)
    art_query = Artist.objects.filter(calendar=True).values_list("id", "name").all()
    LastSession.objects.update_or_create(
        user=request.user,
        defaults={
            "date": date,
            "artists": artists,
        },
    )
    if 1000 in artists:
        nice_artists = ["Premiere"]
    else:
        nice_artists = []
    query_artists = Artist.objects.filter(id__in=artists).values_list("name", flat=True)
    for artist in query_artists:
        nice_artists.append(artist)

    return render(
        request,
        "../templates/homepage.html",
        {
            "periods": periods,
            "data": query,
            "all_artists": art_query,
            "year_ago": year_ago,
            "year_ahead": year_ahead,
            "six_months_ago": six_months_ago,
            "six_months_ahead": six_months,
            "today": datetime.datetime.now(),
            "artists": nice_artists,
        },
    )


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
    context = {
        "all_operas": all_operas,
        "all_roles": all_roles,
        "all_promoters": all_promoters,
        "form": form,
    }
    if request.method == "POST":
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search_query = CalendarEvent.objects
            if search_form.cleaned_data["opera"]:
                search_query = search_query.filter(
                    event__opera__title__icontains=search_form.cleaned_data["opera"]
                )
            if search_form.cleaned_data["role"]:
                search_query = search_query.filter(
                    event__role__name__icontains=search_form.cleaned_data["role"]
                )
            if search_form.cleaned_data["promoter"]:
                search_query = search_query.filter(
                    event__promoter__name__icontains=search_form.cleaned_data[
                        "promoter"
                    ]
                )
            res = search_query.all()
            context["results"] = res
            return render(request, "../templates/search.html", context)
    return render(request, "../templates/search.html", context)


def get_roles(request):
    if request.method == "GET":
        opera_id = request.GET.get("opera")
        roles = (
            Role.objects.filter(opera__name__icontains=opera_id).values("name").all()
        )
        return JsonResponse(list(roles), safe=False)

@login_required
def travel(request):
    formset = {}
    date = request.GET.get("date")
    if request.method == "POST":
        form = TravelForm(request.POST)
        if form.is_valid():
            form.save()
            formset = TravelDataSet(request.POST, instance=form.instance)
            if formset.is_valid():
#                CalendarEvent.objects.filter(event=form.instance).delete()
                formset.save()
            return redirect("/")
    else:
        form = TravelForm()
        formset = inlineformset_factory(parent_model=Event, model=CalendarEvent, form=TravelDataSetForm, extra=1,)
    return render(
            request, "../templates/travel.html", {"form": form, "formset": formset, "start_date": date}
    )


@login_required
def edit_event(request):
    event_id = int(request.GET.get("id", 0))
    event = CalendarEvent.objects.get(pk=event_id)
    historyformset = {}
    if request.method == "GET":
        if event.event is None:
            form = OtherForm(instance=event)
            template = "../templates/other.html"
            formset = {}
        elif event.event.event_type == 3:
            form = TravelForm(instance=event.event)
            formset = TravelDataSet(instance=event.event)
            template = "../templates/travel.html"
        elif event.event.event_type == 4:
            template = "../templates/engagement.html"
            form = EngagementForm(instance=event.event)
            formset = EngagementDataSet(instance=event.event)
        return render(
            request,
            template,
            {"form": form, "formset": formset, "historyformset": historyformset},
        )
    else:
        if event.event is None:
            form = OtherForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                return redirect("/")
        if event.event.event_type == 3:
            form = TravelForm(request.POST, instance=event.event)
            if form.is_valid():
                form.save()
                formset = TravelDataSet(request.POST, instance=event.event)
                if formset.is_valid():
                    all_forms = CalendarEvent.objects.filter(event=event.event).all()
                    for form in formset:
                        if form.is_valid():
                            form.save()
                            all_forms = all_forms.exclude(pk=form.instance.pk)
                    all_forms.delete()
        elif event.event.event_type == 4:
            form = EngagementForm(request.POST, instance=event.event)
            if form.is_valid():
                form.save()
                formset = EngagementDataSet(request.POST, instance=event.event)
                if formset.is_valid():
                    all_forms = CalendarEvent.objects.filter(event=event.event).all()
                    for form in formset:
                        if form.is_valid():
                            form.save()
                            all_forms = all_forms.exclude(pk=form.instance.pk)
                    all_forms.delete()
        return redirect("/")


def get_artists_from_session(user):
    last_session = LastSession.objects.get(user=user)
    if last_session is not None:
        artists = (
            Artist.objects.filter(id__in=last_session.artists)
            .values_list("id", "name")
            .all()
        )
    else:
        artists = Artist.objects.values_list("id", "name").all()
    return artists


def create_context(form, request):
    start_date = request.GET.get("date")
    all_cities = City.objects.only("name").all()
    context = {
        "form": form,
        "start_date": start_date,
        "all_cities": all_cities,
        "artists": get_artists_from_session(request.user),
    }
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
            season_start = datetime.datetime.strptime(
                request.POST[f"event_start_{i}"], "%Y-%m-%d"
            ).date()
            season_end = request.POST[f"event_end_{i}"]
            if season_end == "":
                season_end = season_start
            else:
                season_end = datetime.datetime.strptime(season_end, "%Y-%m-%d").date()
            event_type = request.POST.get(f"event_type_{i}", None)
            periods.append((season_start, season_end, event_type))
    happening = form.cleaned_data.pop("happening")
    artist = Artist.objects.get(id=form.cleaned_data.pop("artist"))
    return periods, happening, artist


@login_required
def other_event(request):
    if request.method == "POST":
        form = OtherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = OtherForm(initial={"date": request.GET.get("date")})
    return render(
        request,
        "../templates/other.html",
        {"form": form, "date": request.GET.get("date")},
    )

@login_required
def engagement(request):
    formset = {}
    date = request.GET.get("date")
    if request.method == "POST":
        form = EngagementForm(request.POST)
        if form.is_valid():
            form.save()
            formset = EngagementDataSet(request.POST, instance=form.instance)
            if formset.is_valid():
                formset.save()
            return redirect("/")
    else:
        form = EngagementForm()
        formset = inlineformset_factory(parent_model=Event, model=CalendarEvent, form=EngagementDataSetForm, extra=1,)
    return render(
            request, "../templates/engagement.html", {"form": form, "formset": formset, "start_date": date}
    )


@login_required
def contact_list(request):
    if request.method == "POST":
        query = request.POST.get("query", "")
        contacts = Contact.objects.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(position__icontains=query)
            | Q(organization__name__icontains=query)
        ).all()
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

@login_required
def edit_contact(request, contact_id):
    contact = Contact.objects.get(id=contact_id)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect("/contact_list")
    else:
        form = ContactForm(instance=contact)
    return render(request, "../templates/contact.html", {"form": form})
