# Generated by Django 2.1.5 on 2019-01-19 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_savegame_playing_as'),
        ('messaging', '0005_message_savegame'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Message',
            new_name='EventMessage',
        ),
    ]
