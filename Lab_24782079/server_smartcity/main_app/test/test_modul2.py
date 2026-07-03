from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()

# =============================================================================
# MODUL 2: PENGUJIAN VISIBILITAS DATA & PRIVASI PELAPOR
# =============================================================================

class PrivacyAndDataHidingTests(APITestCase):
    """
    Kelas pengujian untuk modul Visibilitas Data & Privasi Pelapor.
    """

    def setUp(self):
        self.warga_a = User.objects.create_user(
            username='warga_a', password='TestPass123!', is_admin=False
        )
        self.warga_b = User.objects.create_user(
            username='warga_b', password='TestPass123!', is_admin=False
        )

        self.draft_milik_b = Report.objects.create(
            title='Draf Rahasia Warga B',
            category='Infrastruktur',
            description='Ini adalah draf yang belum diajukan.',
            location='Lokasi Rahasia',
            status='DRAFT',
            reporter=self.warga_b,
        )

        self.laporan_publik_a = Report.objects.create(
            title='Jalan Berlubang di Depan Kampus',
            category='Infrastruktur',
            description='Ada lubang besar yang membahayakan pengendara.',
            location='Jl. Soekarno Hatta',
            status='REPORTED',
            reporter=self.warga_a,
        )

        self.laporan_publik_b = Report.objects.create(
            title='Sampah Menumpuk di Trotoar',
            category='Kebersihan',
            description='Sampah tidak diangkut selama seminggu.',
            location='Jl. Gatot Subroto',
            status='REPORTED',
            reporter=self.warga_b,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PRIV-01: Feed Kota Menyembunyikan Identitas Pelapor
    # ─────────────────────────────────────────────────────────────────────────
    def test_PRIV_01_feed_kota_menyembunyikan_identitas_reporter(self):
        """
        [PRIV-01] Mengakses endpoint Feed Kota (GET /api/report/?tab=feed).
        """
        self.client.force_authenticate(user=self.warga_a)

        response = self.client.get('/api/report/?tab=feed')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', [])
        self.assertTrue(
            len(results) > 0,
            "Feed kota seharusnya memiliki minimal 1 laporan"
        )

        for laporan in results:
            self.assertEqual(
                laporan['reporter'],
                'Warga Anonim',
                f"Laporan '{laporan['title']}' seharusnya menampilkan reporter "
                f"sebagai 'Warga Anonim', tetapi menampilkan '{laporan['reporter']}'"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # PRIV-02: Laporan Saya Menampilkan Nama Asli Pelapor
    # ─────────────────────────────────────────────────────────────────────────
    def test_PRIV_02_laporan_saya_menampilkan_nama_asli(self):
        """
        [PRIV-02] Mengakses endpoint Laporan Saya (GET /api/report/?tab=my_reports).
        """
        self.client.force_authenticate(user=self.warga_a)

        response = self.client.get('/api/report/?tab=my_reports')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get('results', [])
        self.assertTrue(len(results) > 0, "Harus ada laporan milik Warga A")

        for laporan in results:
            self.assertEqual(
                laporan['reporter_name'],
                'warga_a',
                f"Pada tab 'my_reports', reporter_name seharusnya menampilkan "
                f"username asli 'warga_a', bukan '{laporan['reporter_name']}'"
            )

    # ─────────────────────────────────────────────────────────────────────────
    # PRIV-03: Warga A Tidak Bisa Membaca Draf Milik Warga B
    # ─────────────────────────────────────────────────────────────────────────
    def test_PRIV_03_tidak_bisa_baca_draf_orang_lain(self):
        """
        [PRIV-03] Warga A mencoba membaca detail data laporan berstatus DRAFT
        milik Warga B melalui parameter ID API.

        HASIL YANG DIHARAPKAN:
            HTTP 404 Not Found — draf disembunyikan lewat get_queryset()
            (bukan reporter=user, bukan status non-DRAFT).
        """
        self.client.force_authenticate(user=self.warga_a)

        url = f'/api/report/{self.draft_milik_b.pk}/'
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Draf milik warga lain harus tersembunyi (404), bukan 403"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # PRIV-04: Warga A Tidak Bisa Memodifikasi Draf Milik Warga B
    # ─────────────────────────────────────────────────────────────────────────
    def test_PRIV_04_tidak_bisa_modifikasi_draf_orang_lain(self):
        """
        [PRIV-04] Warga A mencoba memanipulasi data draf milik Warga B
        menggunakan metode HTTP PUT via API.

        HASIL YANG DIHARAPKAN:
            HTTP 404 Not Found dan data draf Warga B tidak berubah sama sekali.
        """
        self.client.force_authenticate(user=self.warga_a)

        url = f'/api/report/{self.draft_milik_b.pk}/'
        payload = {
            'title': 'Draft Diubah Paksa oleh Warga A',
            'category': self.draft_milik_b.category,
            'description': self.draft_milik_b.description,
            'location': self.draft_milik_b.location,
            'status': 'REPORTED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.draft_milik_b.refresh_from_db()
        self.assertEqual(
            self.draft_milik_b.title,
            'Draf Rahasia Warga B',
            "Data draf Warga B tidak boleh berubah sama sekali"
        )