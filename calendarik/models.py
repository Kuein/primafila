from django.db import models
from django.contrib.auth.models import User
from cities_light.models import City
from django.db.models.signals import post_save
from django.dispatch import receiver


class Contact(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    calendar = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

#    def __str__(self):
#        if self.user:
#            return self.user.username
#        else:
#            return "No user"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Contact.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.contact.save()


#class Contact(models.Model):
#    first_name = models.CharField(max_length=100)
#    last_name = models.CharField(max_length=100)
#    email = models.EmailField(max_length=100, null=True, blank=True)
#    phone = models.CharField(max_length=100, null=True, blank=True)
#    organization = models.CharField(max_length=100, null=True, blank=True)
#    calendar = models.BooleanField(default=False)
#
#    def __str__(self):
#        return f"{self.first_name} {self.last_name}"

EVENT_TYPES = ((1, "Travel"), (2, "Hotel"), (3, "Other"), (4, "Engagement"))
EVENT_STATUS = (("request", "Request"), ("confirmed", "Confirmed"), ("contract", "Contract"), ("happening", "Happening"), ("inner", "Inner"))

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class ArtistFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file = models.FileField(upload_to="artist_files")


class InnerFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file = models.FileField(upload_to="inner_files")

class Artist(models.Model):
    name = models.CharField(max_length=100)

class CalendarEvent(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    artist_notes = models.TextField(null=True, blank=True)
    inner_notes = models.TextField(null=True, blank=True)
    event_type = models.IntegerField(choices=EVENT_TYPES, default=3)
    status = models.CharField(max_length=100, choices=EVENT_STATUS, null=True, blank=True)
    fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    promoter = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="promoter_contact")
    visible_to_artist = models.BooleanField(default=False)
    another_agency = models.BooleanField(default=False)

    def __str__(self):
        if self.another_agency:
            return f"{self.city} - {self.title} a.A"
        return f"{self.city} - {self.title}"

    def save(self, *arg, **kwargs):
        if not self.title:
            if self.another_agency:
                self.title = f"{self.city} - {self.title} a.A"
            else:
                self.title = f"{self.city} - {self.title}"
        if self.visible_to_artist:
            self.status = "inner"
        super().save(*arg, **kwargs)

