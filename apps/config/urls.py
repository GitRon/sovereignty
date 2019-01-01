from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom routes
    path('', include(('apps.account.urls', 'account'), namespace='account')),
    path('location/', include(('apps.location.urls', 'location'), namespace='location')),
    path('person/', include(('apps.person.urls', 'person'), namespace='person')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
