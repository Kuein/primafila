# Generated by Django 4.1.7 on 2023-03-07 13:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0008_delete_eventhistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="conact_number",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_received",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_received_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_requested",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_requested_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_sent_artist",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_sent_artist_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_sent_promoter",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_sent_promoter_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_signed_artist",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_signed_artist_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_signed_promoter",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="contract_signed_promoter_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="invoice_sent",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="invoice_sent_details",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
