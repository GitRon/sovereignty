from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom routes
    path('location/', include(('apps.location.urls', 'location'), namespace='location')),
    path('person/', include(('apps.person.urls', 'person'), namespace='person')),
]
