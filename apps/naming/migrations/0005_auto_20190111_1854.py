# Generated by Django 2.1.3 on 2019-01-11 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('naming', '0004_auto_20190106_1905'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LocationNamePostfix',
            new_name='LocationNameSuffix',
        ),
        migrations.AlterModelOptions(
            name='personname',
            options={'ordering': ('name',)},
        ),
    ]
