from django.contrib import admin
from .models import Event, Contact, CalendarEvent, Artist, Opera, Role, Promoter, LastSession, City, Currency, ArtistFiles, InnerFiles

# Register your models here.adm
admin.site.register(Event)
admin.site.register(Contact)
admin.site.register(CalendarEvent)
admin.site.register(Artist)
admin.site.register(Opera)
admin.site.register(Role)
admin.site.register(Promoter)
admin.site.register(LastSession)
admin.site.register(City)
admin.site.register(Currency)
admin.site.register(ArtistFiles)
admin.site.register(InnerFiles)

