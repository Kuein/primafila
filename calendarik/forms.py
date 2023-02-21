from django import forms
from .models import Event, Contact


class CalendarEventForm(forms.Form):
    # array of dates or periods
    event_start = forms.DateField()
    event_end = forms.DateField(required=False)
    event = forms.ModelChoiceField(required=False, queryset=Event.objects.all())
    contact = forms.ModelChoiceField(queryset=Contact.objects.all())
