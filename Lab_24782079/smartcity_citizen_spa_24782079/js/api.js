// js/api.js
const BASE_URL = "http://127.0.0.1:2479";

async function requestAPI(endpoint, method = 'GET', bodyData = null) {
    let urutanEndpoint = endpoint;
    if (!endpoint.startsWith('/api/')) {
        urutanEndpoint = `/api${endpoint}`;
    }

    const url = `${BASE_URL}${urutanEndpoint}`;
    const token = localStorage.getItem('access_token');
    
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    
    const config = { method, headers };
    if (bodyData && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(bodyData);
    }
    
    try {
        const response = await fetch(url, config);

        // INTERCEPTOR: kalau token expired/invalid, bersihkan & lempar ke login
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('username');
            window.location.hash = '#login';
}
        return response;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}