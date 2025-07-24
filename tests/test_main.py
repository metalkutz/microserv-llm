import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Análisis de Sentimientos" in response.json()["message"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]

def test_model_loaded(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "model_loaded" in data
    assert isinstance(data["model_loaded"], bool)
    assert "device" in data
    assert data["device"] in ["cuda", "cpu"]

def test_predict_sentiment_positive(client):
    payload = {"text": "I love this product!"}
    response = client.post("/predict_sentiment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "score" in data
    assert data["label"] in ["POSITIVE", "NEGATIVE"]


def test_predict_sentiment_negative(client):
    payload = {"text": "I hate this experience."}
    response = client.post("/predict_sentiment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "score" in data
    assert data["label"] in ["POSITIVE", "NEGATIVE"]


def test_predict_sentiment_empty_text(client):
    payload = {"text": ""}
    response = client.post("/predict_sentiment", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_predict_sentiment_long_text(client):
    payload = {"text": "a" * 513}
    response = client.post("/predict_sentiment", json=payload)
    assert response.status_code == 422  # Pydantic validation error


def test_predict_sentiment_missing_text(client):
    response = client.post("/predict_sentiment", json={})
    assert response.status_code == 422  # Pydantic validation error


def test_predict_sentiment_non_string(client):
    payload = {"text": 12345}
    response = client.post("/predict_sentiment", json=payload)
    assert response.status_code == 422  # Pydantic validation error
