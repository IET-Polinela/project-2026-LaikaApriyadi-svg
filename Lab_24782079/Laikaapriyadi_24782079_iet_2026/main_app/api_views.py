from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer
from .permissions import IsOwnerAndDraftOrReadOnly
from django.db.models import Q

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_permissions(self):
        """
        Menentukan izin berdasarkan aksi yang dilakukan. 
        """
        # Jika user ingin edit (update) atau hapus (destroy) [cite: 58]
        if self.action in ['update', 'partial_update', 'destroy']:
            # Wajib login DAN lolos pengecekan Satpam Draft [cite: 59]
            return [permissions.IsAuthenticated(), IsOwnerAndDraftOrReadOnly()]
        
        # Untuk aksi lainnya (List, Detail, Create), cukup login saja [cite: 60]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Mengisi field 'reporter' secara otomatis dari user yang sedang login. [cite: 51, 61, 62]
        """
        # Ini mencegah user 'menembak' nama reporter lain via JSON [cite: 62, 75]
        serializer.save(reporter=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Report.objects.all() # Admin lihat semua
        # Citizen cuma lihat laporan yang sudah REPORTED atau DRAFT milik sendiri
        return Report.objects.filter(Q(status='REPORTED') | Q(reporter=user)) 