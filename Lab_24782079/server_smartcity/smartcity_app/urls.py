from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Manajemen user kustom
    path('accounts/', include('usermanagement_24782079.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('main_app.urls')),
    path('dashboard/', include('dashboard_24782079.urls')),

    # API
    path('api/', include('main_app.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]