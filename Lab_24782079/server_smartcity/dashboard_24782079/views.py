from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
import json

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from main_app.models import Report

# ==========================================
# 1. HOME & DASHBOARD VIEWS
# ==========================================

def home_view(request):
    total_laporan = Report.objects.count()
    return render(request, 'home.html', {'total': total_laporan})


def _is_staff_or_admin(user):
    """Helper: cek apakah user adalah admin/staff (dipakai guard dashboard_view)."""
    return user.is_authenticated and (getattr(user, 'is_admin', False) or user.is_staff)


@login_required
def dashboard_view(request):
    # ---- GUARD: Hanya admin/staff yang boleh akses dashboard (AUTH-03) ----
    if not _is_staff_or_admin(request.user):
        messages.error(request, "Akses Ditolak: Halaman ini hanya untuk Admin!")
        return redirect('report_list')

    # --- A. Data untuk Grafik Status (Doughnut Chart) ---
    # Menghitung jumlah laporan per status
    status_counts = Report.objects.values('status').annotate(total=Count('status'))

    # Inisialisasi dictionary agar variabel di HTML (draft_count, dsb) tidak None
    stats = {
        'DRAFT': 0,
        'REPORTED': 0,
        'VERIFIED': 0,
        'IN_PROGRESS': 0,
        'RESOLVED': 0
    }

    for item in status_counts:
        # Ubah key jadi uppercase untuk mencocokkan stats dictionary
        s_key = item['status'].upper().replace(" ", "_")
        if s_key in stats:
            stats[s_key] = item['total']

    # --- B. Data untuk Grafik Kategori (Bar Chart) ---
    # HTML lu minta format: category_data -> loop: cat.category & cat.count
    category_data = list(Report.objects.values('category').annotate(count=Count('id')))
    status_labels = ['Draft', 'Reported', 'Verified', 'In Progress', 'Resolved']
    status_values = [
        stats['DRAFT'], stats['REPORTED'], stats['VERIFIED'], stats['IN_PROGRESS'], stats['RESOLVED']
    ]
    category_labels = [item['category'] for item in category_data]
    category_counts = [item['count'] for item in category_data]

    # --- C. Data untuk Tabel (Laporan Terbaru) ---
    # Mengambil 5 laporan terbaru berdasarkan status tertentu
    reported_list = Report.objects.filter(status='REPORTED').order_by('-id')[:5]
    resolved_list = Report.objects.filter(status='RESOLVED').order_by('-id')[:5]

    context = {
        # Sesuai variabel di dashboard/dashboard.html lu
        'draft_count': stats['DRAFT'],
        'reported_count': stats['REPORTED'],
        'verified_count': stats['VERIFIED'],
        'progress_count': stats['IN_PROGRESS'],
        'resolved_count': stats['RESOLVED'],

        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'category_labels_json': json.dumps(category_labels),
        'category_counts_json': json.dumps(category_counts),
        'reported_list': reported_list,
        'resolved_list': resolved_list,
        'total_laporan': Report.objects.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)

# ==========================================
# 2. MIXIN & AUTHENTICATION
# ==========================================

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Mengecek apakah user adalah admin/staff
        return self.request.user.is_authenticated and (getattr(self.request.user, 'is_admin', False) or self.request.user.is_staff)

    def handle_no_permission(self):
        messages.error(self.request, "Akses Ditolak: Fitur ini hanya untuk Admin!")
        return redirect('report_list')

# ==========================================
# 3. CRUD REPORT VIEWS (Web Interface)
# ==========================================

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

# ==========================================
# 4. NAVBAR & STATIC PAGES
# ==========================================

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')