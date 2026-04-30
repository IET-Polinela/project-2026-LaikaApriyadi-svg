from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Report
from django.shortcuts import render
from .models import Report  # Pastikan model Report diimport jika ingin menampilkan total laporan

def home_view(request):
    # Mengambil jumlah laporan untuk ditampilkan sebagai statistik kecil
    total_laporan = Report.objects.count()
    return render(request, 'home.html', {'total': total_laporan})

# 1. MIXIN UNTUK OTORISASI
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

    def handle_no_permission(self):
        messages.error(self.request, "Akses Ditolak: Fitur ini hanya untuk Admin!")
        return redirect('report_list')

# 2. VIEW DAFTAR LAPORAN
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

# 3. VIEW DETAIL
class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

# 4. VIEW TAMBAH LAPORAN
class ReportCreateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan baru berhasil dibuat oleh Admin!"

# 5. VIEW UPDATE LAPORAN
class ReportUpdateView(LoginRequiredMixin, AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location', 'status']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

# 6. VIEW HAPUS LAPORAN
class ReportDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Laporan telah dihapus!")
        return super().delete(request, *args, **kwargs)

# 7. VIEW UPDATE STATUS
class ReportUpdateStatusView(LoginRequiredMixin, AdminRequiredMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        report.status = new_status
        report.save()
        messages.success(request, f"Status diperbarui menjadi {new_status}")
        return redirect('report_list')

# --- TAMBAHAN UNTUK MENU NAVBAR (ABOUT & CONTACT) ---

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def home_view(request):
    total_laporan = Report.objects.count()
    return render(request, 'home.html', {'total': total_laporan})

def home_view(request):
    # Logika sederhana untuk menampilkan halaman home
    return render(request, 'home.html')