// js/api.js
const BASE_URL = 'http://127.0.0.1:2479'; // Port 2479 sesuai running server Django lu

async function requestAPI(endpoint, method = 'GET', bodyData = null) {
    const url = `${BASE_URL}${endpoint}`;
    
    // Ambil access token secara otomatis dari localStorage
    const token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Jika token eksis di memori browser, pasang ke Header Authorization
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method: method,
        headers: headers
    };
    
    if (bodyData && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(bodyData);
    }
    
    try {
        const response = await fetch(url, config);
        return response;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}