// js/api.js
const BASE_URL = "http://103.151.63.87:8010";

async function requestAPI(endpoint, method = 'GET', bodyData = null) {
    const url = `${BASE_URL}${endpoint}`;
    
    // Ambil access token secara otomatis dari localStorage
    const token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
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