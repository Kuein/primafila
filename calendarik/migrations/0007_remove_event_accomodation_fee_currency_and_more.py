# Generated by Django 4.1.7 on 2023-03-07 12:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0006_currency_remove_event_accomodation_type_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="accomodation_fee_currency",
        ),
        migrations.RemoveField(
            model_name="event",
            name="artist_files",
        ),
        migrations.RemoveField(
            model_name="event",
            name="inner_files",
        ),
        migrations.RemoveField(
            model_name="event",
            name="travel_fee_currency",
        ),
    ]
