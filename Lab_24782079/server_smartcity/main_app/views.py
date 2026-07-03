from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import JsonResponse
import json
from .models import Report

# --- 1. HOME & DASHBOARD VIEWS ---

def home_view(request):
    total_laporan = Report.objects.count()
    return render(request, 'main_app/home.html', {'total': total_laporan})


def _is_staff_or_admin(user):
    """Helper: cek apakah user adalah admin/staff."""
    return user.is_authenticated and (getattr(user, 'is_admin', False) or user.is_staff)


@login_required
def dashboard_view(request):
    # ---- GUARD: Hanya admin/staff yang boleh akses dashboard (AUTH-03) ----
    if not _is_staff_or_admin(request.user):
        messages.error(request, "Akses Ditolak: Halaman ini hanya untuk Admin!")
        return redirect('report_list')

    # Mengambil jumlah laporan berdasarkan status untuk grafik lingkaran
    status_counts = Report.objects.values('status').annotate(total=Count('status'))

    stats = {
        'DRAFT': 0,
        'REPORTED': 0,
        'VERIFIED': 0,
        'IN_PROGRESS': 0,
        'RESOLVED': 0
    }

    for item in status_counts:
        status_name = item['status'].upper()
        if status_name in stats:
            stats[status_name] = item['total']

    # Mengambil data kategori untuk grafik batang
    category_qs = Report.objects.values('category').annotate(total=Count('category'))
    cat_labels = [item['category'] for item in category_qs]
    cat_values = [item['total'] for item in category_qs]

    # Data tabel: laporan terbaru per status (dibutuhkan template dashboard.html)
    reported_list = Report.objects.filter(status='REPORTED').order_by('-id')[:5]
    resolved_list = Report.objects.filter(status='RESOLVED').order_by('-id')[:5]

    status_labels = ['Draft', 'Reported', 'Verified', 'In Progress', 'Resolved']
    status_values = [
        stats['DRAFT'], stats['REPORTED'], stats['VERIFIED'], stats['IN_PROGRESS'], stats['RESOLVED']
    ]

    context = {
        'draft': stats['DRAFT'],
        'reported': stats['REPORTED'],
        'verified': stats['VERIFIED'],
        'in_progress': stats['IN_PROGRESS'],
        'resolved': stats['RESOLVED'],
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'total_laporan': Report.objects.count(),

        # Field tambahan yang dipakai template dashboard.html (chart & tabel)
        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'category_labels_json': json.dumps(cat_labels),
        'category_counts_json': json.dumps(cat_values),
        'reported_list': reported_list,
        'resolved_list': resolved_list,
    }
    return render(request, 'dashboard.html', context)


# --- 1b. LIVE SEARCH ENDPOINT (AJAX) ---

def report_search(request):
    """
    Endpoint pencarian laporan untuk fitur Live Search di report_list.html.
    Hanya admin/staff yang boleh akses. Tidak memakai @login_required agar
    pengguna unauthenticated mendapat 403 (bukan redirect 302 ke login).
    """
    if not _is_staff_or_admin(request.user):
        return JsonResponse({'detail': 'Akses ditolak.'}, status=403)

    query = request.GET.get('q', '')
    reports = Report.objects.filter(title__icontains=query) if query else Report.objects.all()

    results = [
        {
            'id': r.id,
            'title': r.title,
            'category': r.category,
            'location': r.location,
            'status': r.status,
        }
        for r in reports
    ]

    return JsonResponse({'results': results})


# --- 1c. DETAIL LAPORAN VIA API NON-DRF (dipakai test_addtional coverage) ---

def report_detail_api(request, pk):
    """
    Endpoint detail laporan sederhana (non-DRF). get_object_or_404 otomatis
    melempar Http404 jika id tidak ditemukan.
    """
    report = get_object_or_404(Report, pk=pk)
    data = {
        'id': report.id,
        'title': report.title,
        'category': report.category,
        'description': report.description,
        'location': report.location,
        'status': report.status,
    }
    return JsonResponse(data)


# --- 2. MIXIN UNTUK OTORISASI ---

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (getattr(self.request.user, 'is_admin', False) or self.request.user.is_staff)

    def handle_no_permission(self):
        messages.error(self.request, "Akses Ditolak: Fitur ini hanya untuk Admin!")
        return redirect('report_list')


class OwnerRequiredMixin:
    """
    Dipakai bersama AdminRequiredMixin (setelah cek admin/staff lolos).
    Memastikan hanya reporter (pemilik) laporan yang boleh melakukan
    update/delete. Admin lain yang bukan pemilik akan mendapat
    PermissionDenied (403), bukan redirect.
    """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.reporter != self.request.user:
            raise PermissionDenied("Anda bukan pemilik laporan ini.")
        return obj

# --- 3. CRUD REPORT VIEWS ---

class ReportListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

class ReportDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

class ReportCreateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan baru berhasil dibuat!"

class ReportUpdateView(LoginRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location', 'status']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

class ReportDeleteView(LoginRequiredMixin, AdminRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()  # akan raise PermissionDenied jika bukan pemilik
        messages.warning(self.request, "Laporan telah dihapus!")
        return super().delete(request, *args, **kwargs)


class ReportUpdateStatusView(LoginRequiredMixin, AdminRequiredMixin, View):
    # Aturan transisi status (state machine) — WF-04
    ALLOWED_TRANSITIONS = {
        'REPORTED': ['VERIFIED'],
        'VERIFIED': ['IN_PROGRESS'],
        'IN_PROGRESS': ['RESOLVED'],
    }

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')

        allowed = self.ALLOWED_TRANSITIONS.get(report.status, [])
        if new_status not in allowed:
            messages.error(
                request,
                f"Transisi status dari {report.status} ke {new_status} tidak diizinkan."
            )
            return redirect('report_list')

        report.status = new_status
        report.save()
        messages.success(request, f"Status diperbarui menjadi {new_status}")
        return redirect('report_list')

# --- 4. NAVBAR VIEWS ---

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')