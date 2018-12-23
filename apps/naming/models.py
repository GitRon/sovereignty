from django.db import models

import apps.person.settings as ps


class PersonName(models.Model):
    name = models.CharField(max_length=20)
    gender = models.PositiveSmallIntegerField(choices=ps.GENDER_CHOICES)

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
