import { useState } from 'react'
import styles from './Contact.module.css'

const API = '/api'

export default function Contact() {
    const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' })
    const [sending, setSending] = useState(false)
    const [success, setSuccess] = useState(false)
    const [error, setError] = useState(null)

    const change = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

    const submit = async e => {
        e.preventDefault()
        setSending(true); setError(null)
        try {
            const res = await fetch(`${API}/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form),
            })
            const data = await res.json()
            if (!res.ok) throw new Error(data.detail || 'Failed to send.')
            setSuccess(true)
            setForm({ name: '', email: '', subject: '', message: '' })
        } catch (err) {
            setError(err.message)
        } finally { setSending(false) }
    }

    return (
        <div className={`container ${styles.page}`}>
            <div className={styles.layout}>
                {/* Info */}
                <div className={styles.info}>
                    <h1 className="section-title">✉️ Get in Touch</h1>
                    <p className="section-subtitle">
                        Have a question about CropGuard AI, found a bug, or want to collaborate? We'd love to hear from you.
                    </p>

                    <div className={styles.contactItems}>
                        {[
                            { icon: '📧', label: 'Email', val: 'cropguardai@example.com' },
                            { icon: '🌐', label: 'Project', val: 'final_year_clgproject' },
                            { icon: '🤖', label: 'Models', val: 'ViT-Base + Swin-Base (PlantVillage)' },
                            { icon: '🗓️', label: 'Dataset', val: '87K+ images, 38 classes, 14 crops' },
                        ].map(c => (
                            <div key={c.label} className={styles.contactItem}>
                                <span className={styles.ciIcon}>{c.icon}</span>
                                <div>
                                    <div className={styles.ciLabel}>{c.label}</div>
                                    <div className={styles.ciVal}>{c.val}</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className={styles.team}>
                        <h3 className={styles.teamTitle}>🎓 Team & Project</h3>
                        <p className={styles.teamDesc}>
                            CropGuard AI is a final-year college project leveraging state-of-the-art Vision Transformer (ViT) and Swin Transformer architectures
                            for plant disease detection. Built with FastAPI, React, and PyTorch.
                        </p>
                    </div>
                </div>

                {/* Form */}
                <div className={styles.formCard}>
                    {success ? (
                        <div className={styles.successBox}>
                            <div className={styles.successIcon}>✅</div>
                            <h2>Message Sent!</h2>
                            <p>Thanks for reaching out. We'll get back to you soon.</p>
                            <button className="btn btn-primary" onClick={() => setSuccess(false)} style={{ marginTop: 16 }}>
                                Send Another
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={submit} className={styles.form}>
                            <h2 className={styles.formTitle}>Send a Message</h2>

                            <div className={styles.row2}>
                                <div className={styles.field}>
                                    <label htmlFor="contact-name">Full Name *</label>
                                    <input id="contact-name" name="name" required value={form.name} onChange={change}
                                        placeholder="Your name" />
                                </div>
                                <div className={styles.field}>
                                    <label htmlFor="contact-email">Email *</label>
                                    <input id="contact-email" type="email" name="email" required value={form.email} onChange={change}
                                        placeholder="you@example.com" />
                                </div>
                            </div>

                            <div className={styles.field}>
                                <label htmlFor="contact-subject">Subject</label>
                                <input id="contact-subject" name="subject" value={form.subject} onChange={change}
                                    placeholder="What's this about?" />
                            </div>

                            <div className={styles.field}>
                                <label htmlFor="contact-message">Message *</label>
                                <textarea id="contact-message" name="message" required value={form.message} onChange={change}
                                    rows={6} placeholder="Write your message here…" />
                            </div>

                            {error && (
                                <div className={styles.errorBox}><span>⚠️</span> {error}</div>
                            )}

                            <button id="contact-submit" type="submit" className="btn btn-primary"
                                style={{ width: '100%', padding: '14px', fontSize: '1rem' }}
                                disabled={sending}>
                                {sending ? 'Sending…' : '📤 Send Message'}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    )
}
