from django.urls import path

from apps.castle import views

urlpatterns = [

    path(r'overview', views.CastleOverviewView.as_view(), name='overview-view'),

]
