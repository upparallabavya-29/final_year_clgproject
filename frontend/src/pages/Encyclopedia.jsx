import { useState, useEffect } from 'react'
import styles from './Encyclopedia.module.css'

const API = '/api'

const SEV_CLASS = { none: 'sev-none', medium: 'sev-medium', high: 'sev-high', critical: 'sev-critical' }
const SEV_LIST = ['', 'none', 'medium', 'high', 'critical']

export default function Encyclopedia() {
    const [items, setItems] = useState([])
    const [crops, setCrops] = useState([])
    const [selected, setSelected] = useState(null)
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [cropFilter, setCrop] = useState('')
    const [sevFilter, setSev] = useState('')

    const fetchItems = async () => {
        setLoading(true)
        const params = new URLSearchParams()
        if (search) params.set('search', search)
        if (cropFilter) params.set('crop', cropFilter)
        if (sevFilter) params.set('severity', sevFilter)
        try {
            const [encRes, cropRes] = await Promise.all([
                fetch(`${API}/encyclopedia?${params}`),
                fetch(`${API}/crops`),
            ])
            const enc = await encRes.json()
            const crps = await cropRes.json()
            setItems(enc.items || [])
            setCrops(crps.crops || [])
        } catch { /* ignore */ } finally { setLoading(false) }
    }

    useEffect(() => { fetchItems() }, [search, cropFilter, sevFilter])

    return (
        <div className={`container ${styles.page}`}>
            <div className={styles.header}>
                <div>
                    <h1 className="section-title">📖 Disease Encyclopedia</h1>
                    <p className="section-subtitle">
                        Browse all {items.length} disease classes with causes and treatments
                    </p>
                </div>
            </div>

            {/* Filters */}
            <div className={styles.filters}>
                <input
                    id="enc-search"
                    type="text"
                    placeholder="🔍 Search crop or disease…"
                    className={styles.searchInput}
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <select id="enc-crop" className={styles.select} value={cropFilter} onChange={e => setCrop(e.target.value)}>
                    <option value="">All Crops</option>
                    {crops.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                <select id="enc-severity" className={styles.select} value={sevFilter} onChange={e => setSev(e.target.value)}>
                    <option value="">All Severities</option>
                    {SEV_LIST.slice(1).map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                {(search || cropFilter || sevFilter) && (
                    <button className="btn btn-ghost" onClick={() => { setSearch(''); setCrop(''); setSev('') }}>
                        ✕ Clear
                    </button>
                )}
            </div>

            {loading && <div className="page-loader"><div className="spinner" /><p>Loading…</p></div>}

            {!loading && items.length === 0 && (
                <div className="empty-state">
                    <span style={{ fontSize: '3rem' }}>🔎</span>
                    <p>No diseases found matching your filters.</p>
                </div>
            )}

            {!loading && (
                <div className={styles.layout}>
                    {/* Grid */}
                    <div className={styles.grid}>
                        {items.map(item => (
                            <button
                                key={item.key}
                                className={`${styles.itemCard} ${selected?.key === item.key ? styles.itemActive : ''}`}
                                onClick={() => setSelected(item)}
                            >
                                <div className={styles.itemTop}>
                                    <span className={styles.itemCrop}>{item.crop}</span>
                                    <span className={`badge ${SEV_CLASS[item.severity]}`} style={{ fontSize: '0.7rem' }}>
                                        {item.severity_label}
                                    </span>
                                </div>
                                <div className={styles.itemDisease}>{item.disease}</div>
                            </button>
                        ))}
                    </div>

                    {/* Detail panel */}
                    {selected && (
                        <div className={styles.detail}>
                            <button className={styles.detailClose} onClick={() => setSelected(null)}>✕</button>
                            <div className={`badge ${SEV_CLASS[selected.severity]}`} style={{ marginBottom: 12 }}>
                                {selected.severity_label}
                            </div>
                            <h2 className={styles.detailDisease}>{selected.disease}</h2>
                            <p className={styles.detailCrop}>🌱 {selected.crop}</p>

                            <div className={styles.detailBlock}>
                                <h3 className={styles.detailHead}>🔍 Cause</h3>
                                <ul className={styles.detailList}>
                                    {selected.cause.map((c, i) => <li key={i}>{c}</li>)}
                                </ul>
                            </div>
                            <div className={styles.detailBlock}>
                                <h3 className={styles.detailHead}>💊 Treatment</h3>
                                <ul className={styles.detailList}>
                                    {selected.treatment.map((t, i) => <li key={i}>{t}</li>)}
                                </ul>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
