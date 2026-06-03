// js/auth.js

function setupLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        // Mencegah halaman reload otomatis agar parameter password tidak bocor
        event.preventDefault(); 

        const usernameInput = document.getElementById('loginUsername').value;
        const passwordInput = document.getElementById('loginPassword').value;

        try {
            // Mengirim data ke endpoint token JWT Django DRF
            const response = await requestAPI('/api/token/', 'POST', {
                username: usernameInput,
                password: passwordInput
            });
            
            if (response.status === 200) {
                const data = await response.json();
                
                // Simpan access dan refresh token ke localStorage browser
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                
                alert('Login Berhasil, Selamat Datang!');
                
                // Pindah rute halaman secara dinamis
                window.location.hash = '#dashboard';
            } else {
                alert('Login Gagal! Periksa kembali username dan password Anda.');
            }
        } catch (error) {
            alert('Gagal menghubungi server backend!');
        }
    });
}

function handleLogout() {
    // Bersihkan seluruh token dari memori lokal browser
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    alert('Anda telah keluar.');
    window.location.hash = '#login';
}