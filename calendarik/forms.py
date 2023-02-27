from django import forms
from .models import Event, Contact, EVENT_TYPES, EVENT_STATUS, ENGAGEMENT_TYPE, TRAVEL_PAY_TYPE, ACCOMODATION_TYPE, Artist, Promoter, TRAVEL_TYPE
from .models import City, Opera, Role


class SearchForm(forms.Form):
    role = forms.CharField(required=False)
    opera = forms.CharField(required=False)
    promoter = forms.CharField(required=False)


class OtherForm(forms.Form):
#    event_start = forms.DateField(required=False)
#    event_end = forms.DateField(required=False)
    artist = forms.ChoiceField(choices=Artist.objects.values_list("id", "name").all())
    inner_notes = forms.CharField(required=False)
    artist_notes = forms.CharField(required=False)
    happening = forms.BooleanField(required=False)
    inner_files = forms.FileField(required=False)
    artist_files = forms.FileField(required=False)


class TravelForm(OtherForm):
    # Travel_to Travel_from Hotel
    travel_type = forms.ChoiceField(required=False, choices=TRAVEL_TYPE)

class EngagementForm(OtherForm):
    opera = forms.ModelChoiceField(queryset=Opera.objects.all())
    role = forms.ModelChoiceField(queryset=Role.objects.all())
    promoter = forms.ModelChoiceField(queryset=Promoter.objects.all())
    engagement_type = forms.CharField(required=False)
    status = forms.ChoiceField(choices=EVENT_STATUS)
    fee = forms.DecimalField(max_digits=6, decimal_places=2)
    role = forms.CharField(max_length=100)
    visible_to_artist = forms.BooleanField(required=False)
    another_agency = forms.BooleanField(required=False)
