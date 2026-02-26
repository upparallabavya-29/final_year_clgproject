import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AuthContext = createContext(null)

const TOKEN_KEY = 'cropguard_token'
const USER_KEY = 'cropguard_user'

export function AuthProvider({ children }) {
    const [user, setUser] = useState(() => {
        try {
            const stored = localStorage.getItem(USER_KEY)
            return stored ? JSON.parse(stored) : null
        } catch { return null }
    })
    const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || null)
    const [loading, setLoading] = useState(false)

    const saveAuth = useCallback((tokenStr, userData) => {
        if (!userData) return
        setToken(tokenStr)
        setUser(userData)
        localStorage.setItem(TOKEN_KEY, tokenStr)
        localStorage.setItem(USER_KEY, JSON.stringify(userData))
    }, [])

    const logout = useCallback(() => {
        setToken(null)
        setUser(null)
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
    }, [])

    // Handle Google OAuth callback — token arrives in URL hash
    useEffect(() => {
        const hash = window.location.hash
        if (hash.includes('token=')) {
            const params = new URLSearchParams(hash.slice(1))
            const t = params.get('token')
            const name = params.get('name') || ''
            const avatar = params.get('avatar') || ''
            const email = params.get('email') || ''
            if (t) {
                // Save immediately with what we have from the hash
                saveAuth(t, { name, avatar, email, provider: 'google' })
                // Clean the URL
                window.history.replaceState({}, '', window.location.pathname)
                // Fetch full profile from backend to get id, email, phone etc.
                fetch('/api/auth/me', {
                    headers: { 'Authorization': `Bearer ${t}` }
                })
                    .then(r => r.ok ? r.json() : null)
                    .then(fullUser => {
                        if (fullUser) {
                            saveAuth(t, fullUser)
                        }
                    })
                    .catch(() => { /* keep hash-based data */ })
            }
        }
    }, [saveAuth])

    const authFetch = useCallback(async (url, options = {}) => {
        const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
        if (token) headers['Authorization'] = `Bearer ${token}`
        return fetch(url, { ...options, headers })
    }, [token])

    return (
        <AuthContext.Provider value={{ user, token, loading, setLoading, saveAuth, logout, authFetch, isLoggedIn: !!user }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
