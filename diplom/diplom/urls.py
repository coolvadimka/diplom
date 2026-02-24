from django.contrib import admin
from django.urls import path, include
from discrete_math import views
from discrete_math.views import page_not_found
from diplom import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('discrete_math.urls')),
    path('users/', include('users.urls', namespace='users')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = page_not_found