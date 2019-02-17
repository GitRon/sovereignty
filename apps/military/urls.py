from django.urls import path

from apps.military import views

urlpatterns = [

    path('', views.OverviewView.as_view(), name='overview-view'),
    path('regiment/<int:pk>/training/<int:type_id>', views.RegimentTrainingView.as_view(),
         name='regiment-training-view'),
    path('regiment/<int:pk>', views.RegimentDetailView.as_view(), name='regiment-detail-view'),

    path('battle/current', views.BattleView.as_view(), name='battle-view'),

]
