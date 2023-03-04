from django import forms
from .models import Event, EventHistory, Contact, CalendarEvent, Promoter, City, Role, Opera
from django.forms import modelformset_factory, inlineformset_factory

class Datalist(forms.widgets.Select):
    input_type = 'text'
    template_name = 'datalist.html'
    option_template_name = 'datalist_option.html'
    add_id_index = False
    checked_attribute = {'selected': True}
    option_inherits_attrs = False

#    def format_value(self, value):
#        if value is None:
#            return ''
#        model = self.choices.queryset.model
#        if model == City:
#            city, _ = City.objects.get_or_create(name=value)
#            self.choices.queryset = City.objects.values_list("id", "name").all()
#            value = city.id
#            return str(city.id)
#        return str(value)


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
        city, _ = City.objects.get_or_create(name=value)
        return city

class OperaChoiceField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = Opera.objects.values_list("id", "name").all()

    def clean(self, value):
        value = super().clean(value)
        opera, _ = Opera.objects.get_or_create(name=value)
        return opera

class RoleChoiceField(forms.CharField):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.widget = Datalist(attrs={"class": "form-control"})
            self.widget.choices = Role.objects.values_list("id", "name").all()
    
        def clean(self, value):
            value = super().clean(value)
            role, _ = Role.objects.get_or_create(name=value)
            return role

class PromoterChoiceField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = Datalist(attrs={"class": "form-control"})
        self.widget.choices = Promoter.objects.values_list("id", "name").all()

    def clean(self, value):
        value = super().clean(value)
        promoter, _ = Promoter.objects.get_or_create(name=value)
        return promoter

class TravelForm(forms.ModelForm):
    city = CityChoiceField(widget=Datalist(attrs={"class": "form-control"}))

    class Meta:
        model = Event
        fields = (
            "city",
            "artist",
            "inner_notes",
            "artist_notes",
            "inner_files",
            "artist_files",
        )
        widgets = {
            "city": Datalist(attrs={"class": "form-control"}),
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
                attrs={"type": "date", "class": "form-control"}
            ),
            "note": forms.TextInput(attrs={"class": "form-control"}),
            "engagement_type": forms.Select(attrs={"class": "form-control"}),
            "end_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }


class EngagementHistoryForm(forms.ModelForm):
    class Meta:
        model = EventHistory
        fields = "__all__"


class EngagementForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "city",
            "artist",
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
            "visible_to_artist",
            "another_agency",
        )
        widgets = {
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "artist": forms.Select(attrs={"class": "form-control"}),
            "inner_notes": forms.Textarea(attrs={"class": "form-control"}),
            "artist_notes": forms.Textarea(attrs={"class": "form-control"}),
            "inner_files": forms.FileInput(attrs={"class": "form-control"}),
            "artist_files": forms.FileInput(attrs={"class": "form-control"}),
            "opera": forms.Select(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "promoter": forms.Select(attrs={"class": "form-control"}),
            "contact": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "fee": forms.NumberInput(attrs={"class": "form-control"}),
            "visible_to_artist": forms.CheckboxInput(attrs={"class": "form-control"}),
            "another_agency": forms.CheckboxInput(attrs={"class": "form-control"}),
        }


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
    parent_model=Event, model=CalendarEvent, form=EngagementDataSetForm,
)
EngagementHistorySet = inlineformset_factory(
    parent_model=Event, model=EventHistory, form=EngagementHistoryForm,
)

