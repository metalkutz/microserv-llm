import pytest
from src.model_service import TextClassifierService

@pytest.fixture(scope="session")
def text_classifier_service():
    """Fixture para inicializar el servicio de clasificación de texto."""
    service = TextClassifierService()
    service.load_model()
    yield service

def test_model_loading(text_classifier_service):
    """Test para verificar que el modelo se carga correctamente."""
    assert text_classifier_service.is_model_loaded() is True

def test_classify_text_positive(text_classifier_service):
    """Test para clasificar un texto positivo."""
    text = "I love this product!"
    result = text_classifier_service.classify(text)
    assert result["label"] == "POSITIVE"
    assert 0 <= result["score"] <= 1

def test_classify_text_negative(text_classifier_service):
    """Test para clasificar un texto negativo."""
    text = "I hate this product!"
    result = text_classifier_service.classify(text)
    assert result["label"] == "NEGATIVE"
    assert 0 <= result["score"] <= 1
