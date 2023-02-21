# Generated by Django 4.1.7 on 2023-02-21 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendarik', '0004_remove_calendarevent_profile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendarevent',
            name='status',
            field=models.CharField(blank=True, choices=[('travel', 'Travel'), ('hotel', 'Hotel'), ('other', 'Other'), ('engagement', 'Engagement')], max_length=100, null=True),
        ),
    ]
