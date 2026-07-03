from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

User = get_user_model()

# =============================================================================
# MODUL 1: PENGUJIAN OTORISASI & MANAJEMEN SESI
# =============================================================================

class AuthenticationTests(APITestCase):
    """
    Kelas pengujian untuk modul Otorisasi & Manajemen Sesi.
    """

    def setUp(self):
        self.warga = User.objects.create_user(
            username='warga_test',
            password='Password123!',
            is_admin=False,
        )

        self.admin = User.objects.create_user(
            username='admin_test',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # AUTH-01: Login Warga dengan Kredensial Valid
    # ─────────────────────────────────────────────────────────────────────────
    def test_AUTH_01_login_warga_dengan_kredensial_valid(self):
        """
        [AUTH-01] Login Warga dengan kredensial valid pada endpoint token.
        """
        url = reverse('token_obtain_pair')

        payload = {
            'username': 'warga_test',
            'password': 'Password123!',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Login dengan kredensial valid seharusnya mengembalikan HTTP 200"
        )

        self.assertIn(
            'access',
            response.data,
            "Respons login harus mengandung field 'access' (JWT Access Token)"
        )

        self.assertIn(
            'refresh',
            response.data,
            "Respons login harus mengandung field 'refresh' (JWT Refresh Token)"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # AUTH-02: Login Warga dengan Password Salah
    # ─────────────────────────────────────────────────────────────────────────
    def test_AUTH_02_login_warga_dengan_password_salah(self):
        """
        [AUTH-02] Login Warga dengan kata sandi (password) salah.
        """
        url = reverse('token_obtain_pair')

        payload = {
            'username': 'warga_test',
            'password': 'passwordSALAH',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Login dengan password salah seharusnya mengembalikan HTTP 401"
        )

        self.assertNotIn(
            'access',
            response.data,
            "Tidak boleh ada token yang dikeluarkan untuk kredensial invalid"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # AUTH-03: Warga Biasa Mengakses Endpoint/Halaman Admin
    # ─────────────────────────────────────────────────────────────────────────
    def test_AUTH_03_warga_tidak_bisa_akses_halaman_admin(self):
        """
        [AUTH-03] Pengguna berstatus Warga biasa (is_admin=False) mencoba
        mengakses URL endpoint/halaman portal Admin (dashboard).

        SKENARIO:
            Warga biasa yang sudah login mencoba mengakses halaman dashboard
            yang hanya dapat diakses oleh admin.

        HASIL YANG DIHARAPKAN:
            Sistem menolak permintaan dengan HTTP 302 (redirect ke report_list).
        """
        self.client.login(username='warga_test', password='Password123!')

        response = self.client.get(reverse('dashboard_main'))

        self.assertEqual(
            response.status_code,
            302,
            "Warga biasa yang mengakses dashboard admin harus di-redirect (302)"
        )