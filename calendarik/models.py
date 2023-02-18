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


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    artist_notes = models.TextField(null=True, blank=True)
    inner_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.city} - {self.title}"


class ArtistFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file = models.FileField(upload_to="artist_files")


class InnerFiles(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file = models.FileField(upload_to="inner_files")


class CalendarEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    promoter = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name="promoter_contact")
    period = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.period = self.date.strftime("%Y-%m")
        super().save(*args, **kwargs)
