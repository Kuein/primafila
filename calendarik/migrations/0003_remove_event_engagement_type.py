# Generated by Django 4.1.7 on 2023-03-04 11:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0002_alter_lastsession_artists"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="engagement_type",
        ),
    ]
