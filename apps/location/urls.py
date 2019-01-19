from django.urls import path

from apps.location import views

urlpatterns = [

    path('show-map', views.ShowMapDashboard.as_view(), name='show-map-view'),
    path('map-dot-details/<int:map_id>/<int:x>/<int:y>', views.MapDotDetail.as_view(), name='map-dot-detail-ajax'),
    path('county/my-county', views.MyCounty.as_view(), name='my-county-view'),

]
