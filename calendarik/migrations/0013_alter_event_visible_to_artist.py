# Generated by Django 4.1.7 on 2023-03-11 15:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0012_alter_event_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="visible_to_artist",
            field=models.BooleanField(default=True),
        ),
    ]
