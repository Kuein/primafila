from django import forms
from .models import (
    Event,
    Contact,
    CalendarEvent,
    Promoter,
    City,
    Role,
    Opera,
)
from django.forms import inlineformset_factory


class Datalist(forms.widgets.Select):
    input_type = "text"
    template_name = "datalist.html"
    option_template_name = "datalist_option.html"
    add_id_index = False
    checked_attribute = {"selected": True}
    option_inherits_attrs = False


class SearchForm(forms.Form):
    role = forms.CharField(required=False)
    opera = forms.CharField(required=False)
    promoter = forms.CharField(required=False)


class OtherForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ("start_date", "note")
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "note": forms.TextInput(attrs={"class": "form-control"}),
        }


class TravelDataSetForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ("start_date", "note", "travel_type", "end_date")
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control period-start"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control period-end"}
            ),
            "note": forms.TextInput(attrs={"class": "form-control"}),
            "travel_type": forms.Select(attrs={"class": "form-control"}),
        }


class CityChoiceField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = City.objects.values_list("id", "name").all()

    def clean(self, value):
        value = super().clean(value)
        if value == "":
            return None
        city, _ = City.objects.get_or_create(name=value)
        return city


class OperaChoiceField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = Opera.objects.values_list("id", "name").all()

    def clean(self, value):
        value = super().clean(value)
        if value == "":
            return None
        opera, _ = Opera.objects.get_or_create(name=value)
        return opera


class RoleChoiceField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = Role.objects.values_list("id", "name").all()

    def clean(self, value, opera=None):
        value = super().clean(value)
        if value == "":
            return None
        if opera:
            opera, _ = Opera.objects.get_or_create(name=opera)
            role, _ = Role.objects.get_or_create(name=value, opera=opera)
        else:
            role = Role.objects.filter(name=value).first()
        return role


#
class PromoterChoiceField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = Promoter.objects.values_list("id", "name").all()

    def clean(self, value):
        value = super().clean(value)
        if value == "":
            return None
        promoter, _ = Promoter.objects.get_or_create(name=value)
        return promoter


class ContactChoiceField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = Promoter.objects.values_list("id", "name").all()

    def clean(self, value, prom=None):
        value = super().clean(value)
        if value == "":
            return None
        if prom:
            promoter, _ = Promoter.objects.get_or_create(name=prom)
            contact, _ = Contact.objects.get_or_create(
                name=value, organization=promoter
            )
        else:
            contact, _ = Contact.objects.get_or_create(name=value)
        return contact


class TravelForm(forms.ModelForm):
    city = CityChoiceField(widget=Datalist(attrs={"class": "form-control"}))
    event_type = forms.IntegerField(widget=forms.HiddenInput(), initial=4)

    class Meta:
        model = Event
        fields = (
            "city",
            "event_type",
            "artist",
            "inner_notes",
            "artist_notes",
            "inner_files",
            "artist_files",
        )
        widgets = {
            "artist": forms.Select(attrs={"class": "form-control"}),
            "inner_notes": forms.Textarea(attrs={"class": "form-control"}),
            "artist_notes": forms.Textarea(attrs={"class": "form-control"}),
            "inner_files": forms.FileInput(attrs={"class": "form-control"}),
            "artist_files": forms.FileInput(attrs={"class": "form-control"}),
        }


class EngagementDataSetForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ("start_date", "note", "engagement_type", "end_date", "title")
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control period-start"}
            ),
            "note": forms.TextInput(attrs={"class": "form-control"}),
            "engagement_type": forms.Select(attrs={"class": "form-control"}),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control period-end"}
            ),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }


class EngagementForm(forms.ModelForm):
    city = CityChoiceField(
        widget=Datalist(attrs={"class": "form-control", "required": "True"}),
        required=False,
    )
    opera = OperaChoiceField(
            widget=Datalist(attrs={"class": "form-control"}), required=True
    )
    role = RoleChoiceField(
        widget=Datalist(attrs={"class": "form-control"}), required=False
    )
    promoter = PromoterChoiceField(
        widget=Datalist(attrs={"class": "form-control"}), required=False
    )
    contact = ContactChoiceField(
        widget=Datalist(attrs={"class": "form-control"}), required=False
    )
    event_type = forms.IntegerField(widget=forms.HiddenInput(), initial=4)

    class Meta:
        model = Event
        fields = (
            "city",
            "artist",
            "event_type",
            "inner_notes",
            "artist_notes",
            "inner_files",
            "artist_files",
            "opera",
            "role",
            "promoter",
            "contact",
            "status",
            "fee",
            "title",
            "visible_to_artist",
            "another_agency",
        )
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "artist": forms.Select(attrs={"class": "form-control", "required": True}),
            "inner_notes": forms.Textarea(attrs={"class": "form-control"}),
            "artist_notes": forms.Textarea(attrs={"class": "form-control"}),
            "inner_files": forms.FileInput(attrs={"class": "form-control"}),
            "artist_files": forms.FileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "visible_to_artist": forms.CheckboxInput(attrs={"class": "form-control"}),
            "another_agency": forms.CheckboxInput(attrs={"class": "form-control"}),
        }

    def clean(self, *args, **kwargs):
        self.fields["role"].clean(self.data["role"], self.data["opera"])
        self.fields["contact"].clean(self.data["contact"], self.data["promoter"])
        super().clean(*args, **kwargs)
        return self.cleaned_data


def update_create(name, model, parent_obj, parent_name):
    if parent_obj:
        obj, _ = model.objects.get_or_create(name=name, parent_name=parent_obj)
    else:
        obj, _ = model.objects.get_or_create(name=name)
    return obj


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "organization": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control"}),
            "position": forms.TextInput(attrs={"class": "form-control"}),
        }


TravelDataSet = inlineformset_factory(
    parent_model=Event, model=CalendarEvent, form=TravelDataSetForm, extra=0
)
EngagementDataSet = inlineformset_factory(
    parent_model=Event,
    model=CalendarEvent,
    form=EngagementDataSetForm,
    extra=0,
)
