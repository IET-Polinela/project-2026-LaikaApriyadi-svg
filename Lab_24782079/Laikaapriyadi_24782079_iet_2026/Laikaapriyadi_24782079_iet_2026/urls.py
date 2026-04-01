from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')), # Memastikan semua rute main_app terbaca [cite: 25, 46]
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
]