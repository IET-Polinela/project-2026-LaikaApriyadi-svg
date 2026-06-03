// js/router.js

// Definisi template HTML halaman SPA menggunakan format backtick ( ` )
const routes = {
    '#login': `
        <div class="row justify-content-center pt-5">
            <div class="col-md-4 card shadow-sm border-0 p-4" style="border-radius: 16px;">
                <h4 class="text-center fw-bold mb-4">Login Warga</h4>
                <form id="loginForm">
                    <div class="mb-3">
                        <input type="text" id="loginUsername" class="form-control" placeholder="Username" required>
                    </div>
                    <div class="mb-3">
                        <input type="password" id="loginPassword" class="form-control" placeholder="Password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 fw-bold" style="border-radius: 10px;">Masuk</button>
                </form>
            </div>
        </div>
    `,
    '#dashboard': `
        <div class="row g-4">
            <aside class="col-12 col-lg-3">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px; border-radius: 16px;">
                    <button class="btn btn-primary btn-lg w-100 fw-bold mb-3" style="border-radius: 12px;">
                        <i class="bi bi-plus-circle-fill me-2"></i>Laporan Baru
                    </button>
                    <button onclick="handleLogout()" class="btn btn-outline-danger w-100 fw-bold" style="border-radius: 12px;">
                        <i class="bi bi-box-arrow-right me-2"></i>Keluar
                    </button>
                </div>
            </aside>
            
            <section class="col-12 col-lg-6">
                <div class="card border-0 p-5 shadow-sm text-center text-muted" style="border: 2px dashed #cbd5e1; border-radius: 24px;">
                    <i class="bi bi-inbox fs-1 text-primary mb-3"></i>
                    <h5 class="fw-bold text-dark">Selamat Datang di Citizen Portal!</h5>
                    <p class="small text-muted mb-0">Koneksi API untuk data laporan real-time akan diimplementasikan pada Lab 12.</p>
                </div>
            </section>
            
            <aside class="col-12 col-lg-3 d-none d-lg-block">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px; border-radius: 16px;">
                    <h6 class="fw-bold text-primary mb-3">
                        <i class="bi bi-info-circle-fill me-2"></i>Info Kilat
                    </h6>
                    <p class="small text-muted mb-0">Arsitektur aplikasi sukses dikonfigurasi menggunakan modul mandiri HeadlessFrontend SPA.</p>
                </div>
            </aside>
        </div>
    `
};