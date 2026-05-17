from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny] # Akses publik untuk sementara
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    
def get_queryset(self):
    user = self.request.user
    if user.is_staff:
        return Report.objects.all() # Admin lihat semua
    # Citizen cuma lihat laporan yang sudah REPORTED atau DRAFT milik sendiri
    return Report.objects.filter(Q(status='REPORTED') | Q(reporter=user)) 