from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
# Import Model dan Form
from main_app.models import Report
from .forms import UniversalSignUpForm

# 1. VIEW LOGIN
class MyLoginView(LoginView):
    def form_valid(self, form):
        username = form.get_user().username
        messages.success(self.request, f"Selamat datang kembali, {username}! Anda berhasil masuk.")
        return super().form_valid(form)

# 2. VIEW LOGOUT
class MyLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "Anda telah berhasil keluar dari sistem.")
        return super().dispatch(request, *args, **kwargs)

# 3. VIEW DAFTAR (SIGNUP) - LOGIKA PERBAIKAN STATUS DI SINI
class SignUpView(CreateView):
    form_class = UniversalSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        role_choice = form.cleaned_data.get('is_admin_choice')
        
        if role_choice == 'True':
            # Jika pilih Admin
            user.is_admin = True
            user.is_staff = True  # Memberikan centang pada IS MEMBER
        else:
            # Jika pilih Citizen
            user.is_admin = False
            user.is_staff = False # Memberikan silang pada IS MEMBER
            
        user.save()
        messages.success(self.request, f"Akun {user.username} berhasil dibuat sebagai { 'Admin' if user.is_admin else 'Citizen' }!")
        return super().form_valid(form)

# 4. MIXIN OTORISASI
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin

    def handle_no_permission(self):
        messages.error(self.request, "Akses Ditolak: Fitur ini hanya untuk Admin!")
        return redirect('report_list')

# --- VIEW UNTUK MAIN APP (LAPORAN) ---

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
    success_message = "Laporan baru berhasil dibuat oleh Admin!"

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