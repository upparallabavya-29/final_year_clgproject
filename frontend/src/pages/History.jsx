import { useState, useEffect } from 'react'
import styles from './History.module.css'
import { authFetch } from '../services/api'

const API = '/api'

const SEV_CLASS = { none: 'sev-none', medium: 'sev-medium', high: 'sev-high', critical: 'sev-critical' }

const SEV_EMOJI = { none: '✅', medium: '⚠️', high: '🔴', critical: '🚨' }

export default function History() {
    const [data, setData] = useState(null)
    const [page, setPage] = useState(1)
    const [loading, setLoading] = useState(true)
    const [clearing, setClearing] = useState(false)
    const [filter, setFilter] = useState('')

    const fetchHistory = async (p = 1) => {
        setLoading(true)
        try {
            const res = await authFetch(`${API}/history?page=${p}&page_size=20`)
            const json = await res.json()
            setData(json)
            setPage(p)
        } catch { /* ignore */ } finally { setLoading(false) }
    }

    useEffect(() => { fetchHistory(1) }, [])

    const clearHistory = async () => {
        if (!confirm('Delete all scan history? This cannot be undone.')) return
        setClearing(true)
        await authFetch(`${API}/history`, { method: 'DELETE' })
        setClearing(false)
        fetchHistory(1)
    }

    const filtered = data?.scans?.filter(s =>
        !filter || s.disease.toLowerCase().includes(filter.toLowerCase()) ||
        s.crop.toLowerCase().includes(filter.toLowerCase())
    ) || []

    return (
        <div className={`container ${styles.page}`}>
            <div className={styles.header}>
                <div>
                    <h1 className="section-title">📋 Scan History</h1>
                    <p className="section-subtitle">All past plant disease analysis results</p>
                </div>
                <div className={styles.headerActions}>
                    <input
                        id="history-search"
                        type="text"
                        className={styles.search}
                        placeholder="🔍 Filter by crop or disease…"
                        value={filter}
                        onChange={e => setFilter(e.target.value)}
                    />
                    <button className="btn btn-secondary" onClick={() => fetchHistory(page)}>↺ Refresh</button>
                    <button className="btn btn-secondary" onClick={clearHistory} disabled={clearing}
                        style={{ color: '#f87171', borderColor: 'rgba(239,68,68,0.3)' }}>
                        {clearing ? 'Clearing…' : '🗑 Clear All'}
                    </button>
                </div>
            </div>

            {loading && <div className="page-loader"><div className="spinner" /><p>Loading history…</p></div>}

            {!loading && (!data || data.total === 0) && (
                <div className="empty-state">
                    <span style={{ fontSize: '3rem' }}>📋</span>
                    <p style={{ fontWeight: 600 }}>No scans yet</p>
                    <p>Go to the Detection page and analyse some plants!</p>
                </div>
            )}

            {!loading && data && data.total > 0 && (
                <>
                    <div className={styles.summary}>
                        <span>Total: <strong>{data.total}</strong> scans</span>
                        <span>Showing page <strong>{page}</strong> of <strong>{data.pages}</strong></span>
                    </div>

                    <div className={styles.tableWrapper}>
                        <table className={styles.table}>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Timestamp</th>
                                    <th>Crop</th>
                                    <th>Disease</th>
                                    <th>Confidence</th>
                                    <th>Severity</th>
                                    <th>Model</th>
                                    <th>⏱️ ms</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map(s => (
                                    <tr key={s.id} className={styles.row}>
                                        <td className={styles.id}>{s.id}</td>
                                        <td className={styles.ts}>{s.timestamp}</td>
                                        <td>{s.crop}</td>
                                        <td className={styles.disease}>{s.disease}</td>
                                        <td>
                                            <div className={styles.confCell}>
                                                <span>{s.confidence.toFixed(1)}%</span>
                                                <div className={styles.miniBar}>
                                                    <div style={{ width: `${s.confidence}%`, background: s.confidence > 80 ? 'var(--accent-green)' : s.confidence > 50 ? 'var(--accent-yellow)' : 'var(--accent-red)' }} />
                                                </div>
                                            </div>
                                        </td>
                                        <td>
                                            <span className={`badge ${SEV_CLASS[s.severity]}`}>
                                                {SEV_EMOJI[s.severity]} {s.severity}
                                            </span>
                                        </td>
                                        <td><span className={styles.model}>{s.model?.toUpperCase()}</span></td>
                                        <td className={styles.ms}>{s.inference_ms?.toFixed(1) || '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    {data.pages > 1 && (
                        <div className={styles.pagination}>
                            <button className="btn btn-secondary" disabled={page <= 1} onClick={() => fetchHistory(page - 1)}>‹ Prev</button>
                            {Array.from({ length: Math.min(data.pages, 7) }, (_, i) => {
                                const p = i + 1
                                return (
                                    <button key={p}
                                        className={`${styles.pageBtn} ${p === page ? styles.pageBtnActive : ''}`}
                                        onClick={() => fetchHistory(p)}
                                    >{p}</button>
                                )
                            })}
                            <button className="btn btn-secondary" disabled={page >= data.pages} onClick={() => fetchHistory(page + 1)}>Next ›</button>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
