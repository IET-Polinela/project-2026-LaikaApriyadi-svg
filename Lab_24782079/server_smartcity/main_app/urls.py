from django.urls import path
from . import views

urlpatterns = [
    # 1. HALAMAN UTAMA (Landing Page) - Sekarang ini yang paling atas
    path('', views.home_view, name='home_page'), 
    
    # 2. DAFTAR LAPORAN (Sekarang pindah ke /reports/)
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    
    # 3. CRUD LAPORAN
    path('report/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('report/add/', views.ReportCreateView.as_view(), name='report_create'),
    path('report/<int:pk>/edit/', views.ReportUpdateView.as_view(), name='report_update'),
    path('report/<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report_delete'),
    
    # 4. WORKFLOW ADMIN (Update Status)
    path('report/<int:pk>/update-status/', views.ReportUpdateStatusView.as_view(), name='update_status'),
    
    # 5. HALAMAN STATIS
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]