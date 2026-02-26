import { useState, useEffect } from 'react'
import styles from './Analytics.module.css'
import { authFetch } from '../services/api'

const API = '/api'

function StatCard({ icon, label, value, sub, color }) {
    return (
        <div className={`card ${styles.statCard}`} style={{ borderColor: color ? `${color}33` : undefined }}>
            <div className={styles.statIcon} style={{ color }}>{icon}</div>
            <div className={styles.statValue} style={{ color: color || undefined }}>{value}</div>
            <div className={styles.statLabel}>{label}</div>
            {sub && <div className={styles.statSub}>{sub}</div>}
        </div>
    )
}

function HorizBar({ label, value, max, color }) {
    const pct = max > 0 ? (value / max) * 100 : 0
    return (
        <div className={styles.hBar}>
            <div className={styles.hBarLabel}>{label}</div>
            <div className={styles.hBarTrack}>
                <div className={styles.hBarFill} style={{ width: `${pct}%`, background: color || 'var(--accent-green)' }} />
            </div>
            <div className={styles.hBarValue}>{value}</div>
        </div>
    )
}

const SEV_COLOR = { none: '#16a34a', medium: '#f59e0b', high: '#ef4444', critical: '#a78bfa' }

export default function Analytics() {
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        authFetch(`${API}/analytics`)
            .then(r => r.json())
            .then(d => { setStats(d); setLoading(false) })
            .catch(() => setLoading(false))
    }, [])

    if (loading) return <div className="page-loader"><div className="spinner" /><p>Loading analytics…</p></div>

    if (!stats || stats.total === 0) return (
        <div className={`container ${styles.page}`}>
            <h1 className="section-title">📊 Analytics Dashboard</h1>
            <div className="empty-state">
                <span style={{ fontSize: '3rem' }}>📊</span>
                <p style={{ fontWeight: 600 }}>No data yet</p>
                <p>Analyse some plants to see your dashboard populate!</p>
            </div>
        </div>
    )

    const maxDisease = stats.top_diseases?.[0]?.count || 1
    const maxDaily = Math.max(...(stats.daily_scans || []).map(d => d.count), 1)

    return (
        <div className={`container ${styles.page}`}>
            <h1 className="section-title">📊 Analytics Dashboard</h1>
            <p className="section-subtitle">An overview of all plant disease scans</p>

            {/* Top stats */}
            <div className={styles.statsGrid}>
                <StatCard icon="🔬" label="Total Scans" value={stats.total} color="var(--accent-blue)" />
                <StatCard icon="✅" label="Healthy Plants" value={stats.healthy_count}
                    sub={`${stats.healthy_pct}% of scans`} color="#16a34a" />
                <StatCard icon="🎯" label="Avg. Confidence" value={`${stats.avg_confidence}%`} color="var(--accent-green)" />
                {stats.feedback_accuracy != null
                    ? <StatCard icon="👍" label="Feedback Accuracy" value={`${stats.feedback_accuracy}%`} color="var(--accent-purple)" />
                    : <StatCard icon="💬" label="User Feedback" value="No data yet" color="var(--text-muted)" />
                }
            </div>

            <div className={styles.twoCol}>
                {/* Top Diseases */}
                <div className="card">
                    <h2 className={styles.cardTitle}>🦠 Top Diseases Detected</h2>
                    <div className={styles.chartArea}>
                        {(stats.top_diseases || []).map(d => (
                            <HorizBar key={d.disease} label={d.disease} value={d.count} max={maxDisease} color="var(--accent-red)" />
                        ))}
                    </div>
                </div>

                {/* Severity Distribution */}
                <div className="card">
                    <h2 className={styles.cardTitle}>🚦 Severity Distribution</h2>
                    <div className={styles.sevGrid}>
                        {(stats.severity_dist || []).map(s => (
                            <div key={s.severity} className={styles.sevCard} style={{ borderColor: `${SEV_COLOR[s.severity]}44` }}>
                                <div className={styles.sevCount} style={{ color: SEV_COLOR[s.severity] }}>{s.count}</div>
                                <div className={styles.sevLabel}>{s.severity}</div>
                            </div>
                        ))}
                    </div>

                    {/* Model usage */}
                    <h2 className={styles.cardTitle} style={{ marginTop: 24 }}>🤖 Model Usage</h2>
                    <div className={styles.modelBars}>
                        {(stats.model_usage || []).map(m => (
                            <div key={m.model} className={styles.modelBar}>
                                <span className={styles.modelName}>{m.model?.toUpperCase()}</span>
                                <div className={styles.mBarTrack}>
                                    <div className={styles.mBarFill}
                                        style={{ width: `${(m.count / stats.total) * 100}%`, background: m.model === 'vit' ? 'var(--accent-green)' : 'var(--accent-purple)' }} />
                                </div>
                                <span className={styles.modelCount}>{m.count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Daily scans */}
            {stats.daily_scans?.length > 0 && (
                <div className="card" style={{ marginTop: 20 }}>
                    <h2 className={styles.cardTitle}>📅 Daily Scans (Last 14 days)</h2>
                    <div className={styles.dailyChart}>
                        {[...(stats.daily_scans || [])].reverse().map(d => {
                            const h = maxDaily > 0 ? (d.count / maxDaily) * 100 : 0
                            return (
                                <div key={d.day} className={styles.dayCol}>
                                    <div className={styles.dayBarWrap}>
                                        <div className={styles.dayBar} style={{ height: `${h}%` }}>
                                            <div className={styles.dayTip}>{d.count}</div>
                                        </div>
                                    </div>
                                    <span className={styles.dayLabel}>{d.day.slice(5)}</span>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}
        </div>
    )
}
