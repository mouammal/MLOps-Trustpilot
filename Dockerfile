# ---- Base image ----
FROM python:3.10-slim AS runtime

# ---- Environment variables ----
# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ---- OS dependencies ----
# Install minimal packages needed for building Python packages (scikit-learn, cryptography, etc.)
# Also installs git, curl, and certificates for downloads
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    cmake \
    git \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Python dependencies ----
# Copy only requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- NLTK data download ----
# Download stopwords corpus at build time, not runtime
ENV NLTK_DATA=/usr/local/nltk_data
RUN python - <<'PY'
import nltk
nltk.download('stopwords', download_dir='/usr/local/nltk_data')
PY

# ---- Copy application code ----
COPY . .

# ---- Non-root user setup ----
# Create a system user 'app' and make them owner of /app
RUN addgroup --system app && adduser --system --ingroup app app
RUN chown -R app:app /app
USER app

# ---- Expose API port ----
EXPOSE 8000

# ---- Healthcheck ----
# Used by Docker / Docker Compose to verify container readiness
HEALTHCHECK --interval=20s --timeout=4s --retries=5 --start-period=10s \
  CMD python -c "import urllib.request,sys,json; \
                print('checking'); \
                resp=urllib.request.urlopen('http://127.0.0.1:8000/health/ready',timeout=2); \
                sys.exit(0 if json.loads(resp.read().decode()).get('status')=='ready' else 1)" || exit 1

# ---- Launch API ----
# FastAPI application entrypoint (assumes api.api:api)
CMD ["uvicorn","api.api:api","--host","0.0.0.0","--port","8000","--workers","2"]
