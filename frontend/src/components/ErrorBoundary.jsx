import React from 'react'
import styles from './ErrorBoundary.module.css'

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null }
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error }
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo)
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className={styles.errorContainer}>
                    <div className={styles.errorCard}>
                        <h2>Oops! Something went wrong.</h2>
                        <p>We're sorry, but the application encountered an unexpected error.</p>
                        <button className="btn btn-primary" onClick={() => window.location.reload()}>
                            Reload Page
                        </button>
                    </div>
                </div>
            )
        }
        return this.props.children
    }
}

export default ErrorBoundary
