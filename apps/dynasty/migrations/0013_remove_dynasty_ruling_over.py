# Generated by Django 2.1.5 on 2019-01-13 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynasty', '0012_auto_20190113_1723'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dynasty',
            name='ruling_over',
        ),
    ]
