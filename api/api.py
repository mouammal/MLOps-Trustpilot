# api/api.py
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from contextlib import asynccontextmanager
from api.schemas import PredictText, PredictLabelResponse, PredictScoreResponse
from api.security.permissions import require_role
from fastapi.security import OAuth2PasswordRequestForm
from api.security.auth import authenticate_user, create_access_token
import time 
import hashlib 
import os 
import platform 
import uuid
from pathlib import Path
import sklearn 
import fastapi 
import joblib
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from src.utils.logging import setup_logging, get_logger, log_event


START_TS = time.time()
LABEL_MODEL_PATH = os.getenv("LABEL_MODEL_PATH", "models/random_forest/model.joblib")
SCORE_MODEL_PATH = os.getenv("SCORE_MODEL_PATH", "models/linear_regression/model.joblib")

REQ_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method","endpoint","status"])
REQ_LAT   = Histogram("http_request_duration_seconds", "Request latency (s)", ["endpoint"])
PRED_LAT  = Histogram("prediction_duration_seconds", "Model prediction latency (s)", ["endpoint","model"])

def _file_meta(p: str):
    path = Path(p)
    info = {"exists": path.exists(), "path": p}
    if path.exists():
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        info.update({
            "size_bytes": path.stat().st_size,
            "modified": path.stat().st_mtime,
            "sha256": h.hexdigest(),
        })
    return info

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Setup logging au démarrage
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))
    app.state.logger = get_logger("api")
    app.state.logger.info("API starting")

    # ---- Charger modèles + métadonnées
    app.state.label_model = joblib.load(LABEL_MODEL_PATH)
    app.state.score_model = joblib.load(SCORE_MODEL_PATH)
    app.state.label_meta = _file_meta(LABEL_MODEL_PATH)
    app.state.score_meta = _file_meta(SCORE_MODEL_PATH)
    yield

api = FastAPI(title="Trustpilot ML API", version="v1", lifespan=lifespan)

@api.get("/")
def home():
    return {"message": "Bienvenue sur l'API de traitement d'avis de Trustpilot !"}

@api.get("/health")
def health():
    return {
        "status": "ok",
        "label_model": os.path.exists(LABEL_MODEL_PATH),
        "score_model": os.path.exists(SCORE_MODEL_PATH),
        "paths": {"label": LABEL_MODEL_PATH, "score": SCORE_MODEL_PATH},
    }

@api.get("/health/live")
def health_live():
    return {"status": "alive", "uptime_s": round(time.time() - START_TS, 2)}

@api.get("/health/ready")
def health_ready():
    ready = api.state.label_meta.get("exists") and api.state.score_meta.get("exists")
    return {
        "status": "ready" if ready else "degraded",
        "models": {"label": api.state.label_meta, "score": api.state.score_meta},
        "versions": {
            "python": platform.python_version(),
            "fastapi": fastapi.__version__,
            "sklearn": sklearn.__version__,
        },
        "uptime_s": round(time.time() - START_TS, 2),
    }

@api.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

# -------- Middleware LOGS (avec X-Request-ID) --------
@api.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    t0 = time.time()
    logger = getattr(api.state, "logger", get_logger("api"))
    try:
        response: Response = await call_next(request)
        latency_ms = round((time.time() - t0) * 1000, 2)
        response.headers["X-Request-ID"] = req_id
        log_event(
            logger,
            event="http",
            request_id=req_id,
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            latency_ms=latency_ms,
        )
        return response
    except Exception as e:
        latency_ms = round((time.time() - t0) * 1000, 2)
        log_event(
            logger,
            event="http_error",
            request_id=req_id,
            method=request.method,
            path=request.url.path,
            error=str(e),
            latency_ms=latency_ms,
        )
        raise

# -------- Middleware METRICS --------
@api.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    REQ_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    REQ_LAT.labels(request.url.path).observe(elapsed)
    return response

@api.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@api.post("/predict-label", response_model=PredictLabelResponse)
def predict_label(payload: PredictText, request: Request, _: None = Depends(require_role("client","admin"))):
    t0 = time.time()
    pred = api.state.label_model.predict([payload.text])[0]
    elapsed = time.time() - t0
    PRED_LAT.labels("/predict-label","label").observe(elapsed)
    # log prédiction
    logger = getattr(api.state, "logger", get_logger("api"))
    log_event(
        logger,
        event="predict",
        endpoint="/predict-label",
        model="label",
        text_len=len(payload.text),
        latency_ms=round(elapsed * 1000, 2),
        ok=True,
        request_id=request.headers.get("X-Request-ID"),
    )
    return {"label": str(pred), "model_version": LABEL_MODEL_PATH}

@api.post("/predict-score", response_model=PredictScoreResponse)
def predict_score(payload: PredictText, request: Request, _: None = Depends(require_role("admin"))):
    t0 = time.time()
    score = float(api.state.score_model.predict([payload.text])[0])
    clipped_score = max(0, min(5, score))
    elapsed = time.time() - t0
    PRED_LAT.labels("/predict-score","score").observe(elapsed)
    # log prédiction
    logger = getattr(api.state, "logger", get_logger("api"))
    log_event(
        logger,
        event="predict",
        endpoint="/predict-score",
        model="score",
        text_len=len(payload.text),
        latency_ms=round(elapsed * 1000, 2),
        ok=True,
        request_id=request.headers.get("X-Request-ID"),
    )
    return {"score": clipped_score, "model_version": SCORE_MODEL_PATH}
