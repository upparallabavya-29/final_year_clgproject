import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import styles from './Navbar.module.css'

const NAV_ITEMS = [
    { id: 'home', path: '/', label: 'Home', icon: '🏠' },
    { id: 'detection', path: '/detection', label: 'Detect', icon: '🔬', protected: false },
    { id: 'history', path: '/history', label: 'History', icon: '📋', protected: true },
    { id: 'analytics', path: '/analytics', label: 'Analytics', icon: '📊', protected: true },
    { id: 'encyclopedia', path: '/encyclopedia', label: 'Encyclopedia', icon: '📖', protected: false },
    { id: 'contact', path: '/contact', label: 'Contact', icon: '✉️' },
]

export default function Navbar() {
    const location = useLocation()
    const navigate = useNavigate()
    const currentPageId = NAV_ITEMS.find(item => item.path === location.pathname)?.id || 'auth'
    const { user, isLoggedIn, logout } = useAuth()
    const [menuOpen, setMenuOpen] = useState(false)
    const [profileOpen, setProfileOpen] = useState(false)

    const openAuth = (mode) => navigate(`/auth?mode=${mode}`)

    const initials = user?.name
        ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
        : '?'

    return (
        <nav className={styles.navbar}>
            <div className={styles.inner}>
                {/* Logo */}
                <button className={styles.logo} onClick={() => navigate('home')}>
                    <span className={styles.logoIcon}>🌿</span>
                    <span className={styles.logoText}>
                        <span className={styles.logoGreen}>Crop</span>Guard<span className={styles.logoAI}> AI</span>
                    </span>
                </button>

                {/* Desktop nav */}
                <div className={styles.links}>
                    {NAV_ITEMS.map(item => (
                        <button
                            key={item.id}
                            className={`${styles.link} ${currentPageId === item.id ? styles.active : ''}`}
                            onClick={() => navigate(item.path)}
                        >
                            <span className={styles.linkIcon}>{item.icon}</span>
                            {item.label}
                            {item.protected && !isLoggedIn && <span className={styles.lockBadge}>🔒</span>}
                        </button>
                    ))}
                </div>

                {/* Right: auth */}
                <div className={styles.right}>
                    {isLoggedIn ? (
                        <div className={styles.profileWrap}>
                            <button className={styles.profileBtn} id="navbar-profile-btn" onClick={() => setProfileOpen(v => !v)}>
                                {user?.avatar ? (
                                    <img src={user.avatar} alt={user?.name || user?.email || 'User'} className={styles.avatar} />
                                ) : (
                                    <div className={styles.avatarInitials}>{initials}</div>
                                )}
                                <span className={styles.profileName}>
                                    {user?.name ? user.name.split(' ')[0] : (user?.email ? user.email.split('@')[0] : (user?.phone || 'User'))}
                                </span>
                                <span className={styles.profileChev}>{profileOpen ? '▲' : '▼'}</span>
                            </button>
                            {profileOpen && (
                                <div className={styles.dropdown}>
                                    <div className={styles.dropUser}>
                                        <div className={styles.dropName}>{user?.name}</div>
                                        <div className={styles.dropEmail}>{user?.email || user?.phone || user?.provider}</div>
                                    </div>
                                    <div className={styles.dropDivider} />
                                    <button className={styles.dropLink} onClick={() => { navigate('history'); setProfileOpen(false) }}>📋 Scan History</button>
                                    <button className={styles.dropLink} onClick={() => { navigate('analytics'); setProfileOpen(false) }}>📊 Analytics</button>
                                    <div className={styles.dropDivider} />
                                    <button id="navbar-logout-btn" className={`${styles.dropLink} ${styles.dropLogout}`} onClick={() => { logout(); setProfileOpen(false) }}>
                                        🚪 Sign Out
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className={styles.authBtns}>
                            <button id="navbar-signin-btn" className="btn btn-ghost" style={{ fontSize: '0.875rem', padding: '8px 14px' }} onClick={() => openAuth('login')}>
                                Sign In
                            </button>
                            <button id="navbar-signup-btn" className="btn btn-primary" style={{ fontSize: '0.875rem', padding: '9px 18px' }} onClick={() => openAuth('signup')}>
                                Sign Up Free
                            </button>
                        </div>
                    )}

                    <button className={styles.hamburger} onClick={() => setMenuOpen(v => !v)} aria-label="Toggle menu">
                        {menuOpen ? '✕' : '☰'}
                    </button>
                </div>
            </div>

            {/* Mobile drawer */}
            {menuOpen && (
                <div className={styles.drawer}>
                    {NAV_ITEMS.map(item => (
                        <button
                            key={item.id}
                            className={`${styles.drawerLink} ${currentPageId === item.id ? styles.drawerActive : ''}`}
                            onClick={() => { navigate(item.path); setMenuOpen(false) }}
                        >
                            <span>{item.icon}</span> {item.label}
                            {item.protected && !isLoggedIn && <span className={styles.lockBadge}>🔒</span>}
                        </button>
                    ))}
                    <div className={styles.drawerDivider} />
                    {isLoggedIn ? (
                        <button className={`${styles.drawerLink} ${styles.drawerLogout}`} onClick={() => { logout(); setMenuOpen(false) }}>
                            🚪 Sign Out
                        </button>
                    ) : (
                        <>
                            <button className={styles.drawerLink} onClick={() => { openAuth('login'); setMenuOpen(false) }}>🔐 Sign In</button>
                            <button className={styles.drawerLink} onClick={() => { openAuth('signup'); setMenuOpen(false) }}>🌿 Sign Up Free</button>
                        </>
                    )}
                </div>
            )}
        </nav>
    )
}
