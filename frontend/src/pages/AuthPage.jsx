import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import styles from './AuthPage.module.css'

const API = '/api'

// ── Tab: Email ─────────────────────────────────────────────────────────────
function EmailTab({ mode, onSuccess }) {
    const { saveAuth } = useAuth()
    const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
    const [err, setErr] = useState('')
    const [loading, setLoading] = useState(false)
    const isLogin = mode === 'login'

    const change = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

    const submit = async e => {
        e.preventDefault()
        setErr('')
        if (!isLogin && form.password !== form.confirm) { setErr('Passwords do not match.'); return }
        setLoading(true)
        try {
            const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register'
            const body = isLogin
                ? { email: form.email, password: form.password }
                : { name: form.name, email: form.email, password: form.password }
            const res = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail || 'Failed.')
            saveAuth(data.token, data.user)
            onSuccess()
        } catch (e) { setErr(e.message) } finally { setLoading(false) }
    }

    return (
        <form className={styles.tabForm} onSubmit={submit}>
            {!isLogin && (
                <div className={styles.field}>
                    <label>Full Name</label>
                    <input name="name" required placeholder="Your name" value={form.name} onChange={change} />
                </div>
            )}
            <div className={styles.field}>
                <label>Email Address</label>
                <input name="email" type="email" required placeholder="you@example.com" value={form.email} onChange={change} />
            </div>
            <div className={styles.field}>
                <label>Password</label>
                <input name="password" type="password" required placeholder={isLogin ? 'Your password' : 'Min. 6 characters'} value={form.password} onChange={change} />
            </div>
            {!isLogin && (
                <div className={styles.field}>
                    <label>Confirm Password</label>
                    <input name="confirm" type="password" required placeholder="Repeat password" value={form.confirm} onChange={change} />
                </div>
            )}
            {err && <div className={styles.error}>⚠️ {err}</div>}
            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '13px', marginTop: 4 }} disabled={loading}>
                {loading ? 'Please wait…' : isLogin ? '🔐 Sign In' : '🌿 Create Account'}
            </button>
        </form>
    )
}

// ── Tab: Mobile OTP ────────────────────────────────────────────────────────
function MobileTab({ mode, onSuccess }) {
    const { saveAuth } = useAuth()
    const [step, setStep] = useState('phone')  // 'phone' | 'otp'
    const [phone, setPhone] = useState('')
    const [name, setName] = useState('')
    const [otp, setOtp] = useState('')
    const [demoOtp, setDemoOtp] = useState('')
    const [err, setErr] = useState('')
    const [loading, setLoading] = useState(false)

    const sendOTP = async () => {
        if (!phone.trim()) { setErr('Enter a phone number.'); return }
        setErr(''); setLoading(true)
        try {
            const res = await fetch('/api/auth/mobile/send-otp', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, name }) })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail || 'Failed to send OTP.')
            setStep('otp')
        } catch (e) { setErr(e.message) } finally { setLoading(false) }
    }

    const verifyOTP = async () => {
        if (!otp.trim()) { setErr('Enter the OTP.'); return }
        setErr(''); setLoading(true)
        try {
            const res = await fetch('/api/auth/mobile/verify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, otp, name }) })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail || 'Verification failed.')
            saveAuth(data.token, data.user)
            onSuccess()
        } catch (e) { setErr(e.message) } finally { setLoading(false) }
    }

    return (
        <div className={styles.tabForm}>
            {step === 'phone' ? (
                <>
                    {mode === 'signup' && (
                        <div className={styles.field}>
                            <label>Your Name</label>
                            <input placeholder="Full name" value={name} onChange={e => setName(e.target.value)} />
                        </div>
                    )}
                    <div className={styles.field}>
                        <label>Mobile Number</label>
                        <div className={styles.phoneRow}>
                            <span className={styles.phoneCode}>🇮🇳 +91</span>
                            <input placeholder="10-digit number" value={phone} onChange={e => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))} style={{ flex: 1 }} />
                        </div>
                    </div>
                    {err && <div className={styles.error}>⚠️ {err}</div>}
                    <button className="btn btn-primary" style={{ width: '100%', padding: '13px' }} onClick={sendOTP} disabled={loading}>
                        {loading ? 'Sending…' : '📱 Send OTP'}
                    </button>
                </>
            ) : (
                <>
                    <div className={styles.otpSent}>
                        OTP sent to <strong>+91 {phone}</strong>
                    </div>
                    <div className={styles.otpInputs}>
                        <input
                            className={styles.otpBox}
                            maxLength={6}
                            placeholder="Enter 6-digit OTP"
                            value={otp}
                            onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                            autoFocus
                        />
                    </div>
                    {err && <div className={styles.error}>⚠️ {err}</div>}
                    <button className="btn btn-primary" style={{ width: '100%', padding: '13px' }} onClick={verifyOTP} disabled={loading || otp.length < 6}>
                        {loading ? 'Verifying…' : '✅ Verify OTP'}
                    </button>
                    <button className={styles.resend} onClick={() => { setStep('phone'); setOtp(''); setErr('') }}>
                        ← Change number
                    </button>
                </>
            )}
        </div>
    )
}

