# Generated by Django 3.0.6 on 2020-08-01 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('castle', '0004_auto_20200801_1647'),
    ]

    operations = [
        migrations.RenameField(
            model_name='castleupgrade',
            old_name='costs',
            new_name='building_cost',
        ),
        migrations.AddField(
            model_name='castleupgrade',
            name='maintenance_cost',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
