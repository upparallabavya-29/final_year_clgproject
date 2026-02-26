import styles from './Footer.module.css'

export default function Footer() {
    return (
        <footer className={styles.footer}>
            <div className="container">
                <div className={styles.footerContent}>
                    <div className={styles.brand}>
                        <span className={styles.logo}>🌿 CropGuard AI</span>
                        <p>Advanced plant disease detection powered by Vision Transformers. Protect your crops with state-of-the-art AI.</p>
                    </div>

                    <div className={styles.links}>
                        <div className={styles.linkGroup}>
                            <h4>Analysis</h4>
                            <a href="/detection">Disease Detection</a>
                            <a href="/encyclopedia">Encyclopedia</a>
                            <a href="/history">Your Scans</a>
                        </div>
                        <div className={styles.linkGroup}>
                            <h4>Project</h4>
                            <a href="#">About Us</a>
                            <a href="/contact">Contact</a>
                            <a href="#">Privacy Policy</a>
                        </div>
                    </div>
                </div>

                <div className={styles.bottom}>
                    <p>&copy; {new Date().getFullYear()} CropGuard AI. All rights reserved.</p>
                    <div className={styles.models}>
                        <span>Powered by ViT & Swin Transformers</span>
                    </div>
                </div>
            </div>
        </footer>
    )
}
