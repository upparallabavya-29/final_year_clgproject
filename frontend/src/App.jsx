import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, useSearchParams } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ErrorBoundary from './components/ErrorBoundary'
import Home from './pages/Home'
import Detection from './pages/Detection'
import History from './pages/History'
import Analytics from './pages/Analytics'
import Encyclopedia from './pages/Encyclopedia'
import Contact from './pages/Contact'
import AuthPage from './pages/AuthPage'

function ProtectedRoute({ children }) {
  const { isLoggedIn, loading } = useAuth()
  const location = useLocation()

  if (loading) return null; // or a loading spinner

  if (!isLoggedIn) {
    return <Navigate to={`/auth?mode=signup&redirect=${encodeURIComponent(location.pathname)}`} replace />
  }
  return children
}

function PageWrapper({ Component }) {
  // Adapter for pages that still expect `navigate` prop
  // so we don't have to rewrite every single page component right now
  const navigate = useNavigate()
  const urlNavigate = (path) => {
    if (path === 'home') navigate('/')
    else navigate(`/${path}`)
  }
  return <Component navigate={urlNavigate} />
}

export default function App() {
  return (
    <ErrorBoundary>
      <Toaster position="bottom-right" />
      <AuthProvider>
        <BrowserRouter>
          <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Navbar />
            <main style={{ flex: 1 }}>
              <Routes>
                <Route path="/" element={<PageWrapper Component={Home} />} />

                {/* Public Routes */}
                <Route path="/detection" element={<PageWrapper Component={Detection} />} />
                <Route path="/encyclopedia" element={<PageWrapper Component={Encyclopedia} />} />
                <Route path="/contact" element={<PageWrapper Component={Contact} />} />

                <Route path="/auth" element={<AuthRouteWrapper />} />
                <Route path="/auth/callback" element={<OAuthCallback />} />

                {/* Protected Routes */}
                <Route path="/history" element={
                  <ProtectedRoute>
                    <PageWrapper Component={History} />
                  </ProtectedRoute>
                } />
                <Route path="/analytics" element={
                  <ProtectedRoute>
                    <PageWrapper Component={Analytics} />
                  </ProtectedRoute>
                } />

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}

function AuthRouteWrapper() {
  const [searchParams] = useSearchParams()
  const mode = searchParams.get('mode') || 'login'
  return <PageWrapper Component={(props) => <AuthPage mode={mode} {...props} />} />
}

function OAuthCallback() {
  const navigate = useNavigate()
  // AuthContext handles token extraction in the background. Navigate gracefully away short after.
  useEffect(() => {
    const timer = setTimeout(() => navigate('/'), 500)
    return () => clearTimeout(timer)
  }, [navigate])

  return (
    <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
      <h2>🌱 Signing you in...</h2>
      <p>Securely connecting to CropGuard AI.</p>
    </div>
  )
}