// ── Google button ──────────────────────────────────────────────────────────
function GoogleBtn() {
    return (
        <a id="google-signin-btn" href="/api/auth/google" className={styles.googleBtn}>
            <svg width="20" height="20" viewBox="0 0 48 48">
                <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
                <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
                <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
                <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
            </svg>
            Continue with Google
        </a>
    )
}

// ══════════════════════════════════════════════════════════════════════
// Main Auth Page
// ══════════════════════════════════════════════════════════════════════
export default function AuthPage({ mode = 'login', navigate }) {
    const [tab, setTab] = useState('email')     // 'email' | 'mobile'
    const [currentMode, setMode] = useState(mode)

    const onSuccess = () => navigate('home')

    return (
        <div className={styles.page}>
            {/* Background orbs */}
            <div className={styles.bg} aria-hidden>
                <div className={styles.orb1} /><div className={styles.orb2} /><div className={styles.orb3} />
            </div>

            <div className={styles.card}>
                {/* Logo */}
                <div className={styles.logo} onClick={() => navigate('home')} style={{ cursor: 'pointer' }}>
                    <span className={styles.logoLeaf}>🌿</span>
                    <span className={styles.logoText}><span style={{ color: 'var(--accent-green)' }}>Crop</span>Guard <span style={{ color: 'var(--accent-blue)', fontWeight: 500 }}>AI</span></span>
                </div>

                <h1 className={styles.title}>{currentMode === 'login' ? 'Welcome back!' : 'Create your account'}</h1>
                <p className={styles.subtitle}>{currentMode === 'login' ? 'Sign in to access your plant health dashboard.' : 'Join CropGuard AI to track and protect your crops.'}</p>

                {/* Google */}
                <GoogleBtn />

                <div className={styles.divider}><span>or continue with</span></div>

                {/* Method tabs */}
                <div className={styles.tabs}>
                    <button id="auth-tab-email" className={`${styles.tabBtn} ${tab === 'email' ? styles.tabActive : ''}`} onClick={() => setTab('email')}>
                        📧 Email
                    </button>
                    <button id="auth-tab-mobile" className={`${styles.tabBtn} ${tab === 'mobile' ? styles.tabActive : ''}`} onClick={() => setTab('mobile')}>
                        📱 Mobile OTP
                    </button>
                </div>

                {/* Tab content */}
                {tab === 'email' && <EmailTab mode={currentMode} onSuccess={onSuccess} />}
                {tab === 'mobile' && <MobileTab mode={currentMode} onSuccess={onSuccess} />}

                {/* Toggle mode */}
                <p className={styles.toggleRow}>
                    {currentMode === 'login' ? "Don't have an account?" : 'Already have an account?'}
                    <button className={styles.toggleBtn} onClick={() => setMode(m => m === 'login' ? 'signup' : 'login')}>
                        {currentMode === 'login' ? 'Sign Up' : 'Sign In'}
                    </button>
                </p>

                {/* Terms */}
                {currentMode === 'signup' && (
                    <p className={styles.terms}>
                        By creating an account you agree to our <span>Terms of Service</span> and <span>Privacy Policy</span>.
                    </p>
                )}
            </div>
        </div>
    )
}
