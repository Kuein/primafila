# Generated by Django 4.1.7 on 2023-02-27 15:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("calendarik", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="artist",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="calendarik.artist",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="artist_files",
            field=models.ManyToManyField(
                blank=True, related_name="artist_files", to="calendarik.artistfiles"
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="inner_files",
            field=models.ManyToManyField(
                blank=True, related_name="inner_files", to="calendarik.innerfiles"
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="title",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
