// js/router.js

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
                <div class="card border-0 p-3 shadow-sm mb-3" style="border-radius: 16px;">
                    <button onclick="editingReportId=null; document.getElementById('reportForm').reset(); document.getElementById('reportModalLabel').innerText='Buat Laporan Baru';" 
                            data-bs-toggle="modal" data-bs-target="#reportModal" 
                            class="btn btn-primary btn-lg w-100 fw-bold mb-3" style="border-radius: 12px;">
                        <i class="bi bi-plus-circle-fill me-2"></i>Laporan Baru
                    </button>
                    
                    <!-- ========================================== -->
                    <!-- SINKRONISASI 5 STATUS SESUAI IMAGE_5CD41E  -->
                    <!-- ========================================== -->
                    <div class="list-group list-group-flush small">
                        <h6 class="fw-bold mb-3 mt-1 text-secondary"><i class="bi bi-graph-up me-2"></i>Rekap Status</h6>
                        
                        <div class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 py-2">
                            <span><i class="bi bi-file-earmark-text me-2 text-muted"></i>Draft Keluhan</span>
                            <span id="stat-draft" class="badge bg-secondary rounded-pill">0</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 py-2">
                            <span><i class="bi bi-megaphone me-2 text-warning"></i>Total Diajukan</span>
                            <span id="stat-reported" class="badge bg-warning text-dark rounded-pill">0</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 py-2">
                            <span><i class="bi bi-patch-check me-2 text-info"></i>Terverifikasi</span>
                            <span id="stat-verified" class="badge bg-info rounded-pill">0</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 py-2">
                            <span><i class="bi bi-clock-history me-2 text-primary"></i>Sedang Diproses</span>
                            <span id="stat-process" class="badge bg-primary rounded-pill">0</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center border-0 px-0 py-2">
                            <span><i class="bi bi-check-circle me-2 text-success"></i>Selesai Ditangani</span>
                            <span id="stat-done" class="badge bg-success rounded-pill">0</span>
                        </div>
                    </div>
                </div>
                <button onclick="handleLogout()" class="btn btn-outline-danger w-100 fw-bold" style="border-radius: 12px;">
                    <i class="bi bi-box-arrow-right me-2"></i>Keluar
                </button>
            </aside>
            
            <section class="col-12 col-lg-6">
                <ul class="nav nav-pills mb-3 bg-white p-2 shadow-sm d-flex" style="border-radius: 12px;">
                    <li class="nav-item flex-fill">
                        <button onclick="switchTab('my_reports')" id="tab-my_reports" class="nav-link w-100 active fw-bold">Laporan Saya</button>
                    </li>
                    <li class="nav-item flex-fill">
                        <button onclick="switchTab('feed')" id="tab-feed" class="nav-link w-100 fw-bold text-muted">Feed Kota</button>
                    </li>
                </ul>

                <div id="listContainer" class="row g-3">
                    <div class="text-center p-5">
                        <div class="spinner-border text-primary" role="status"></div>
                        <p class="mt-2 text-muted">Menarik data dari API...</p>
                    </div>
                </div>

                <nav id="paginationContainer" class="mt-4 d-flex justify-content-center"></nav>
            </section>
            
            <aside class="col-12 col-lg-3 d-none d-lg-block">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px; border-radius: 16px;">
                    <h6 class="fw-bold text-primary mb-3">
                        <i class="bi bi-info-circle-fill me-2"></i>Info Kilat
                    </h6>
                    <p class="small text-muted mb-0">Interface kini terhubung otomatis dengan data real-time melalui optimasi Fetch API.</p>
                </div>
            </aside>
        </div>
    `
};

// Fungsi pembantu untuk visual tab di router
function switchTab(tab) {
    document.querySelectorAll('.nav-link').forEach(el => {
        el.classList.remove('active');
        el.classList.add('text-muted');
    });
    document.getElementById('tab-' + tab).classList.add('active');
    document.getElementById('tab-' + tab).classList.remove('text-muted');
    
    // Panggil fungsi penarik data dari app.js
    if (typeof loadDashboardData === 'function') {
        loadDashboardData(tab, 1);
    }
}