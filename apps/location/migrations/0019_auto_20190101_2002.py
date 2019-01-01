# Generated by Django 2.1.3 on 2019-01-01 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0018_county_savegame'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='savegame',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='maps', to='account.Savegame'),
        ),
    ]
