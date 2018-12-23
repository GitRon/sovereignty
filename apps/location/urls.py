from apps.location import views
from django.conf.urls import url

urlpatterns = [

    url(r'^show-map$', views.ShowMapDashboard.as_view(), name='show-map-view'),

]
