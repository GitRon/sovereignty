from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom routes
    path('', include(('apps.account.urls', 'account'), namespace='account')),
    path('location/', include(('apps.location.urls', 'location'), namespace='location')),
    path('castle/', include(('apps.castle.urls', 'castle'), namespace='castle')),
    path('dynasty/', include(('apps.dynasty.urls', 'dynasty'), namespace='dynasty')),
    path('message/', include(('apps.messaging.urls', 'message'), namespace='message')),
    path('military/', include(('apps.military.urls', 'military'), namespace='military')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
