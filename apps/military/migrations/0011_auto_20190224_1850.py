# Generated by Django 2.1.7 on 2019-02-24 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('military', '0010_auto_20190222_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='round',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='battle',
            name='losses_attacker',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='battle',
            name='losses_defender',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='battlefieldtile',
            name='regiment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='on_battlefield_tile', to='military.Regiment'),
        ),
    ]
