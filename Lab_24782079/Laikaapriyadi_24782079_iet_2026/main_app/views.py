from django.shortcuts import render, redirect
from .models import Report
from .forms import ReportForm

# Fungsi Tambah Laporan (Create)
def add_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ReportForm()
    return render(request, 'main_app/add_report.html', {'form': form})

# Fungsi Daftar Laporan (Read)
def report_list(request):
    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'main_app/report_list.html', {'reports': reports})