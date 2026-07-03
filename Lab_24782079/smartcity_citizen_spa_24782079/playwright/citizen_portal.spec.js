// =============================================================================
// FILE: citizen_portal.spec.js — E2E Test Suite Playwright
// =============================================================================
// CATATAN PENYESUAIAN (oleh mahasiswa, NPM 24782079):
//   File ini adalah file resmi dari dosen. HANYA bagian konfigurasi
//   (BASE_URL, kredensial test) yang disesuaikan agar cocok dengan environment
//   project (port Django 2479, akun admin12/123). Seluruh logika test,
//   assertion, dan alur skenario TIDAK diubah sama sekali dari versi asli.
// =============================================================================
//
// CARA MENJALANKAN:
//   1. Pastikan server Django backend aktif:
//      > cd server_smartcity
//      > python manage.py runserver 2479
//
//   2. Jalankan semua test:
//      > npx playwright test
//
//   3. Untuk mode visual (interaktif):
//      > npx playwright test --ui
//
//   4. Untuk menjalankan test tertentu:
//      > npx playwright test tests/e2e/citizen_portal.spec.js
//
//   5. Untuk mode headed (melihat browser):
//      > npx playwright test --headed
//
// PRASYARAT:
//   - npm init playwright@latest  (jika belum diinisialisasi)
//   - Server backend Django harus berjalan di http://127.0.0.1:2479
//   - SPA Citizen Portal harus bisa diakses (via Live Server / file:// / http-server)
//
// ARSITEKTUR APLIKASI:
//   - SPA Citizen Portal: Single Page Application berbasis hash-routing (#login, #register, #dashboard)
//   - Admin Portal: Server-side rendered Django templates (login, dashboard, report list)
//   - API Backend: Django REST Framework + SimpleJWT (token-based auth)
//   - Storage: localStorage menyimpan 'access_token', 'refresh_token', 'username'
// =============================================================================

// ---------------------------------------------------------------------------
// IMPORT & SETUP
// ---------------------------------------------------------------------------
const { test, expect } = require('@playwright/test');

// ---------------------------------------------------------------------------
// KONSTANTA
// ---------------------------------------------------------------------------
// [DISESUAIKAN] BASE_URL: Django dijalankan di port 2479, bukan 8000.
const BASE_URL = 'http://127.0.0.1:2479';

// SPA_URL: sudah cocok dengan setup Live Server (folder smartcity_citizen_spa)
//   Opsi 1 (Live Server): 'http://127.0.0.1:5500/smartcity_citizen_spa/index.html'
//   Opsi 2 (http-server):  'http://localhost:8080/index.html'
//   Opsi 3 (file://):      'file:///C:/Users/.../smartcity_citizen_spa/index.html'
const SPA_URL = 'http://127.0.0.1:5500/Lab_24782079/smartcity_citizen_spa_24782079/index.html';
// ---------------------------------------------------------------------------
// KREDENSIAL TEST
// ---------------------------------------------------------------------------
// TODO (perlu dikonfirmasi): akun citizen test ini harus benar-benar ada di
// database Django kamu (via createsuperuser biasa / register lewat SPA),
// karena loginSPA() memerlukannya. Sesuaikan jika kredensial berbeda.
const TEST_CITIZEN_USERNAME = 'testwarga';
const TEST_CITIZEN_PASSWORD = 'testpassword123';

// [DISESUAIKAN] Akun admin sesuai project: admin12 / 123
const TEST_ADMIN_USERNAME  = 'admin12';
const TEST_ADMIN_PASSWORD  = '123';

