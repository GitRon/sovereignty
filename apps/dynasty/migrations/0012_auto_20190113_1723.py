# Generated by Django 2.1.5 on 2019-01-13 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0005_auto_20190111_1854'),
        ('dynasty', '0011_auto_20190106_1857'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='name',
        ),
        migrations.AddField(
            model_name='person',
            name='first_name',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='first_name_persons', to='naming.PersonName'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='middle_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='middle_name_persons', to='naming.PersonName'),
        ),
    ]
