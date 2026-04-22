from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

# IMPORT BARU UNTUK LAB 6 [cite: 23, 42]
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Report

# 1. MIXIN UNTUK OTORISASI (Hanya Admin yang boleh CRUD) 
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Mengecek apakah user sudah login dan apakah is_admin bernilai True [cite: 42]
        return self.request.user.is_authenticated and self.request.user.is_admin

    def handle_no_permission(self):
        # Jika bukan admin mencoba akses, berikan pesan error dan lempar balik ke daftar [cite: 47, 59-60]
        messages.error(self.request, "Akses Ditolak: Fitur ini hanya untuk Admin!")
        return redirect('report_list')

# 2. VIEW DAFTAR LAPORAN (Bisa dilihat siapa saja, termasuk Citizen) [cite: 13, 44]
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

# 3. VIEW DETAIL (Bisa dilihat siapa saja yang sudah login) [cite: 44]
class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

# 4. VIEW TAMBAH LAPORAN (HANYA ADMIN) [cite: 14, 43]
class ReportCreateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan baru berhasil dibuat oleh Admin!"

# 5. VIEW UPDATE LAPORAN (HANYA ADMIN) [cite: 14, 43]
class ReportUpdateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location', 'status']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

# 6. VIEW HAPUS LAPORAN (HANYA ADMIN) [cite: 14, 43]
class ReportDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Laporan telah dihapus!")

# 7. VIEW UPDATE STATUS WORKFLOW (HANYA ADMIN) [cite: 42]
class ReportUpdateStatusView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        report.status = new_status
        report.save()
        messages.success(request, f"Status diperbarui menjadi {new_status}")
        return redirect('report_list')