// js/app.js

// 1. VARIABEL GLOBAL UNTUK STATE MANAJEMEN
let currentTab = 'my_reports';
let currentPage = 1;
let allReports = [];
let editingReportId = null;

// 2. FUNGSI ROUTING SPA
function handleRouting() {
    const hash = window.location.hash || '#login';
    const appContent = document.getElementById('app-content');

    // GUARD: cegah akses #dashboard tanpa token
    if (hash === '#dashboard' && !localStorage.getItem('access_token')) {
        window.location.hash = '#login';
        return;
    }

    appContent.innerHTML = routes[hash] || routes['#login'];
    
    if (hash === '#login') {
        if (typeof setupLoginForm === 'function') setupLoginForm();
    } else if (hash === '#dashboard') {
        loadDashboardData(); 
    }
}

// 3. FUNGSI UTAMA: MENARIK DATA API TERPAGINASI
async function loadDashboardData(tab = currentTab, page = currentPage) {
    currentTab = tab;
    currentPage = page;

    const response = await requestAPI(`/report/?tab=${tab}&page=${page}`, 'GET');

    if (response && response.status === 200) {
        const responseData = await response.json();
        
        allReports = responseData.results || []; 
        const totalData = responseData.count || 0; 
        const totalPages = Math.ceil(totalData / 10); 

        renderList();          
        renderPagination(totalPages); 
        loadSummaryStats();    
        
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
        container.innerHTML = '<div class="text-center py-5 text-muted">Belum ada laporan di kategori ini.</div>';
        return;
    }

    container.innerHTML = '';
    allReports.forEach(report => {
        // Logika Progress Bar & Warna Status
        let pWidth = '20%'; let pBg = 'bg-secondary';
        if (report.status === 'REPORTED') { pWidth = '40%'; pBg = 'bg-warning'; }
        else if (report.status === 'VERIFIED') { pWidth = '60%'; pBg = 'bg-info'; }
        else if (report.status === 'IN_PROGRESS') { pWidth = '80%'; pBg = 'bg-primary'; }
        else if (report.status === 'RESOLVED') { pWidth = '100%'; pBg = 'bg-success'; }

        const editBtn = (report.is_owner && report.status === 'DRAFT') 
            ? `<button onclick="editDraft(${report.id})" class="btn btn-sm btn-outline-primary fw-bold">Edit Draft</button>` : '';

        container.innerHTML += `
            <div class="col-12 col mb-3">
                <div class="card border-0 shadow-sm p-3" style="border-radius: 16px;">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="badge bg-light text-primary border">${report.category}</span>
                        <small class="text-muted"><i class="bi bi-geo-alt me-1"></i>${report.location}</small>
                    </div>
                    <h5 class="fw-bold">${report.title}</h5>
                    <p class="small text-secondary text-truncate">${report.description}</p>
                    <div class="progress mb-2" style="height: 6px;"><div class="progress-bar progress-bar-striped progress-bar-animated ${pBg}" style="width: ${pWidth}"></div></div>
                    <div class="d-flex justify-content-between align-items-center mt-2">
                        <small class="text-muted text-capitalize">Oleh: ${report.reporter}</small>
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

// 6. FUNGSI REKAP STATUS SIDEBAR (BYPASS PAGINATION) - 5 STATUS SINKRON DENGAN ROUTER.JS
async function loadSummaryStats() {
    const res = await requestAPI(`/report/?tab=my_reports&page_size=1000`, 'GET');
    if (res && res.status === 200) {
        const data = await res.json();
        const r = data.results || [];
        
        // Memasukkan angka ke elemen ID yang sudah kita buat di router.js
        if(document.getElementById('stat-draft')) 
            document.getElementById('stat-draft').innerText = r.filter(x => x.status === 'DRAFT').length;
        if(document.getElementById('stat-reported'))
            document.getElementById('stat-reported').innerText = r.filter(x => x.status === 'REPORTED').length;
        if(document.getElementById('stat-verified'))
            document.getElementById('stat-verified').innerText = r.filter(x => x.status === 'VERIFIED').length;
        if(document.getElementById('stat-process'))
            document.getElementById('stat-process').innerText = r.filter(x => x.status === 'IN_PROGRESS').length;
        if(document.getElementById('stat-done'))
            document.getElementById('stat-done').innerText = r.filter(x => x.status === 'RESOLVED').length;
    }
}

// 7. MANAJEMEN MODAL: EDIT & SUBMIT
function editDraft(id) {
    const report = allReports.find(r => r.id === id);
    if (!report) return;
    editingReportId = id;
    document.getElementById('inputTitle').value = report.title;
    document.getElementById('inputCategory').value = report.category;
    document.getElementById('inputLocation').value = report.location;
    document.getElementById('inputDescription').value = report.description;
    document.getElementById('reportModalLabel').innerText = "Edit Laporan Draft";
    new bootstrap.Modal(document.getElementById('reportModal')).show();
}

async function handleSave(status) {
    const payload = {
        title: document.getElementById('inputTitle').value,
        category: document.getElementById('inputCategory').value,
        location: document.getElementById('inputLocation').value,
        description: document.getElementById('inputDescription').value,
        status: status
    };

    const method = editingReportId ? 'PUT' : 'POST'; 
    const path = editingReportId ? `/report/${editingReportId}/` : '/report/';
    
    const response = await requestAPI(path, method, payload);
    if (response.status === 201 || response.status === 200) {
        bootstrap.Modal.getInstance(document.getElementById('reportModal')).hide();
        document.getElementById('reportForm').reset();
        editingReportId = null;

        // Notifikasi sukses (dibutuhkan agar sesuai skenario UI-05)
        if (status === 'DRAFT') {
            alert('Laporan berhasil disimpan sebagai DRAFT');
        } else {
            alert('Laporan berhasil diajukan');
        }

        loadDashboardData(); 
    }
}

// Event Delegation untuk tombol modal
document.addEventListener('click', e => {
    if (e.target.id === 'btnSubmit' || e.target.closest('#btnSubmit')) handleSave('REPORTED');
    if (e.target.id === 'btnDraft' || e.target.closest('#btnDraft')) handleSave('DRAFT');
});

window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);