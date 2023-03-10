# Generated by Django 4.1.7 on 2023-03-11 15:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0011_event_probengeld_fee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("request", "Request"),
                    ("confirmed", "Confirmed"),
                    ("contract", "Contract"),
                ],
                default="normal",
                max_length=100,
                null=True,
            ),
        ),
    ]
