# Generated by Django 2.1.7 on 2019-02-16 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('military', '0004_regimenttype_default_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regimenttype',
            name='default_type',
            field=models.BooleanField(default=False, help_text='There can only be one default type.'),
        ),
    ]
