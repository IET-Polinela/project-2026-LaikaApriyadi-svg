from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Report

# --- 1. HOME & DASHBOARD VIEWS ---

def home_view(request):
    total_laporan = Report.objects.count()
    return render(request, 'home.html', {'total': total_laporan})

@login_required
def dashboard_view(request):
    # Mengambil jumlah laporan berdasarkan status untuk grafik lingkaran
    status_counts = Report.objects.values('status').annotate(total=Count('status'))
    
    # Inisialisasi dictionary status (pastikan key sesuai dengan pilihan di models.py)
    stats = {
        'DRAFT': 0, 
        'REPORTED': 0, 
        'VERIFIED': 0, 
        'IN_PROGRESS': 0, 
        'RESOLVED': 0
    }
    
    for item in status_counts:
        # Kita pakai .upper() untuk jaga-jaga jika di DB tersimpan huruf kecil
        status_name = item['status'].upper()
        if status_name in stats:
            stats[status_name] = item['total']

    # Mengambil data kategori untuk grafik batang
    category_qs = Report.objects.values('category').annotate(total=Count('category'))
    cat_labels = [item['category'] for item in category_qs]
    cat_values = [item['total'] for item in category_qs]

    context = {
        'draft': stats['DRAFT'],
        'reported': stats['REPORTED'],
        'verified': stats['VERIFIED'],
        'in_progress': stats['IN_PROGRESS'],
        'resolved': stats['RESOLVED'],
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'total_laporan': Report.objects.count(),
    }
    return render(request, 'dashboard.html', context)

# --- 2. MIXIN UNTUK OTORISASI ---

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Sesuaikan dengan field admin di model User lu (is_admin atau is_staff)
        return self.request.user.is_authenticated and (getattr(self.request.user, 'is_admin', False) or self.request.user.is_staff)

    def handle_no_permission(self):
        messages.error(self.request, "Akses Ditolak: Fitur ini hanya untuk Admin!")
        return redirect('report_list')

# --- 3. CRUD REPORT VIEWS ---

class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

class ReportCreateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan baru berhasil dibuat!"

class ReportUpdateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location', 'status']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

class ReportDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Laporan telah dihapus!")
        return super().delete(request, *args, **kwargs)

class ReportUpdateStatusView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        report.status = new_status
        report.save()
        messages.success(request, f"Status diperbarui menjadi {new_status}")
        return redirect('report_list')

# --- 4. NAVBAR VIEWS ---

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')