from django.urls import path

from apps.dynasty import views

urlpatterns = [

    path(r'', views.DynastyDashboard.as_view(), name='dashboard-view'),
    path(r'person/detail/<int:pk>', views.PersonDetail.as_view(), name='person-detail-view'),

]
