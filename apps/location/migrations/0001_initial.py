# Generated by Django 2.1.3 on 2018-11-18 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('area_type', models.PositiveSmallIntegerField(choices=[(1, 'Fields'), (2, 'Montains'), (3, 'Swamp'), (4, 'Woods')])),
            ],
        ),
    ]
