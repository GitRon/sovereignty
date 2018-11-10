from django.db import models

"""
TODO:
    - name parts need to be m/w/x
"""


class PersonNamePrefix(models.Model):
    text = models.CharField(max_length=20)

    def __str__(self):
        return self.text


class PersonNamePostfix(models.Model):
    text = models.CharField(max_length=20)

    def __str__(self):
        return self.text
