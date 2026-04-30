from django.urls import path
from .views import DashboardMainView, dashboard_api_data

urlpatterns = [
    path('', DashboardMainView.as_view(), name='dashboard_main'), # Halaman utama dashboard
    path('api/data/', dashboard_api_data, name='dashboard_api_data'), # API untuk Chart.js
]