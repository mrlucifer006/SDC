const API_BASE_URL = `${import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}/api`;

export const getAuthToken = () => localStorage.getItem('token');
export const setAuthToken = (token: string) => localStorage.setItem('token', token);
export const removeAuthToken = () => localStorage.removeItem('token');

async function fetchWithAuth(url: string, options: RequestInit = {}) {
    const token = getAuthToken();
    const headers: Record<string, string> = {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    // Only set Content-Type to JSON if body is a string (not FormData)
    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    // Merge provided headers
    const finalHeaders = { ...headers, ...(options.headers as Record<string, string>) };
    if (options.body instanceof FormData && finalHeaders['Content-Type']) {
        // Let the browser set the boundary for FormData
        delete finalHeaders['Content-Type'];
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
        ...options,
        headers: finalHeaders,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'API request failed');
    }

    return response.json();
}

export const api = {
    get: (url: string) => fetchWithAuth(url),
    post: (url: string, data: any, isForm: boolean = false) => {
        const options: RequestInit = {
            method: 'POST',
        };
        
        if (isForm) {
            options.body = data; // Should be FormData
        } else {
            options.body = JSON.stringify(data);
        }

        return fetchWithAuth(url, options);
    }
};
