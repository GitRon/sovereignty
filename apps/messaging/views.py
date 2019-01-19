from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from apps.messaging.models import EventMessage


class MarkAsRead(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        message = get_object_or_404(EventMessage, pk=self.kwargs.pop('pk'))
        message.done = True
        message.save()

        return redirect('account:dashboard-view')
