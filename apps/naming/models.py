from django.db import models

import apps.dynasty.settings as ps
from apps.naming.managers import PersonNameManager


class PersonName(models.Model):
    name = models.CharField(max_length=20)
    gender = models.PositiveSmallIntegerField(choices=ps.GENDER_CHOICES)

    objects = PersonNameManager()

    class Meta:
        unique_together = ('name', 'gender')
        ordering = ('name',)

    def __str__(self):
        return self.name


class LocationNamePrefix(models.Model):
    text = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.text


class LocationNamePostfix(models.Model):
    text = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.text