// ---------------------------------------------------------------------------
// FAKE JWT TOKENS UNTUK TESTING
// ---------------------------------------------------------------------------
const EXPIRED_ACCESS_TOKEN  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjAwMDAwMDAwLCJpYXQiOjE2MDAwMDAwMDAsImp0aSI6ImZha2VfYWNjZXNzX2lkIiwidXNlcl9pZCI6MX0.fake_signature_for_testing';
const EXPIRED_REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYwMDAwMDAwMCwiaWF0IjoxNjAwMDAwMDAwLCJqdGkiOiJmYWtlX3JlZnJlc2hfaWQiLCJ1c2VyX2lkIjoxfQ.fake_signature_for_testing';
const VALID_ACCESS_TOKEN    = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjo5OTk5OTk5OTk5LCJpYXQiOjE2MDAwMDAwMDAsImp0aSI6InZhbGlkX2FjY2Vzc19pZCIsInVzZXJfaWQiOjF9.fake_valid_signature';

// =============================================================================
// FUNGSI HELPER
// =============================================================================

async function loginSPA(page, username, password) {
    await page.goto(`${SPA_URL}#login`);
    await page.waitForSelector('#loginForm', { state: 'visible', timeout: 10000 });
    await page.locator('#loginUsername').fill(username);
    await page.locator('#loginPassword').fill(password);
    await page.locator('#loginForm button[type="submit"]').click();
}

async function loginAdmin(page, username, password) {
    // [DISESUAIKAN] Path login admin dikonfirmasi via smartcity_app/urls.py:
    // django.contrib.auth.urls di-include dengan prefix 'accounts/',
    // sehingga path login yang benar adalah '/accounts/login/', bukan '/login/'.
    await page.goto(`${BASE_URL}/accounts/login/`);
    await page.waitForSelector('form', { state: 'visible', timeout: 10000 });
    await page.locator('input[name="username"]').fill(username);
    await page.locator('input[name="password"]').fill(password);
    await Promise.all([
        page.waitForNavigation({ waitUntil: 'networkidle', timeout: 15000 }),
        page.locator('button[type="submit"]').click()
    ]);
}

async function setupAuthTokens(page, accessToken, refreshToken, username = 'testwarga') {
    await page.evaluate(
        ({ access, refresh, user }) => {
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('username', user);
        },
        { access: accessToken, refresh: refreshToken, user: username }
    );
}

async function clearAuthTokens(page) {
    await page.evaluate(() => {
        localStorage.clear();
    });
}

async function mockSPAApiUrl(page) {
    const BASE_URL = 'http://127.0.0.1:2479';

    await page.route('**/api/**', async (route) => {
        const originalUrl = route.request().url();

        if (originalUrl.startsWith(BASE_URL)) {
            return route.continue();
        }

        const urlObj = new URL(originalUrl);
        const newUrl = `${BASE_URL}${urlObj.pathname}${urlObj.search}`;

        await route.continue({ url: newUrl });
    });
}


// #############################################################################
// #   MODUL 1: OTORISASI & SESI (AUTH-04, AUTH-05, AUTH-06)                   #
// #############################################################################

