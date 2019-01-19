from django.urls import path

from apps.account import views

urlpatterns = [

    path('', views.Dashboard.as_view(), name='dashboard-view'),
    path('menu', views.Menu.as_view(), name='menu-view'),
    path('menu/load/savegame/<int:savegame_id>', views.Menu.as_view(), name='menu-load-savegame-view'),
    path('finish-year', views.FinishYear.as_view(), name='finish-year-view'),

]
