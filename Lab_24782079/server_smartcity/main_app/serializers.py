from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    # 'reporter' SELALU disamarkan (PRIV-01)
    reporter = serializers.SerializerMethodField()
    # 'reporter_name' menampilkan nama asli HANYA untuk pemilik laporan (PRIV-02)
    reporter_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'title', 'category', 'description',
            'location', 'status', 'reporter', 'reporter_name', 'is_owner',
            'created_at', 'updated_at'
        ]

    def get_reporter(self, obj):
        # Selalu disamarkan menjadi "Warga Anonim", untuk SEMUA laporan (PRIV-01)
        return "Warga Anonim"

    def get_reporter_name(self, obj):
        # Nama asli hanya jika request.user adalah pemilik laporan (PRIV-02)
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            if obj.reporter == request.user:
                return obj.reporter.username
        return "Warga Anonim"

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.reporter == request.user
        return False