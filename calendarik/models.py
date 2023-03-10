from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Promoter(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    organization = models.ForeignKey(
        Promoter, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class Currency(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class LastSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date = models.DateField(null=True, blank=True)
    artists = ArrayField(
        base_field=models.IntegerField(null=True, blank=True), null=True, blank=True
    )

    def __str__(self):
        return f"{self.user}"


class Artist(models.Model):
    name = models.CharField(max_length=100)
    calendar = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Opera(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100)
    opera = models.ForeignKey(Opera, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


EVENT_TYPES = ((1, "Travel"), (2, "Hotel"), (3, "Other"), (4, "Engagement"))
EVENT_STATUS = (
    ("request", "Request"),
    ("confirmed", "Confirmed"),
    ("contract", "Contract"),
    ("happening", "Happening"),
    ("inner", "Inner"),
    ("normal", "Normal"),
)
TRAVEL_TYPE = ((1, "Travel to"), (2, "Travel from"), (3, "Hotel"))
ENGAGEMENT_TYPE = ((1, "Premiere"), (2, "Performance"), (3, "Rehearsal"))
TRAVEL_PAY_TYPE = ((1, "Full"), (2, "Limit"))


class Event(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    artist_notes = models.TextField(null=True, blank=True)
    inner_notes = models.TextField(null=True, blank=True)
    event_type = models.IntegerField(choices=EVENT_TYPES, default=3)
    # travel fields
    travel_type = models.IntegerField(choices=TRAVEL_TYPE, null=True, blank=True)
    # other fields
    # engagement fields
    opera = models.ForeignKey(Opera, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True
    )
    regie = models.CharField(max_length=100, null=True, blank=True)
    dirigent = models.CharField(max_length=100, null=True, blank=True)
    promoter = models.ForeignKey(
        Promoter,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="promoter",
    )
    status = models.CharField(
        max_length=100, choices=EVENT_STATUS, null=True, blank=True, default="normal"
    )
    visible_to_artist = models.BooleanField(default=False)
    another_agency = models.BooleanField(default=False)
    last_edited = models.CharField(max_length=100, null=True, blank=True)

    fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fee_currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)

    travel_fee_type = models.IntegerField(choices=TRAVEL_PAY_TYPE, null=True, blank=True)
    travel_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    accomodation_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    accomodation_fee_type = models.IntegerField(choices=TRAVEL_PAY_TYPE, null=True, blank=True)

    calculated_fee = models.BooleanField(default=True)
    individual_fee = models.BooleanField(default=False)

    total_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # statuses and history
    contract_requested = models.BooleanField(default=False)
    contract_requested_details = models.CharField(max_length=100, null=True, blank=True)
    contract_received = models.BooleanField(default=False)
    contract_received_details = models.CharField(max_length=100, null=True, blank=True)
    contract_sent_artist = models.BooleanField(default=False)
    contract_sent_artist_details = models.CharField(max_length=100, null=True, blank=True)
    contract_signed_artist = models.BooleanField(default=False)
    contract_signed_artist_details = models.CharField(max_length=100, null=True, blank=True)
    contract_sent_promoter = models.BooleanField(default=False)
    contract_sent_promoter_details = models.CharField(max_length=100, null=True, blank=True)
    contract_signed_promoter = models.BooleanField(default=False)
    contract_signed_promoter_details = models.CharField(max_length=100, null=True, blank=True)
    invoice_sent = models.BooleanField(default=False)
    invoice_sent_details = models.CharField(max_length=100, null=True, blank=True)
    contract_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *arg, **kwargs):
        if self.event_type == 2:
            if self.travel_type in (1, "1"):
                self.title = f"✈️ {self.city}"
            elif self.travel_type in (2, "2"):
                self.title = f"{self.city} ✈️"
            elif self.travel_type in (3, "3"):
                self.title = f"🏠 {self.city}"
        if not self.title:
            self.title = f"{self.city} - {self.opera}"
        if not self.title.endswith("a.A.") and self.another_agency:
            self.title = f"{self.title} a.A."
        if self.title.endswith("a.A.") and not self.another_agency:
            self.title = self.title[:-4]
#        if self.visible_to_artist or not self.status:
#            self.status = "inner"
        super().save(*arg, **kwargs)


class ArtistFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file = models.FileField(upload_to="artist_files")

    def __str__(self):
        return self.file.name


class InnerFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file = models.FileField(upload_to="inner_files")

    def __str__(self):
        return self.file.name

def get_sentinel_user():
    return User.objects.get_or_create(username="deleted")[0]


class CalendarEvent(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    #    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    engagement_type = models.IntegerField(
        choices=ENGAGEMENT_TYPE, null=True, blank=True
    )
    fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    travel_type = models.IntegerField(choices=TRAVEL_TYPE, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    happend = models.BooleanField(default=False)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return "No title"

    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.start_date
        if self.event is None:
            self.title = f"{self.note:30}"
        if self.travel_type in (1, "1"):
            self.title = f"✈️ {self.event.city}"
        elif self.travel_type in (2, "2"):
            self.title = f"{self.event.city} ✈️"
        elif self.travel_type in (3, "3"):
            self.title = f"🏠 {self.event.city}"
        if self.event and self.event.title and not self.title:
            self.title = self.event.title
        if self.engagement_type == 1:
            self.title = self.title.upper()
        super().save(*args, **kwargs)
