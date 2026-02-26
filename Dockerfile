# ─── Docker image for Plant Disease Detection App ─────────────────────────
FROM python:3.11-slim

# Metadata
LABEL maintainer="Plant Disease AI Project"
LABEL description="CropGuard AI — Plant Disease Detection using ViT and Swin Transformers"

# System dependencies for OpenCV and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p checkpoints logs data \
    && chown -R appuser:appuser checkpoints logs data

# Switch to non-root user
USER appuser

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Entrypoint — run as production server
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
