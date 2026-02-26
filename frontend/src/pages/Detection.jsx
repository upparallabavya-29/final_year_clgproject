import { useState, useCallback, useRef } from 'react'
import styles from './Detection.module.css'
import { authFetch } from '../services/api'

const API = '/api'

const SEV_CLASS = {
    none: 'sev-none',
    medium: 'sev-medium',
    high: 'sev-high',
    critical: 'sev-critical',
}

function ConfBar({ value, color }) {
    return (
        <div className={styles.confBarBg}>
            <div className={styles.confBarFill} style={{ width: `${value}%`, background: color || 'var(--accent-green)' }} />
        </div>
    )
}

export default function Detection({ navigate }) {
    const [file, setFile] = useState(null)
    const [preview, setPreview] = useState(null)
    const [model, setModel] = useState('vit')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState(null)
    const [feedback, setFeedback] = useState(null)   // 'correct' | 'wrong'
    const [fbSent, setFbSent] = useState(false)
    const [dragOver, setDragOver] = useState(false)
    const fileInput = useRef(null)

    const handleFile = (f) => {
        if (!f || !f.type.startsWith('image/')) { setError('Please select a valid image file.'); return }
        setFile(f)
        setPreview(URL.createObjectURL(f))
        setResult(null)
        setError(null)
        setFbSent(false)
        setFeedback(null)
    }

    const onDrop = useCallback(e => {
        e.preventDefault()
        setDragOver(false)
        const f = e.dataTransfer.files[0]
        if (f) handleFile(f)
    }, [])

    const onDragOver = e => { e.preventDefault(); setDragOver(true) }
    const onDragLeave = e => { e.preventDefault(); setDragOver(false) }

    const analyse = async () => {
        if (!file) { setError('Please upload a plant leaf image first.'); return }
        setLoading(true)
        setError(null)
        setResult(null)

        const fd = new FormData()
        fd.append('file', file)

        try {
            const res = await authFetch(`${API}/detect?model=${model}`, { method: 'POST', body: fd })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail || 'Detection failed.')
            setResult(data)
        } catch (e) {
            setError(e.message || 'Network error. Is the backend running?')
        } finally {
            setLoading(false)
        }
    }

    const sendFeedback = async (correct) => {
        if (!result?.scan_id || fbSent) return
        setFeedback(correct ? 'correct' : 'wrong')
        setFbSent(true)
        await authFetch(`${API}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scan_id: result.scan_id, was_correct: correct, comment: '' })
        }).catch(() => { })
    }

    const reset = () => {
        setFile(null); setPreview(null); setResult(null); setError(null)
        setFbSent(false); setFeedback(null)
    }

    return (
        <div className={`container ${styles.page}`}>
            <div className={styles.header}>
                <h1 className="section-title">🔬 Plant Disease Detection</h1>
                <p className="section-subtitle">
                    Upload a clear photo of a plant leaf to get an instant AI diagnosis.
                </p>
            </div>

            <div className={styles.layout}>
                {/* Upload panel */}
                <div className={styles.uploadPanel}>
                    {/* Drop zone */}
                    <div
                        id="detection-drop-zone"
                        className={`${styles.dropZone} ${dragOver ? styles.dragActive : ''} ${preview ? styles.hasPreview : ''}`}
                        onDrop={onDrop}
                        onDragOver={onDragOver}
                        onDragLeave={onDragLeave}
                        onClick={() => !preview && fileInput.current.click()}
                    >
                        {preview ? (
                            <div className={styles.previewWrapper}>
                                <img src={preview} alt="Uploaded plant" className={styles.previewImg} />
                                <button className={styles.previewRemove} onClick={e => { e.stopPropagation(); reset() }}>✕</button>
                                {loading && (
                                    <div className={styles.scanOverlay}>
                                        <div className={styles.scanLine} />
                                        <span>Analysing…</span>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className={styles.dropPrompt}>
                                <div className={styles.dropIcon}>📷</div>
                                <p className={styles.dropText}>Drag & drop a leaf photo here</p>
                                <p className={styles.dropSub}>or click to browse — JPG, PNG, WEBP · Max 20 MB</p>
                            </div>
                        )}
                    </div>
                    <input ref={fileInput} type="file" accept="image/*" style={{ display: 'none' }}
                        onChange={e => handleFile(e.target.files[0])} />

                    {/* Controls */}
                    <div className={styles.controls}>
                        <div className={styles.modelSelect}>
                            <label>AI Model</label>
                            <div className={styles.modelBtns}>
                                {['vit', 'swin'].map(m => (
                                    <button
                                        key={m}
                                        id={`model-${m}`}
                                        className={`${styles.modelBtn} ${model === m ? styles.modelActive : ''}`}
                                        onClick={() => setModel(m)}
                                    >
                                        {m === 'vit' ? '🧠 ViT' : '🔷 Swin'}
                                        <span className={styles.modelSub}>{m === 'vit' ? 'Base Patch16' : 'Base 224'}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            id="detection-analyse-btn"
                            className="btn btn-primary"
                            style={{ width: '100%', padding: '14px', fontSize: '1rem', marginTop: '8px' }}
                            onClick={analyse}
                            disabled={loading || !file}
                        >
                            {loading ? <><span className="spinner" style={{ width: 20, height: 20 }} /> Analysing…</> : '🔬 Analyse Disease'}
                        </button>

                        {!file && (
                            <button className="btn btn-secondary" style={{ width: '100%', marginTop: '8px', fontSize: '0.875rem' }}
                                onClick={() => fileInput.current.click()}>
                                📂 Choose File
                            </button>
                        )}
                    </div>

                    {error && (
                        <div className={styles.errorBox}>
                            <span>⚠️</span> {error}
                        </div>
                    )}
                </div>

                {/* Result panel */}
                <div className={styles.resultPanel}>
                    {!result && !loading && (
                        <div className="empty-state">
                            <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
                                <circle cx="36" cy="36" r="35" stroke="currentColor" strokeWidth="1.5" strokeDasharray="4 3" />
                                <text x="36" y="44" textAnchor="middle" fontSize="28">🌿</text>
                            </svg>
                            <p style={{ fontSize: '1rem', fontWeight: 500 }}>Awaiting Analysis</p>
                            <p style={{ fontSize: '0.875rem' }}>Upload a leaf image and click Analyse</p>
                        </div>
                    )}

                    {loading && (
                        <div className="page-loader">
                            <div className="spinner" style={{ width: 48, height: 48 }} />
                            <p>Running inference…</p>
                            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Applying {model.toUpperCase()} model</p>
                        </div>
                    )}

                    {result && !loading && (
                        <div className={`${styles.result} animate-fade-in`}>
                            {result.demo_mode && (
                                <div className={styles.demoNotice}>
                                    ⚠️ Demo mode — no trained model loaded. Showing sample result.
                                </div>
                            )}

                            {/* Top result */}
                            <div className={styles.resultTop}>
                                <div>
                                    <div className={`badge ${SEV_CLASS[result.severity]} ${styles.severityBadge}`}>
                                        {result.severity_label}
                                    </div>
                                    <h2 className={styles.resultDisease}>{result.disease}</h2>
                                    <p className={styles.resultCrop}>🌱 {result.crop}</p>
                                </div>
                                <div className={styles.confCircle}>
                                    <span className={styles.confValue}>{Math.round(result.confidence)}%</span>
                                    <span className={styles.confLabel}>confidence</span>
                                </div>
                            </div>

                            {/* Top-3 */}
                            <div className={styles.top3}>
                                <h3 className={styles.sectionHead}>Top Predictions</h3>
                                {result.top3.map((t, i) => (
                                    <div key={i} className={styles.top3Row}>
                                        <span className={styles.top3Num}>{i + 1}</span>
                                        <span className={styles.top3Name}>{t.class.replace(/___/g, ' › ').replace(/_/g, ' ')}</span>
                                        <span className={styles.top3Pct}>{(t.probability * 100).toFixed(1)}%</span>
                                        <ConfBar value={t.probability * 100} color={i === 0 ? 'var(--accent-green)' : 'var(--accent-blue)'} />
                                    </div>
                                ))}
                            </div>

                            {/* Cause */}
                            <div className={styles.infoBlock}>
                                <h3 className={styles.sectionHead}>🔍 Cause</h3>
                                <ul className={styles.infoList}>
                                    {result.cause.map((c, i) => <li key={i}>{c}</li>)}
                                </ul>
                            </div>

                            {/* Treatment */}
                            <div className={styles.infoBlock}>
                                <h3 className={styles.sectionHead}>💊 Treatment</h3>
                                <ul className={styles.infoList}>
                                    {result.treatment.map((t, i) => <li key={i}>{t}</li>)}
                                </ul>
                            </div>

                            {/* Meta */}
                            <div className={styles.meta}>
                                <span>⏱️ {result.inference_ms > 0 ? `${result.inference_ms} ms` : 'Demo'}</span>
                                <span>🤖 {result.model.toUpperCase()}</span>
                                {result.scan_id && <span>🆔 Scan #{result.scan_id}</span>}
                            </div>

                            {/* Feedback */}
                            {result.scan_id && (
                                <div className={styles.feedback}>
                                    <p>Was this diagnosis correct?</p>
                                    <div className={styles.feedbackBtns}>
                                        <button
                                            id="feedback-correct"
                                            className={`${styles.fbBtn} ${feedback === 'correct' ? styles.fbCorrect : ''}`}
                                            onClick={() => sendFeedback(true)} disabled={fbSent}
                                        >👍 Yes</button>
                                        <button
                                            id="feedback-wrong"
                                            className={`${styles.fbBtn} ${feedback === 'wrong' ? styles.fbWrong : ''}`}
                                            onClick={() => sendFeedback(false)} disabled={fbSent}
                                        >👎 No</button>
                                    </div>
                                    {fbSent && <p className={styles.fbThanks}>Thanks for your feedback! 🙏</p>}
                                </div>
                            )}

                            <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                                <button className="btn btn-secondary" style={{ flex: 1 }} onClick={reset}>🔄 New Scan</button>
                                <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => navigate('history')}>📋 View History</button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
