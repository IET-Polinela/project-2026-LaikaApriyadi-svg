from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()

# =============================================================================
# MODUL 4: PENGUJIAN FUNGSIONALITAS DASAR & VALIDASI INPUT
# =============================================================================

class CRUDAndValidationTests(APITestCase):
    """
    Kelas pengujian untuk fungsionalitas dasar dan validasi input.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_crud', password='TestPass123!', is_admin=False
        )
        self.client.force_authenticate(user=self.warga)

    # ─────────────────────────────────────────────────────────────────────────
    # FT-01: Membuat Laporan Baru dengan Data Lengkap
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_01_buat_laporan_dengan_data_lengkap(self):
        """
        [FT-01] Mengirim data laporan baru dengan seluruh kolom (field)
        terisi lengkap dan benar.
        """
        url = reverse('report-list')
        payload = {
            'title': 'Laporan Lengkap Uji',
            'category': 'Infrastruktur',
            'description': 'Deskripsi laporan lengkap untuk pengujian.',
            'location': 'Jl. Testing No. 1',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Laporan dengan data lengkap seharusnya berhasil dibuat (201)"
        )
        self.assertTrue(
            Report.objects.filter(title='Laporan Lengkap Uji').exists()
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FT-02: Laporan Ditolak Jika Judul Kosong
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_02_ditolak_jika_judul_kosong(self):
        """
        [FT-02] Mengirim data pembuatan laporan baru dengan mengosongkan
        kolom judul (title).
        """
        url = reverse('report-list')
        payload = {
            'title': '',
            'category': 'Infrastruktur',
            'description': 'Deskripsi laporan tanpa judul.',
            'location': 'Jl. Testing No. 1',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    # ─────────────────────────────────────────────────────────────────────────
    # FT-03: Laporan Ditolak Jika Deskripsi Kosong
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_03_ditolak_jika_deskripsi_kosong(self):
        """
        [FT-03] Mengirim data pembuatan laporan baru dengan mengosongkan
        kolom deskripsi (description).
        """
        url = reverse('report-list')
        payload = {
            'title': 'Laporan Tanpa Deskripsi',
            'category': 'Infrastruktur',
            'description': '',
            'location': 'Jl. Testing No. 1',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)

    # ─────────────────────────────────────────────────────────────────────────
    # FT-04: Keamanan dari Serangan XSS (Cross-Site Scripting)
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_04_xss_script_disimpan_sebagai_string_literal(self):
        """
        [FT-04] Mengisi nilai deskripsi laporan menggunakan kode skrip
        injeksi jahat HTML: <script>alert('xss')</script>.
        """
        url = reverse('report-list')

        kode_xss = '<script>alert("xss")</script>'
        payload = {
            'title': 'Laporan XSS Test',
            'category': 'Keamanan',
            'description': kode_xss,
            'location': 'Lab Keamanan Siber',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Data dengan karakter HTML harus tetap diterima oleh API"
        )

        laporan = Report.objects.get(title='Laporan XSS Test')

        self.assertIn(
            'script',
            laporan.description.lower(),
            "Kode XSS harus tersimpan sebagai string literal di database"
        )