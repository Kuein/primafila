# Generated by Django 4.1.7 on 2023-03-06 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0005_rename_title_opera_name_remove_opera_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name="event",
            name="accomodation_type",
        ),
        migrations.RemoveField(
            model_name="event",
            name="travel_payment_type",
        ),
        migrations.AddField(
            model_name="calendarevent",
            name="fee",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="accomodation_fee",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="accomodation_fee_type",
            field=models.IntegerField(
                blank=True, choices=[(1, "Full"), (2, "Limit")], null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="calculated_fee",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="event",
            name="dirigent",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="individual_fee",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="event",
            name="regie",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="event",
            name="total_fee",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="travel_fee",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="travel_fee_type",
            field=models.IntegerField(
                blank=True, choices=[(1, "Full"), (2, "Limit")], null=True
            ),
        ),
        migrations.AddField(
            model_name="calendarevent",
            name="currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="calendarik.currency",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="accomodation_fee_currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="accomodation_fee_currency",
                to="calendarik.currency",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="fee_currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="calendarik.currency",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="travel_fee_currency",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="travel_fee_currency",
                to="calendarik.currency",
            ),
        ),
    ]
