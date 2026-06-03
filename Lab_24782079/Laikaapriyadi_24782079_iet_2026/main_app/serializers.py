from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    # 1. Menggunakan SerializerMethodField untuk menyembunyikan identitas asli
    reporter = serializers.SerializerMethodField()
    
    # 2. Tambahkan field is_owner sesuai instruksi Lab 12 (Figure 2)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'category', 'description', 
            'location', 'status', 'reporter', 'is_owner', # <--- Pastikan 'is_owner' didaftarkan di sini
            'created_at', 'updated_at'
        ]

    # Mengembalikan string statis agar pelapor tetap anonim di API
    def get_reporter(self, obj):
        return "Warga Anonim"

    # Tambahkan fungsi ini untuk memeriksa jika request.user merupakan pelapor (Figure 2)
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            # Mengembalikan True jika user yang sedang login adalah pemilik laporan
            return obj.reporter == request.user
        return False