test.describe('Modul 1: Otorisasi & Sesi (AUTH-04, AUTH-05, AUTH-06)', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto(SPA_URL);
        await clearAuthTokens(page);
        await mockSPAApiUrl(page);
    });

    test('AUTH-04: Akses #dashboard tanpa token → redirect ke #login', async ({ page }) => {
        const tokenBefore = await page.evaluate(() => {
            return localStorage.getItem('access_token');
        });
        expect(tokenBefore).toBeNull();

        await page.goto(`${SPA_URL}#dashboard`);

        await page.waitForFunction(
            () => window.location.hash === '#login',
            null,
            { timeout: 5000 }
        );

        await expect(page).toHaveURL(/#login/);

        const loginForm = page.locator('#loginForm');
        await expect(loginForm).toBeVisible({ timeout: 5000 });

        console.log('[AUTH-04] ✅ Redirect dari #dashboard ke #login berhasil diverifikasi');
    });

    test('AUTH-05: Token kadaluarsa → interceptor menangani 401 dan redirect ke #login', async ({ page }) => {
        await setupAuthTokens(page, EXPIRED_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        const storedToken = await page.evaluate(() => localStorage.getItem('access_token'));
        expect(storedToken).toBe(EXPIRED_ACCESS_TOKEN);

        await page.unroute('http://103.151.63.71:8013/api/**');

        await page.route('**/api/**', async (route) => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({
                    detail: 'Given token not valid for any token type',
                    code: 'token_not_valid'
                })
            });
        });

        page.on('dialog', async (dialog) => {
            console.log(`[AUTH-05] Dialog muncul: "${dialog.message()}"`);
            await dialog.accept();
        });

        await page.goto(`${SPA_URL}#dashboard`);

        await page.waitForTimeout(2000);

        await page.waitForFunction(
            () => window.location.hash === '#login',
            null,
            { timeout: 10000 }
        );

        await expect(page).toHaveURL(/#login/);

        const tokenAfter = await page.evaluate(() => localStorage.getItem('access_token'));
        const refreshAfter = await page.evaluate(() => localStorage.getItem('refresh_token'));

        expect(tokenAfter).toBeNull();
        expect(refreshAfter).toBeNull();

        console.log('[AUTH-05] ✅ Interceptor 401 berhasil: localStorage dibersihkan, redirect ke #login');
    });

    test('AUTH-06: Kedua token kadaluarsa → localStorage dibersihkan, redirect ke #login', async ({ page }) => {
        await setupAuthTokens(page, EXPIRED_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        const accessBefore = await page.evaluate(() => localStorage.getItem('access_token'));
        const refreshBefore = await page.evaluate(() => localStorage.getItem('refresh_token'));
        expect(accessBefore).not.toBeNull();
        expect(refreshBefore).not.toBeNull();

        await page.unroute('http://103.151.63.71:8013/api/**');

        await page.route('**/api/**', async (route) => {
            await route.fulfill({
                status: 401,
                contentType: 'application/json',
                body: JSON.stringify({
                    detail: 'Token is invalid or expired',
                    code: 'token_not_valid'
                })
            });
        });

        page.on('dialog', async (dialog) => {
            console.log(`[AUTH-06] Dialog muncul: "${dialog.message()}"`);
            await dialog.accept();
        });

        await page.goto(`${SPA_URL}#dashboard`);

        await page.waitForTimeout(2000);

        await page.waitForFunction(
            () => window.location.hash === '#login',
            null,
            { timeout: 10000 }
        );
        await expect(page).toHaveURL(/#login/);

        const accessAfter = await page.evaluate(() => localStorage.getItem('access_token'));
        expect(accessAfter).toBeNull();

        const refreshAfter = await page.evaluate(() => localStorage.getItem('refresh_token'));
        expect(refreshAfter).toBeNull();

        const usernameAfter = await page.evaluate(() => localStorage.getItem('username'));
        expect(usernameAfter).toBeNull();

        await expect(page.locator('#loginForm')).toBeVisible({ timeout: 5000 });

        console.log('[AUTH-06] ✅ Kedua token expired: localStorage bersih, redirect ke #login berhasil');
    });
});


// #############################################################################
// #   MODUL 5: INTERAKTIVITAS UI (UI-01 through UI-06)                        #
// #############################################################################

