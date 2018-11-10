from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom routes
    path('person/', include(('apps.person.urls', 'person'), namespace='person')),
]
