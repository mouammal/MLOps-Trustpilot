from __future__ import annotations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
import numpy as np

def build_label_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            min_df=5, max_features=50000, ngram_range=(1,2),
            sublinear_tf=True, dtype=np.float32,
        )),
        ("clf", RandomForestClassifier(
            n_estimators=200, max_depth=None, random_state=42, n_jobs=-1
        )),
    ])

def build_score_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(min_df=3, ngram_range=(1,2))),
        ("reg", Ridge(alpha=1.0, random_state=42)),
    ])
