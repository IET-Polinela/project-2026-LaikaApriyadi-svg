from django.urls import path
from . import views


urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
    path('report/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('report/add/', views.ReportCreateView.as_view(), name='report_create'),
    path('report/<int:pk>/edit/', views.ReportUpdateView.as_view(), name='report_update'),
    path('report/<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report_delete'),
    path('report/<int:pk>/update-status/', views.ReportUpdateStatusView.as_view(), name='update_status'),
]