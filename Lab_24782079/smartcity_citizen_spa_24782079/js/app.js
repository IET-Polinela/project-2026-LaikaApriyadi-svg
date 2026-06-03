// js/app.js

// 1. VARIABEL GLOBAL UNTUK STATE MANAJEMEN [cite: 90, 126]
let currentTab = 'my_reports';
let currentPage = 1;
let allReports = [];
let editingReportId = null;

// 2. FUNGSI ROUTING SPA [cite: 90]
function handleRouting() {
    const hash = window.location.hash || '#login';
    const appContent = document.getElementById('app-content');
    
    appContent.innerHTML = routes[hash] || routes['#login'];
    
    if (hash === '#login') {
        if (typeof setupLoginForm === 'function') setupLoginForm();
    } else if (hash === '#dashboard') {
        loadDashboardData(); // Tarik data real-time saat dashboard dimuat 
    }
}

// 3. FUNGSI UTAMA: MENARIK DATA API TERPAGINASI (Figure 4) [cite: 87, 88]
async function loadDashboardData(tab = currentTab, page = currentPage) {
    currentTab = tab;
    currentPage = page;

    // Menembak API Backend dengan parameter tab dan halaman [cite: 88, 94]
    const response = await requestAPI(`/report/?tab=${tab}&page=${page}`, 'GET');

    if (response && response.status === 200) {
        const responseData = await response.json();
        
        // INSTRUKSI 1: Ekstraksi Data Paginasi [cite: 96, 97]
        allReports = responseData.results || []; 
        const totalData = responseData.count || 0; 
        const totalPages = Math.ceil(totalData / 10); // Pembulatan ke atas (Figure 4) [cite: 99]

        // INSTRUKSI 2: Pemicu Perbaruan UI [cite: 101, 102]
        renderList();          // Menggambar kartu laporan [cite: 103]
        renderPagination(totalPages); // Menggambar tombol halaman [cite: 104]
        loadSummaryStats();    // Update rekap sidebar [cite: 123]
        
    } else {
        const listContainer = document.getElementById('listContainer');
        if (listContainer) {
            listContainer.innerHTML = `
                <div class="col-12 text-center text-muted p-3">
                    <i class="bi bi-exclamation-triangle fs-1"></i>
                    <p>Gagal memuat data laporan.</p>
                </div>`;
        }
    }
}

// 4. MANIPULASI DOM: MENGGAMBAR KARTU LAPORAN DINAMIS 
function renderList() {
    const container = document.getElementById('listContainer');
    if (!container) return;

    if (allReports.length === 0) {
        container.innerHTML = '<div class="text-center py-5">Belum ada laporan.</div>';
        return;
    }

    container.innerHTML = '';
    allReports.forEach(report => {
        // Logika Progress Bar berdasarkan status [cite: 7]
        let pWidth = '20%'; let pBg = 'bg-secondary';
        if (report.status === 'REPORTED') { pWidth = '50%'; pBg = 'bg-warning'; }
        else if (report.status === 'RESOLVED') { pWidth = '100%'; pBg = 'bg-success'; }

        // Tombol Edit hanya untuk DRAFT milik sendiri [cite: 143]
        const editBtn = (report.is_owner && report.status === 'DRAFT') 
            ? `<button onclick="editDraft(${report.id})" class="btn btn-sm btn-outline-primary fw-bold">Edit Draft</button>` : '';

        container.innerHTML += `
            <div class="col-12 mb-3">
                <div class="card border-0 shadow-sm p-3" style="border-radius: 16px;">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="badge bg-light text-primary">${report.category}</span>
                        <small class="text-muted">${report.location}</small>
                    </div>
                    <h5 class="fw-bold">${report.title}</h5>
                    <p class="small text-secondary">${report.description}</p>
                    <div class="progress mb-2" style="height: 6px;"><div class="progress-bar ${pBg}" style="width: ${pWidth}"></div></div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">Oleh: ${report.reporter}</small>
                        ${editBtn}
                    </div>
                </div>
            </div>`;
    });
}

// 5. MANIPULASI DOM: MENYUSUN TOMBOL HALAMAN 
function renderPagination(total) {
    const container = document.getElementById('paginationContainer');
    if (!container || total <= 1) { if(container) container.innerHTML = ''; return; }

    let html = '<ul class="pagination pagination-sm">';
    for (let i = 1; i <= total; i++) {
        html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                    <button class="page-link" onclick="loadDashboardData(currentTab, ${i})">${i}</button>
                 </li>`;
    }
    container.innerHTML = html + '</ul>';
}

// 6. FUNGSI REKAP STATUS SIDEBAR (BYPASS PAGINATION) [cite: 119, 120]
async function loadSummaryStats() {
    const res = await requestAPI(`/report/?tab=my_reports&page_size=1000`, 'GET');
    if (res && res.status === 200) {
        const data = await res.json();
        const r = data.results || [];
        document.getElementById('stat-draft').innerText = r.filter(x => x.status === 'DRAFT').length;
        document.getElementById('stat-process').innerText = r.filter(x => x.status === 'REPORTED').length;
        document.getElementById('stat-done').innerText = r.filter(x => x.status === 'RESOLVED').length;
    }
}

// 7. MANAJEMEN MODAL: EDIT & SUBMIT [cite: 124, 127, 129]
function editDraft(id) {
    const report = allReports.find(r => r.id === id);
    if (!report) return;
    editingReportId = id;
    document.getElementById('reportTitle').value = report.title;
    document.getElementById('reportCategory').value = report.category;
    document.getElementById('reportLocation').value = report.location;
    document.getElementById('reportDescription').value = report.description;
    document.getElementById('reportModalLabel').innerText = "Edit Laporan Draft";
    new bootstrap.Modal(document.getElementById('reportModal')).show();
}

async function handleSave(status) {
    const payload = {
        title: document.getElementById('reportTitle').value,
        category: document.getElementById('reportCategory').value,
        location: document.getElementById('reportLocation').value,
        description: document.getElementById('reportDescription').value,
        status: status
    };

    const method = editingReportId ? 'PUT' : 'POST'; // [cite: 131, 132]
    const path = editingReportId ? `/report/${editingReportId}/` : '/report/'; 
    
    const response = await requestAPI(path, method, payload);
    if (response.status === 201 || response.status === 200) {
        bootstrap.Modal.getInstance(document.getElementById('reportModal')).hide();
        document.getElementById('reportForm').reset();
        editingReportId = null;
        loadDashboardData(); // Panggil ulang data lokal [cite: 134, 146]
    }
}

// Inisialisasi tombol di modal (Gunakan type="button" di HTML!) [cite: 147, 148]
document.addEventListener('click', e => {
    if (e.target.id === 'btnSubmit') handleSave('REPORTED');
    if (e.target.id === 'btnDraft') handleSave('DRAFT');
});

window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);