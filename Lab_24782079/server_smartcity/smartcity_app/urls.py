from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model

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
    path('api/', include('api.urls')), # Jalur API punyamu yang lama tetap aman
    path('bikin-admin-rahasia/', buat_admin_rahasia), # Jalur pemicu baru kita
]