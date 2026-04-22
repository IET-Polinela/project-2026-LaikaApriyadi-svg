from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Letakkan usermanagement DI ATAS auth.urls agar logout kustom kita yang dipakai
    path('accounts/', include('usermanagement_24782079.urls')), 
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('main_app.urls')),
]