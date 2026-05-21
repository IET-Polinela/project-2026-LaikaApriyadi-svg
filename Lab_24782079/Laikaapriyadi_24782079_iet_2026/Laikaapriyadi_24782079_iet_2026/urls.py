from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Letakkan usermanagement DI ATAS auth.urls agar logout kustom kita yang dipakai
    path('accounts/', include('usermanagement_24782079.urls')), 
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('main_app.urls')),
    path('dashboard/', include('dashboard_24782079.urls')),
    path('api/', include('main_app.api_urls')), # Hubungkan ke api_urls.py
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]