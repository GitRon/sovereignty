from apps.person import views
from django.conf.urls import url

urlpatterns = [

    url(r'^$', views.PersonDashboard.as_view(), name='dashboard-view'),

]
