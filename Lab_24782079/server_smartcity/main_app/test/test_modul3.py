from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()

# =============================================================================
# MODUL 3: PENGUJIAN ALUR KERJA & ATURAN BISNIS STATUS LAPORAN
# =============================================================================

class WorkflowStateTests(APITestCase):
    """
    Kelas pengujian untuk alur kerja dan transisi status laporan via REST API.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_wf', password='TestPass123!', is_admin=False
        )

        self.laporan_draft = Report.objects.create(
            title='Lampu Kampus Mati',
            category='Fasilitas Umum',
            description='Lampu di depan gedung rektorat tidak menyala.',
            location='Gedung Rektorat',
            status='DRAFT',
            reporter=self.warga,
        )

        self.laporan_reported = Report.objects.create(
            title='Saluran Air Tersumbat',
            category='Infrastruktur',
            description='Saluran air di samping kantin tersumbat.',
            location='Kantin Polinela',
            status='REPORTED',
            reporter=self.warga,
        )

        self.laporan_resolved = Report.objects.create(
            title='AC Rusak di Lab',
            category='Fasilitas Umum',
            description='AC di Lab CPS 1 sudah diperbaiki.',
            location='Lab CPS 1',
            status='RESOLVED',
            reporter=self.warga,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-01: Warga Mengajukan Laporan (DRAFT → REPORTED)
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_01_warga_mengajukan_draf_menjadi_reported(self):
        """
        [WF-01] Warga menekan tombol ajukan laporan pada data berstatus DRAFT.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_draft.pk}/'
        payload = {
            'title': self.laporan_draft.title,
            'category': self.laporan_draft.category,
            'description': self.laporan_draft.description,
            'location': self.laporan_draft.location,
            'status': 'REPORTED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Pengajuan draf ke REPORTED seharusnya berhasil (HTTP 200)"
        )

        self.laporan_draft.refresh_from_db()
        self.assertEqual(
            self.laporan_draft.status,
            'REPORTED',
            "Status laporan di database harus berubah menjadi 'REPORTED'"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-02: Warga Tidak Bisa Mengubah Konten Laporan yang Sudah REPORTED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_02_tidak_bisa_edit_laporan_yang_sudah_reported(self):
        """
        [WF-02] Warga mencoba memperbarui teks konten laporan yang sudah
        berstatus REPORTED via API.

        CATATAN: Asumsi HTTP 403 berdasarkan docstring asli (permission
        IsOwnerAndDraftOrReadOnly). Perlu dikonfirmasi ulang setelah isi
        main_app/permissions.py dibagikan — cek apakah pengecekan itu
        dilakukan di has_object_permission (403) atau di get_queryset (404).
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_reported.pk}/'
        payload = {
            'title': 'Judul Diubah Paksa',
            'category': self.laporan_reported.category,
            'description': self.laporan_reported.description,
            'location': self.laporan_reported.location,
            'status': 'REPORTED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.laporan_reported.refresh_from_db()
        self.assertEqual(self.laporan_reported.title, 'Saluran Air Tersumbat')

    # ─────────────────────────────────────────────────────────────────────────
    # WF-05: Laporan RESOLVED Bersifat Read-Only
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_05_laporan_resolved_tidak_bisa_diubah(self):
        """
        [WF-05] Pengguna mencoba mengirimkan modifikasi data pada laporan
        yang sudah berstatus RESOLVED.

        CATATAN: Sama seperti WF-02, asumsi HTTP 403 — perlu dikonfirmasi
        setelah main_app/permissions.py dibagikan.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_resolved.pk}/'
        payload = {
            'title': 'Coba Ubah Laporan Resolved',
            'category': self.laporan_resolved.category,
            'description': self.laporan_resolved.description,
            'location': self.laporan_resolved.location,
            'status': 'RESOLVED',
        }

        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# =============================================================================
# MODUL 3b: PENGUJIAN ADMIN PORTAL — TRANSISI STATUS
# =============================================================================

class AdminWorkflowTests(TestCase):
    """
    Kelas pengujian untuk portal admin (Django monolithic views).
    """

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_portal',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

        self.laporan_reported = Report.objects.create(
            title='Jalan Rusak di Blok C',
            category='Infrastruktur',
            description='Jalan berlubang parah di area parkir Blok C.',
            location='Blok C Polinela',
            status='REPORTED',
            reporter=self.admin,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-03: Admin Mengubah Status REPORTED menjadi VERIFIED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_03_admin_mengubah_status_reported_ke_verified(self):
        """
        [WF-03] Admin mengubah status laporan dari REPORTED menjadi VERIFIED
        melalui UI Portal Admin (url name: 'update_status').
        """
        self.client.login(username='admin_portal', password='AdminPass123!')

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.laporan_reported.pk}),
            {'status': 'VERIFIED'}
        )

        self.laporan_reported.refresh_from_db()
        self.assertEqual(
            self.laporan_reported.status,
            'VERIFIED',
            "Status seharusnya berhasil berubah dari REPORTED ke VERIFIED"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-04: Tidak Ada Transisi Langsung ke RESOLVED dari REPORTED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_04_tidak_ada_transisi_langsung_ke_resolved_dari_reported(self):
        """
        [WF-04] Memastikan laporan REPORTED tidak bisa langsung dipindah
        ke RESOLVED (harus lewat VERIFIED -> IN_PROGRESS terlebih dahulu),
        sesuai ALLOWED_TRANSITIONS di ReportUpdateStatusView.
        """
        self.client.login(username='admin_portal', password='AdminPass123!')

        response = self.client.post(
            reverse('update_status', kwargs={'pk': self.laporan_reported.pk}),
            {'status': 'RESOLVED'}
        )

        self.laporan_reported.refresh_from_db()
        self.assertEqual(
            self.laporan_reported.status,
            'REPORTED',
            "Status TIDAK boleh berubah karena RESOLVED bukan transisi valid dari REPORTED"
        )