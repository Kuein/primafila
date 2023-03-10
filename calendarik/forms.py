from django import forms
from .models import (
    Event,
    Contact,
    CalendarEvent,
    Promoter,
    City,
    Role,
    Opera,
    ArtistFiles,
    InnerFiles,
)
from django.forms import inlineformset_factory
from django.forms import ClearableFileInput


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
    event_type = forms.IntegerField(widget=forms.HiddenInput(), initial=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["city"].widget.choices = City.objects.values_list(
            "id", "name"
        ).all()

    class Meta:
        model = Event
        fields = (
            "city",
            "event_type",
            "artist",
            "inner_notes",
            "artist_notes",
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
        fields = (
            "start_date",
            "note",
            "engagement_type",
            "end_date",
            "title",
            "fee",
            "currency",
        )
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
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "currency": forms.Select(attrs={"class": "form-control"}),
            "happend": forms.CheckboxInput(attrs={"class": "form-control"}),
        }


class ArtistFileForm(forms.ModelForm):
    class Meta:
        model = ArtistFiles
        fields = ("file", "event")
        widgets = {
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }


class InnerFileForm(forms.ModelForm):
    class Meta:
        model = InnerFiles
        fields = ("file", "event")
        widgets = {
            "file": forms.FileInput(attrs={"class": "form-control"}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dirigent"].widget.choices = (
            Event.objects.distinct().values_list("dirigent", "dirigent").all()
        )
        self.fields["regie"].widget.choices = (
            Event.objects.distinct().values_list("regie", "regie").all()
        )
        self.fields["city"].widget.choices = City.objects.values_list(
            "id", "name"
        ).all()
        self.fields["opera"].widget.choices = Opera.objects.values_list(
            "id", "name"
        ).all()
        self.fields["role"].widget.choices = Role.objects.values_list(
            "id", "name"
        ).all()
        self.fields["promoter"].widget.choices = Promoter.objects.values_list(
            "id", "name"
        ).all()

    class Meta:
        model = Event
        fields = (
            "contract_requested",
            "contract_requested_details",
            "contract_received",
            "contract_received_details",
            "contract_sent_artist",
            "contract_sent_artist_details",
            "contract_signed_artist",
            "contract_signed_artist_details",
            "contract_sent_promoter",
            "contract_sent_promoter_details",
            "contract_signed_promoter",
            "contract_signed_promoter_details",
            "invoice_sent",
            "invoice_sent_details",
            "conact_number",
            "fee_currency",
            "calculated_fee",
            "individual_fee",
            "travel_fee_type",
            "travel_fee",
            "accomodation_fee",
            "accomodation_fee_type",
            "regie",
            "dirigent",
            "city",
            "artist",
            "event_type",
            "inner_notes",
            "artist_notes",
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
            "regie": Datalist(
                attrs={"class": "form-control"},
            ),
            "dirigent": Datalist(
                attrs={"class": "form-control"},
            ),
            "travel_fee_type": forms.Select(attrs={"class": "form-control"}),
            "accomodation_fee_type": forms.Select(attrs={"class": "form-control"}),
            "travel_fee": forms.NumberInput(attrs={"class": "form-control"}),
            "accomodation_fee": forms.NumberInput(attrs={"class": "form-control"}),
            "fee_currency": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "artist": forms.Select(attrs={"class": "form-control", "required": True}),
            "inner_notes": forms.Textarea(attrs={"class": "form-control", "rows": "4"}),
            "artist_notes": forms.Textarea(
                attrs={"class": "form-control", "rows": "4"}
            ),
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

ArtistFileFormset = inlineformset_factory(
    parent_model=Event, model=ArtistFiles, form=ArtistFileForm, extra=0
)
InnerFileFormset = inlineformset_factory(
    parent_model=Event, model=InnerFiles, form=InnerFileForm, extra=0
)
