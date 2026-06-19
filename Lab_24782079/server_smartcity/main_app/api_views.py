from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination  # <--- WAJIB TAMBAHKAN INI
from .models import Report
from .serializers import ReportSerializer
from .permissions import IsOwnerAndDraftOrReadOnly
from django.db.models import Q

# 1. Aktivasi PageNumberPagination dengan ukuran page size = 10 (Figure 1)
class ReportPagination(PageNumberPagination):
    page_size = 10  # Maksimal 10 item per halaman
    page_size_query_param = 'page_size'
    max_page_size = 100

# @extend_schema(exclude=True)
class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    pagination_class = ReportPagination  # <--- DAFTARKAN PAGINASI DI SINI

    def get_permissions(self):
        """
        Menentukan izin berdasarkan aksi yang dilakukan. 
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerAndDraftOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Mengisi field 'reporter' secara otomatis dari user yang sedang login.
        """
        serializer.save(reporter=self.request.user)

    def get_queryset(self):
        user = self.request.user
        
        # 2. Mekanisme sorting berdasarkan tanggal pembaruan terkini (Figure 1)
        queryset = Report.objects.all().order_by('-updated_at')
        
        # Jika user adalah Staff/Admin, berikan akses penuh melihat semua data
        if user.is_staff:
            return queryset

        # 3. Server Side Filtering: Membaca parameter tab dari URL (Figure 1)
        # API dipanggil dalam format: /api/report/?tab=${tab}
        tab = self.request.query_params.get('tab', None)
        
        if tab == 'my_reports':
            # Jika ?tab=my_reports -> kembalikan hanya laporan milik user yang sedang login (Figure 1)[cite: 2]
            queryset = queryset.filter(reporter=user)
        elif tab == 'feed':
            # Jika ?tab=feed -> kembalikan laporan dari warga lain yang statusnya BUKAN DRAFT (Figure 1)[cite: 2]
            queryset = queryset.filter(~Q(reporter=user) & ~Q(status='DRAFT'))
        else:
            # Kondisi default: Mengembalikan laporan publik atau draf milik sendiri (Figure 1)[cite: 2]
            queryset = queryset.filter(~Q(status='DRAFT') | Q(status='DRAFT', reporter=user))
            
        return queryset