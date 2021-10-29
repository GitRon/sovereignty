from django.urls import path

from apps.location import views

urlpatterns = [

    path('show-map', views.ShowMapDashboard.as_view(), name='show-map-view'),
    path('map-dot-details/<int:map_id>/<int:x>/<int:y>', views.MapDotDetail.as_view(), name='map-dot-detail-ajax'),
    path('county/my-county/gold', views.MyCountyGoldView.as_view(), name='my-county-gold-view'),
    path('county/my-county/manpower', views.MyCountyManpowerView.as_view(), name='my-county-manpower-view'),
    path('county/my-county', views.MyCounty.as_view(), name='my-county-view'),
    path('county/my-provinces', views.MyProvincesView.as_view(), name='my-provinces-view'),
    path('county/province/<int:pk>/upgrade', views.ProvinceUpgradeView.as_view(), name='province-upgrade-view'),

]
