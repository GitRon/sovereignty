# Generated by Django 2.1.3 on 2019-01-06 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dynasty', '0008_auto_20190106_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trait',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Alcoholic'), (2, 'Cruel'), (3, 'Sodomist'), (4, 'Tiny'), (5, 'Giant'), (6, 'Strategist'), (7, 'Religious Zeal'), (8, 'Benevolent')]),
        ),
    ]