test.describe('Modul 5: Interaktivitas UI (UI-01 through UI-06)', () => {

    test('UI-01: Chart.js di Dashboard Admin ter-render dengan benar', async ({ page }) => {
        await loginAdmin(page, TEST_ADMIN_USERNAME, TEST_ADMIN_PASSWORD);

        await page.goto(`${BASE_URL}/dashboard/`);

        await page.waitForLoadState('networkidle');

        const statusChartCanvas  = page.locator('#statusChart');
        const categoryChartCanvas = page.locator('#categoryChart');

        await expect(statusChartCanvas).toBeVisible({ timeout: 15000 });
        await expect(categoryChartCanvas).toBeVisible({ timeout: 15000 });

        const chartsRendered = await page.evaluate(() => {
            if (typeof Chart === 'undefined') return false;
            const instances = Object.keys(Chart.instances || {});
            return instances.length >= 2;
        });

        expect(chartsRendered).toBe(true);

        await expect(page.locator('#reportedTable')).toBeVisible();
        await expect(page.locator('#resolvedTable')).toBeVisible();

        console.log('[UI-01] ✅ Chart.js statusChart dan categoryChart berhasil ter-render');
    });

    test('UI-02: Live Search pada daftar laporan admin berfungsi', async ({ page }) => {
        await loginAdmin(page, TEST_ADMIN_USERNAME, TEST_ADMIN_PASSWORD);

        await page.goto(`${BASE_URL}/reports/`);
        await page.waitForLoadState('networkidle');

        const searchInput = page.locator('#searchInput');
        const tableBody   = page.locator('#reportTableBody');

        await expect(searchInput).toBeVisible({ timeout: 10000 });
        await expect(tableBody).toBeVisible({ timeout: 10000 });

        const initialRowCount = await tableBody.locator('tr').count();
        console.log(`[UI-02] Jumlah baris awal: ${initialRowCount}`);

        const searchKeyword = 'Lampu';

        const responsePromise = page.waitForResponse(
            (response) => response.url().includes(`/search/?q=${searchKeyword}`) && response.status() === 200,
            { timeout: 15000 }
        );

        await searchInput.click();
        await searchInput.fill('');
        await searchInput.type(searchKeyword, { delay: 100 });

        const searchResponse = await responsePromise;

        expect(searchResponse.status()).toBe(200);

        const responseData = await searchResponse.json();
        console.log(`[UI-02] Hasil pencarian "${searchKeyword}": ${responseData.results?.length || 0} item`);

        await page.waitForTimeout(1000);

        const filteredRowCount = await tableBody.locator('tr').count();
        console.log(`[UI-02] Jumlah baris setelah filter: ${filteredRowCount}`);

        if (responseData.results && responseData.results.length > 0) {
            expect(filteredRowCount).toBeGreaterThan(0);
            expect(filteredRowCount).toBe(responseData.results.length);
        }

        console.log('[UI-02] ✅ Live search berfungsi: input → AJAX → tabel terupdate');
    });

    test('UI-03: Pagination Feed Kota — maks 10 kartu, kontrol pagination muncul', async ({ page }) => {
        await page.goto(SPA_URL);
        await mockSPAApiUrl(page);

        await page.unroute('http://103.151.63.71:8013/api/**');

        const mockReports = [];
        for (let i = 1; i <= 25; i++) {
            mockReports.push({
                id: i,
                title: `Laporan Test #${i}`,
                description: `Deskripsi laporan pengujian nomor ${i}`,
                category: i % 2 === 0 ? 'Infrastruktur' : 'Kebersihan',
                location: `Lokasi Test ${i}`,
                status: ['REPORTED', 'VERIFIED', 'IN_PROGRESS', 'RESOLVED'][i % 4],
                reporter_name: 'testwarga',
                is_owner: false,
                updated_at: new Date().toISOString()
            });
        }

        await page.route('**/api/report/**', async (route) => {
            const url = route.request().url();

            if (url.includes('tab=feed') || url.includes('tab=my_reports')) {
                const pageMatch = url.match(/page=(\d+)/);
                const pageNum = pageMatch ? parseInt(pageMatch[1]) : 1;

                const pageSize = 10;
                const startIdx = (pageNum - 1) * pageSize;
                const endIdx = startIdx + pageSize;
                const pageData = mockReports.slice(startIdx, endIdx);

                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        count: mockReports.length,
                        results: pageData,
                        next: endIdx < mockReports.length ? 'next_page_url' : null,
                        previous: pageNum > 1 ? 'prev_page_url' : null
                    })
                });
            } else {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ count: 0, results: [] })
                });
            }
        });

        await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        page.on('dialog', async (dialog) => await dialog.accept());

        await page.goto(`${SPA_URL}#dashboard`);
        await page.waitForSelector('#btnBukaModal', { state: 'visible', timeout: 10000 });

        const tabFeedKota = page.locator('#tabFeedKota');
        await expect(tabFeedKota).toBeVisible();
        await tabFeedKota.click();

        await page.waitForTimeout(2000);

        const listContainer = page.locator('#listContainer');
        await expect(listContainer).toBeVisible();

        const reportCards = listContainer.locator('.col');
        const cardCount = await reportCards.count();

        expect(cardCount).toBeLessThanOrEqual(10);
        expect(cardCount).toBeGreaterThan(0);

        console.log(`[UI-03] Jumlah kartu di Feed Kota: ${cardCount} (maks 10)`);

        const paginationContainer = page.locator('#paginationContainer');
        await expect(paginationContainer).toBeVisible();

        const paginationButtons = paginationContainer.locator('.page-item');
        const paginationCount = await paginationButtons.count();

        expect(paginationCount).toBeGreaterThanOrEqual(3);

        console.log(`[UI-03] ✅ Pagination terverifikasi: ${cardCount} kartu, ${paginationCount} tombol navigasi`);
    });

    test('UI-04: Klik tombol Buat Laporan → modal #reportModal muncul', async ({ page }) => {
        await page.goto(SPA_URL);

        await page.unroute('http://103.151.63.71:8013/api/**');

        await page.route('**/api/**', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ count: 0, results: [] })
            });
        });

        await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        page.on('dialog', async (dialog) => await dialog.accept());

        await page.goto(`${SPA_URL}#dashboard`);

        const btnBukaModal = page.locator('#btnBukaModal');
        await expect(btnBukaModal).toBeVisible({ timeout: 10000 });

        const reportModal = page.locator('#reportModal');

        await expect(reportModal).not.toBeVisible();

        await btnBukaModal.click();

        await expect(reportModal).toBeVisible({ timeout: 5000 });

        const hasShowClass = await reportModal.evaluate(
            (el) => el.classList.contains('show')
        );
        expect(hasShowClass).toBe(true);

        await expect(page.locator('#reportForm')).toBeVisible();
        await expect(page.locator('#inputTitle')).toBeVisible();
        await expect(page.locator('#inputCategory')).toBeVisible();
        await expect(page.locator('#inputLocation')).toBeVisible();
        await expect(page.locator('#inputDescription')).toBeVisible();
        await expect(page.locator('#btnDraft')).toBeVisible();
        await expect(page.locator('#btnSubmit')).toBeVisible();

        const modalTitle = page.locator('#reportModalLabel');
        await expect(modalTitle).toContainText('Buat Laporan Baru');

        console.log('[UI-04] ✅ Modal #reportModal berhasil dibuka dengan semua elemen form');
    });

    test('UI-05: Isi form dan simpan draft → modal tutup, notifikasi muncul', async ({ page }) => {
        await page.goto(SPA_URL);
        await page.unroute('http://103.151.63.71:8013/api/**');

        let draftSubmitted = false;

        await page.route('**/api/report/**', async (route) => {
            const method = route.request().method();
            const url = route.request().url();

            if (method === 'POST') {
                draftSubmitted = true;

                const postData = route.request().postDataJSON();
                console.log(`[UI-05] POST received: ${JSON.stringify(postData)}`);

                await route.fulfill({
                    status: 201,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        id: 99,
                        title: postData?.title || 'Test Draft',
                        category: postData?.category || 'Infrastruktur',
                        location: postData?.location || 'Test Location',
                        description: postData?.description || 'Test Description',
                        status: 'DRAFT',
                        reporter_name: 'testwarga',
                        is_owner: true
                    })
                });
            } else if (method === 'GET' && url.includes('page_size=1000')) {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({
                        count: 1,
                        results: [{
                            id: 99,
                            title: 'Test Draft',
                            status: 'DRAFT',
                            category: 'Infrastruktur',
                            location: 'Gedung Lab',
                            description: 'Deskripsi test',
                            reporter_name: 'testwarga',
                            is_owner: true
                        }]
                    })
                });
            } else {
                await route.fulfill({
                    status: 200,
                    contentType: 'application/json',
                    body: JSON.stringify({ count: 0, results: [] })
                });
            }
        });

        await setupAuthTokens(page, VALID_ACCESS_TOKEN, EXPIRED_REFRESH_TOKEN);

        let alertMessage = '';
        page.on('dialog', async (dialog) => {
            alertMessage = dialog.message();
            console.log(`[UI-05] Alert: "${alertMessage}"`);
            await dialog.accept();
        });

        await page.goto(`${SPA_URL}#dashboard`);
        await page.waitForSelector('#btnBukaModal', { state: 'visible', timeout: 10000 });

        await page.locator('#btnBukaModal').click();

        await expect(page.locator('#reportModal')).toBeVisible({ timeout: 5000 });

        await page.locator('#inputTitle').fill('AC Mati di Lab CPS 1');

        await page.locator('#inputCategory').selectOption('Infrastruktur');

        await page.locator('#inputLocation').fill('Gedung Lab Analisis, Lantai 2');

        await page.locator('#inputDescription').fill(
            'Unit AC di ruang Lab CPS 1 tidak berfungsi sejak tadi pagi. ' +
            'Suhu ruangan sangat panas dan mengganggu kegiatan praktikum.'
        );

        await page.locator('#btnDraft').click();

        await page.waitForTimeout(2000);

        const reportModal = page.locator('#reportModal');
        await expect(reportModal).not.toBeVisible({ timeout: 5000 });

        expect(alertMessage).toContain('berhasil');

        await page.waitForTimeout(2000);

        const summaryStats = page.locator('#summaryStats');
        await expect(summaryStats).toBeVisible();

        const draftBadge = summaryStats.locator('.badge.bg-secondary').first();
        const draftCountText = await draftBadge.textContent();
        const draftCount = parseInt(draftCountText, 10);

        expect(draftCount).toBeGreaterThanOrEqual(1);

        console.log(`[UI-05] ✅ Draft tersimpan: modal tutup, alert muncul, badge Draf = ${draftCount}`);
    });

    test('UI-06: Responsive navbar pada viewport mobile (400x800)', async ({ page }) => {
        await page.setViewportSize({ width: 400, height: 800 });

        await page.goto(SPA_URL);
        await page.waitForLoadState('domcontentloaded');

        const navbar = page.locator('.navbar');
        await expect(navbar).toBeVisible({ timeout: 5000 });

        const navbarToggler = page.locator('.navbar-toggler');
        const togglerCount = await navbarToggler.count();

        if (togglerCount > 0) {
            await expect(navbarToggler).toBeVisible();
            console.log('[UI-06] ✓ Navbar toggler (hamburger) button terlihat di mobile');

            const navbarCollapse = page.locator('.navbar-collapse');
            const collapseCount = await navbarCollapse.count();
            if (collapseCount > 0) {
                const hasShow = await navbarCollapse.evaluate(
                    (el) => el.classList.contains('show')
                );
                expect(hasShow).toBe(false);
                console.log('[UI-06] ✓ Navbar collapse TIDAK dalam state "show" (tersembunyi)');
            }
        } else {
            const navbarBox = await navbar.boundingBox();
            expect(navbarBox).not.toBeNull();

            expect(navbarBox.width).toBeLessThanOrEqual(400);

            const navMenus = page.locator('#nav-menus');
            const navMenusCount = await navMenus.count();
            expect(navMenusCount).toBeGreaterThanOrEqual(1);

            console.log('[UI-06] ✓ Navbar beradaptasi dengan viewport mobile (400px)');
        }

        const mobileNavbarBox = await navbar.boundingBox();
        const mobileWidth = mobileNavbarBox?.width || 0;

        await page.setViewportSize({ width: 1280, height: 800 });
        await page.waitForTimeout(500);

        const desktopNavbarBox = await navbar.boundingBox();
        const desktopWidth = desktopNavbarBox?.width || 0;

        expect(desktopWidth).toBeGreaterThan(mobileWidth);

        console.log(`[UI-06] ✅ Responsive terverifikasi: mobile=${mobileWidth}px, desktop=${desktopWidth}px`);

        await page.setViewportSize({ width: 1280, height: 720 });
    });
});

// =============================================================================
// SELESAI
// =============================================================================