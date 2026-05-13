from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    # Menggunakan SerializerMethodField untuk menyembunyikan identitas asli
    reporter = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'category', 'description', 
            'location', 'status', 'reporter', 
            'created_at', 'updated_at'
        ]

    # Mengembalikan string statis agar pelapor tetap anonim di API
    def get_reporter(self, obj):
        return "Warga Anonim"