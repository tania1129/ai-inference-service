import logging
import os
import sqlite3
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
from functools import lru_cache
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

from training_examples import EXAMPLES

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def train_model():
    texts, labels = zip(*EXAMPLES)
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode"),
        LogisticRegression(random_state=42),
    )
    model.fit(texts, labels)
    return model


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = train_model()
    backend = os.getenv("STORAGE_BACKEND", "sqlite")
    if backend == "firestore":
        from google.cloud import firestore

        client = firestore.Client()
        app.state.collection = client.collection("inference_logs")
        try:
            yield
        finally:
            client.close()
    elif backend == "dynamodb":
        import boto3

        app.state.table = boto3.resource("dynamodb").Table(os.environ["DYNAMODB_TABLE"])
        yield
    elif backend == "sqlite":
        path = os.getenv("SQLITE_PATH", "inference.db")
        with closing(sqlite3.connect(path)) as conn, conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS inference_logs "
                "(id TEXT PRIMARY KEY, timestamp TEXT, prediction TEXT, "
                "text_length INTEGER, model_version TEXT)"
            )
        app.state.sqlite_path = path
        yield
    else:
        raise ValueError("STORAGE_BACKEND must be sqlite, firestore, or dynamodb")


app = FastAPI(
    title="AI Cloud Inference Service",
    description="Classifies the sentiment of English product reviews.",
    version="1.0.0",
    lifespan=lifespan,
)


class InferenceRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    text_input: str = Field(min_length=1, max_length=2000)
    max_length: int = Field(default=50, ge=1, le=200)


class InferenceResponse(BaseModel):
    status: Literal["success"]
    input_text: str
    prediction: Literal["positive", "negative"]
    request_id: str


@app.get("/")
def health_check():
    return {"status": "online", "message": "AI Inference API is active."}


@app.post("/predict", response_model=InferenceResponse)
def run_inference(payload: InferenceRequest, request: Request):
    state = request.app.state
    text_used = " ".join(payload.text_input.split()[:payload.max_length])
    prediction = str(state.model.predict([text_used])[0])
    request_id = uuid4().hex
    record = {
        "timestamp": datetime.now(timezone.utc),
        "prediction": prediction,
        "text_length": len(text_used),
        "model_version": "1.0.0",
    }
    try:
        if hasattr(state, "collection"):
            state.collection.document(request_id).set(record, timeout=5, retry=None)
        elif hasattr(state, "table"):
            state.table.put_item(Item={
                **record, "request_id": request_id,
                "timestamp": record["timestamp"].isoformat(),
            })
        else:
            with closing(sqlite3.connect(state.sqlite_path)) as conn, conn:
                conn.execute(
                    "INSERT INTO inference_logs VALUES (?, ?, ?, ?, ?)",
                    (request_id, record["timestamp"].isoformat(), prediction,
                     record["text_length"], record["model_version"]),
                )
    except Exception as error:
        logger.exception("Could not save prediction metadata for %s", request_id)
        raise HTTPException(503, "Prediction storage is temporarily unavailable.") from error
    return {
        "status": "success",
        "input_text": text_used,
        "prediction": prediction,
        "request_id": request_id,
    }
