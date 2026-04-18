FROM python:3.11-slim

# System dependencies for WeasyPrint (Cairo, Pango, GDK-PixBuf) and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libharfbuzz0b \
    libharfbuzz-subset0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libjpeg-dev \
    shared-mime-info \
    fonts-liberation \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Non-root user required by HF Spaces
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install Python dependencies before copying source (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY --chown=appuser:appuser . .

USER appuser

# HF Spaces default port
EXPOSE 7860

# Streamlit must bind to 7860; FastAPI subprocess binds internally to 8000
ENV FASTAPI_HOST=0.0.0.0
ENV FASTAPI_PORT=8000
ENV FASTAPI_BASE_URL=http://localhost:8000
ENV PYTHONPATH=/app

CMD ["streamlit", "run", "app/main.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
