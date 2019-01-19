from django.db import models

from apps.messaging.managers import MessageManager


class EventMessage(models.Model):
    TYPE_OK = 1
    TYPE_YES_NO = 2
    TYPE_CHOICES = (
        (TYPE_OK, "Acknowledge-Message"),
        (TYPE_YES_NO, "Yes-No-Message"),
    )

    title = models.CharField(max_length=50)
    text = models.TextField(null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    done = models.BooleanField(default=False)
    created_in_year = models.PositiveIntegerField()

    # System attributes
    savegame = models.ForeignKey('account.Savegame', related_name='messages', on_delete=models.CASCADE)

    objects = MessageManager()

    def __str__(self):
        return self.title
