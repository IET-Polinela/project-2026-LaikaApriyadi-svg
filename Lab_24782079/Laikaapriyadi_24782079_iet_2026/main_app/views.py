from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Report

# View untuk daftar laporan
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html'
    context_object_name = 'reports'

# View untuk DETAIL laporan (Ini yang error tadi)
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'

# View untuk buat laporan
class ReportCreateView(SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil ditambahkan!"

# View untuk edit laporan
class ReportUpdateView(SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/report_form.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

# View untuk hapus laporan
class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, "Laporan telah dihapus!")
        return super().delete(request, *args, **kwargs)

# View untuk update status (Workflow)
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        report.status = new_status
        report.save()
        messages.success(request, f"Status laporan diubah menjadi {new_status}")
        return redirect('report_list')