// js/app.js

function handleRouting() {
    // Ambil hash URL saat ini, jika kosong set default ke #login
    const hash = window.location.hash || '#login';
    const appContent = document.getElementById('app-content');
    
    // Ambil template HTML dari objek routes yang ada di router.js
    appContent.innerHTML = routes[hash] || routes['#login'];
    
    // Jika rute saat ini adalah #login, pasang event listener submit formulir
    if (hash === '#login') {
        if (typeof setupLoginForm === 'function') {
            setupLoginForm();
        }
    }
}

// Pasang pelacak event listener perubahan hash URL global browser
window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);