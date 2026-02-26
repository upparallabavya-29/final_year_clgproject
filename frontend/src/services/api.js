import toast from 'react-hot-toast'

export async function authFetch(url, options = {}) {
    const token = localStorage.getItem('cropguard_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    // Remove Content-Type if we're sending FormData
    if (options.body && options.body instanceof FormData) {
        delete headers['Content-Type'];
    }

    try {
        const res = await fetch(url, { ...options, headers });
        if (res.status === 401) {
            localStorage.removeItem('cropguard_token');
            localStorage.removeItem('cropguard_user');
            window.location.href = '/auth?mode=login';
        }
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            throw new Error(data.detail || `Request failed with status ${res.status}`);
        }
        return res;
    } catch (err) {
        toast.error(err.message || 'An unexpected networking error occurred');
        throw err;
    }
}
