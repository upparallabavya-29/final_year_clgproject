import { useState, useEffect } from 'react'
import styles from './Home.module.css'
import { authFetch } from '../services/api'

const FEATURES = [
    {
        icon: '🔬',
        title: 'Dual Transformer Models',
        desc: 'Choose between Vision Transformer (ViT) and Swin Transformer for best accuracy.'
    },
    {
        icon: '⚡',
        title: 'Instant Diagnosis',
        desc: 'Real-time inference in milliseconds — upload a leaf photo and get results.'
    },
    {
        icon: '💊',
        title: 'Treatment Guidance',
        desc: 'Detailed cause analysis and actionable treatment plans for every disease.'
    },
    {
        icon: '📊',
        title: 'Scan Analytics',
        desc: 'Track your scan history and view disease patterns with interactive dashboards.'
    },
    {
        icon: '📖',
        title: 'Disease Encyclopedia',
        desc: 'Browse all 38 plant disease classes with rich descriptions and severity ratings.'
    },
    {
        icon: '🌍',
        title: 'Multi-language Support',
        desc: 'Available in English, Hindi, and Telugu for wider accessibility.'
    },
]

export default function Home({ navigate }) {
    const [stats, setStats] = useState([
        { value: '38', label: 'Disease Classes', icon: '🦠' },
        { value: '87K+', label: 'Training Images', icon: '🖼️' },
        { value: '14', label: 'Crop Species', icon: '🌾' },
        { value: '2', label: 'AI Models', icon: '🤖' },
    ]);
    const [crops, setCrops] = useState([]);

    useEffect(() => {
        authFetch('/api/stats/summary').then(res => res.json()).then(data => {
            if (data.total_scans !== undefined) {
                setStats([
                    { value: '38', label: 'Disease Classes', icon: '🦠' },
                    { value: `${data.total_scans}+`, label: 'Total Analyses', icon: '🖼️' },
                    { value: '14', label: 'Crop Species', icon: '🌾' },
                    { value: `${data.total_users || 0}`, label: 'Active Users', icon: '👤' },
                ]);
            }
        }).catch(console.error);

        const cropImages = {
            'Apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6caa6?w=200&h=200&fit=crop',
            'Blueberry': 'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=200&h=200&fit=crop',
            'Cherry': 'https://images.unsplash.com/photo-1528821128474-27f963b062bf?w=200&h=200&fit=crop',
            'Corn (Maize)': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=200&h=200&fit=crop',
            'Grape': 'https://images.unsplash.com/photo-1596369526145-81206c279c6d?w=200&h=200&fit=crop',
            'Orange': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=200&h=200&fit=crop',
            'Peach': 'https://images.unsplash.com/photo-1595163539873-1f1969a532d8?w=200&h=200&fit=crop',
            'Bell Pepper': 'https://images.unsplash.com/photo-1563514227147-6d2ff665a6a0?w=200&h=200&fit=crop',
            'Potato': 'https://images.unsplash.com/photo-1518977676601-b552317beff2?w=200&h=200&fit=crop',
            'Raspberry': 'https://images.unsplash.com/photo-1577069861033-55d04cec4f18?w=200&h=200&fit=crop',
            'Soybean': 'https://images.unsplash.com/photo-1582239423984-babbcb06cb23?w=200&h=200&fit=crop',
            'Squash': 'https://images.unsplash.com/photo-1570586437263-ab629fccc818?w=200&h=200&fit=crop',
            'Strawberry': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=200&h=200&fit=crop',
            'Tomato': 'https://images.unsplash.com/photo-1518977822557-013b5e4c0ba6?w=200&h=200&fit=crop',
        };

        const getImageUrl = (name) => cropImages[name] || 'https://images.unsplash.com/photo-1581881067986-2a6230f73fdd?w=200&h=200&fit=crop';

        authFetch('/api/crops').then(res => res.json()).then(data => {
            if (data && Array.isArray(data.crops)) {
                setCrops(data.crops.map(c => ({ name: c, image: getImageUrl(c) })));
            } else if (Array.isArray(data)) {
                setCrops(data.map(c => ({ name: c.name || c, image: getImageUrl(c.name || c) })));
            }
        }).catch(console.error);
    }, []);

    return (
        <div className={styles.page}>
            {/* Hero */}
            <section className={styles.hero}>
                <div className={styles.heroBg} aria-hidden="true">
                    <div className={styles.orb1} />
                    <div className={styles.orb2} />
                    <div className={styles.orb3} />
                </div>
                <div className={`container ${styles.heroContent}`}>
                    <div className={`badge ${styles.heroBadge}`}>
                        <span>🌿</span> AI-Powered Plant Health
                    </div>
                    <h1 className={styles.heroTitle}>
                        Detect Plant Diseases<br />
                        <span className={styles.heroAccent}>Instantly with AI</span>
                    </h1>
                    <p className={styles.heroDesc}>
                        Upload a leaf photo — our Vision Transformer models diagnose 38 disease classes across
                        14 crop species and provide expert treatment recommendations in seconds.
                    </p>
                    <div className={styles.heroBtns}>
                        <button id="home-detect-btn" className="btn btn-primary" onClick={() => navigate('detection')}
                            style={{ padding: '14px 32px', fontSize: '1rem' }}>
                            🔬 Analyse Now — It's Free
                        </button>
                        <button id="home-enc-btn" className="btn btn-secondary" onClick={() => navigate('encyclopedia')}
                            style={{ padding: '14px 28px', fontSize: '1rem' }}>
                            📖 Browse Encyclopedia
                        </button>
                    </div>

                    {/* Stats */}
                    <div className={styles.stats}>
                        {stats.map((s, i) => (
                            <div key={s.label} className={`${styles.stat} animate-fade-in-up`} style={{ animationDelay: `${0.6 + i * 0.1}s` }}>
                                <span className={styles.statIcon}>{s.icon}</span>
                                <span className={styles.statValue}>{s.value}</span>
                                <span className={styles.statLabel}>{s.label}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Crops */}
            <section className={styles.crops}>
                <div className="container">
                    <h2 className="section-title" style={{ textAlign: 'center' }}>Supported Crops</h2>
                    <p className="section-subtitle" style={{ textAlign: 'center' }}>14 crop species supported on the PlantVillage dataset</p>
                    <div className={styles.cropGrid}>
                        {crops.length > 0 ? crops.map((c, i) => (
                            <div key={c.name} className={`${styles.cropCard} animate-zoom-in`} style={{ animationDelay: `${i * 0.05}s` }}>
                                <img src={c.image} alt={c.name} className={styles.cropImg} loading="lazy" />
                                <span className={styles.cropName}>{c.name}</span>
                            </div>
                        )) : (
                            <div style={{ gridColumn: '1 / -1', textAlign: 'center', color: 'var(--text-muted)' }}>Loading crops...</div>
                        )}
                    </div>
                </div>
            </section>

            {/* Features */}
            <section className={styles.features}>
                <div className="container">
                    <h2 className="section-title" style={{ textAlign: 'center' }}>Why CropGuard AI?</h2>
                    <p className="section-subtitle" style={{ textAlign: 'center' }}>
                        Production-grade plant pathology — powered by state-of-the-art transformer models.
                    </p>
                    <div className={styles.featureGrid}>
                        {FEATURES.map((f, i) => (
                            <div key={f.title} className="card animate-fade-in-up" style={{ animationDelay: `${i * 0.1}s` }}>
                                <div className={styles.featureIcon}>{f.icon}</div>
                                <h3 className={styles.featureTitle}>{f.title}</h3>
                                <p className={styles.featureDesc}>{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA banner */}
            <section className={styles.cta}>
                <div className="container">
                    <div className={styles.ctaBox}>
                        <div className={styles.ctaOrb} aria-hidden="true" />
                        <h2 className={styles.ctaTitle}>Ready to protect your crops?</h2>
                        <p className={styles.ctaDesc}>
                            Upload your first plant leaf image and get an instant AI-powered diagnosis with treatment plan.
                        </p>
                        <button id="home-cta-bottom" className="btn btn-primary" onClick={() => navigate('detection')}
                            style={{ padding: '14px 36px', fontSize: '1rem' }}>
                            🌿 Start Free Analysis
                        </button>
                    </div>
                </div>
            </section>
        </div>
    )
}
