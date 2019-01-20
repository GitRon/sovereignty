from django.urls import path

from apps.dynasty import views

urlpatterns = [

    path(r'overview', views.DynastyOverviewView.as_view(), name='overview-view'),
    path(r'marriage', views.MarriageView.as_view(), name='marriage-view'),
    path(r'marriage/marrying/<int:other_person>', views.MarryingFormView.as_view(),
         name='marrying-form-view'),
    path(r'person/detail/<int:pk>', views.PersonDetail.as_view(), name='person-detail-view'),

]
