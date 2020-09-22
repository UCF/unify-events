# Generated by Django 3.1.1 on 2020-09-14 11:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0002_auto_20200914_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='admin_calendars', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='calendar',
            name='editors',
            field=models.ManyToManyField(blank=True, related_name='editor_calendars', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='calendar',
            name='subscriptions',
            field=models.ManyToManyField(blank=True, related_name='subscribed_calendars', to='events.Calendar'),
        ),
    ]
