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
            // PERBAIKAN: Gunakan '/token/' saja karena '/api' sudah ada di BASE_URL api.js
            const response = await requestAPI('/token/', 'POST', {
                username: usernameInput,
                password: passwordInput
            });
            
            if (response.status === 200) {
                const data = await response.json();
                
                // Simpan access dan refresh token ke localStorage browser
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                
                // Opsional: Langsung pindah tanpa alert biar kerasa kayak aplikasi modern
                window.location.hash = '#dashboard';
            } else {
                alert('Login Gagal! Periksa kembali username dan password Anda.');
            }
        } catch (error) {
            console.error("Auth Error:", error);
            alert('Gagal menghubungi server backend! Pastikan server Django jalan.');
        }
    });
}

function handleLogout() {
    // Bersihkan seluruh token dari memori lokal browser
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Redirect ke login
    window.location.hash = '#login';
}