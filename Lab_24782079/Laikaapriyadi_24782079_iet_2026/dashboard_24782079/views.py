from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count
from main_app.models import Report

# View untuk menampilkan halaman HTML Dashboard [cite: 72]
class DashboardMainView(TemplateView):
    template_name = 'dashboard/dashboard.html'

# View khusus format JsonResponse untuk diolah JavaScript/Chart.js [cite: 73, 80]
def dashboard_api_data(request):
    # Menghitung distribusi status (persentase) [cite: 76, 92]
    status_stats = list(Report.objects.values('status').annotate(count=Count('status')))
    
    # Menghitung distribusi kategori [cite: 77]
    category_stats = list(Report.objects.values('category').annotate(count=Count('category')))
    
    # Mengambil data 5 laporan terbaru berstatus REPORTED dan RESOLVED [cite: 78-79]
    latest_reported = list(Report.objects.filter(status='REPORTED').order_by('-id')[:5].values())
    latest_resolved = list(Report.objects.filter(status='RESOLVED').order_by('-id')[:5].values())
    
    return JsonResponse({
        'status_stats': status_stats,
        'category_stats': category_stats,
        'latest_reported': latest_reported,
        'latest_resolved': latest_resolved
    })