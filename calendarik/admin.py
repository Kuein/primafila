from django.contrib import admin
from .models import Event, Contact, CalendarEvent

# Register your models here.adm
admin.site.register(Event)
admin.site.register(Contact)
admin.site.register(CalendarEvent)

