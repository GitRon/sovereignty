from django.db import models

import apps.person.settings as ps


class Person(models.Model):
    name = models.CharField(max_length=50)
    nobility = models.BooleanField(default=True)
    from_location = models.CharField(max_length=50, blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=ps.GENDER_CHOICES)
    birth_year = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} von {self.from_location}'
