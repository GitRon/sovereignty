# Generated by Django 2.1.7 on 2019-02-16 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('location', '0023_auto_20190119_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('done', models.BooleanField(default=False)),
                ('losses_attacker', models.PositiveIntegerField()),
                ('losses_defender', models.PositiveIntegerField()),
                ('attacker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attacker_in_battles', to='location.County')),
                ('defender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defender_in_battles', to='location.County')),
            ],
        ),
        migrations.CreateModel(
            name='BattlefieldTile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coordinate_x', models.IntegerField(db_index=True)),
                ('coordinate_y', models.IntegerField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Regiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('current_men', models.PositiveIntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='RegimentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('attack_value', models.PositiveSmallIntegerField()),
                ('defense_value', models.PositiveSmallIntegerField()),
                ('costs', models.PositiveSmallIntegerField()),
                ('morale', models.PositiveSmallIntegerField()),
                ('steps_per_turn', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='RegimentUpgrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75)),
                ('bonus_attack', models.PositiveSmallIntegerField()),
                ('bonus_defense', models.PositiveSmallIntegerField()),
                ('bonus_morale', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='regiment',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regiments', to='military.RegimentType'),
        ),
        migrations.AddField(
            model_name='regiment',
            name='upgrades',
            field=models.ManyToManyField(related_name='regiments', to='military.RegimentUpgrade'),
        ),
    ]
