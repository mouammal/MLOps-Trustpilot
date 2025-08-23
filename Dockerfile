# ---- Base slim
FROM python:3.10-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# OS deps (compilation légère pour scikit-learn) + certs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dépendances runtime (garde requirements.txt minimal côté API)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Télécharge le corpus NLTK au build (pas à l'exécution)
ENV NLTK_DATA=/usr/local/nltk_data
RUN python - <<'PY'
import nltk
nltk.download('stopwords', download_dir='/usr/local/nltk_data')
PY

# Code
COPY . .

# User non-root
RUN addgroup --system app && adduser --system --ingroup app app
RUN chown -R app:app /app
USER app

EXPOSE 8000

# Healthcheck image (Compose en définira un aussi)
HEALTHCHECK --interval=20s --timeout=4s --retries=5 --start-period=10s \
  CMD python -c "import urllib.request,sys,json; \
print('checking'); \
resp=urllib.request.urlopen('http://127.0.0.1:8000/health/ready',timeout=2); \
sys.exit(0 if json.loads(resp.read().decode()).get('status')=='ready' else 1)" || exit 1

# Lancement API (FastAPI app = api.api:api)
CMD ["uvicorn","api.api:api","--host","0.0.0.0","--port","8000","--workers","2"]
