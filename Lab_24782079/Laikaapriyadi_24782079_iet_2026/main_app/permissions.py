from rest_framework import permissions

class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):
    """
    Izin kustom: Pemilik hanya bisa edit/delete jika status adalah 'DRAFT'.
    Pengguna lain hanya bisa melihat (Read-Only).
    """
    def has_object_permission(self, request, view, obj):
        # 1. Izinkan akses jika request adalah metode 'aman' (GET, HEAD, OPTIONS) 
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Cek apakah user yang login adalah pemilik (reporter) [cite: 48, 49]
        # DAN cek apakah status laporan masih 'DRAFT' [cite: 49]
        return obj.reporter == request.user and obj.status == 'DRAFT'