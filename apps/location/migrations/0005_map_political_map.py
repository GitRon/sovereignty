# Generated by Django 2.1.3 on 2018-12-24 13:33

import apps.location.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0004_auto_20181223_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='political_map',
            field=models.ImageField(blank=True, null=True, upload_to=apps.location.models.upload_location),
        ),
    ]
