from django.urls import path

from apps.messaging import views

urlpatterns = [

    path('<int:pk>/mark-as-read', views.MarkAsRead.as_view(), name='mark-as-read-view'),

]
