import logging
from typing import Dict, List, Any
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextClassifierService:
    """Servicio para clasificación de texto usando un modelo preentrenado de DistilBERT.
    """
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.classifier = None
        self._model_loaded = False

    def load_model(self) -> None:
        """Carga el modelo y el tokenizer de Hugging Face."""
        try:
            logger.info(f"Cargando modelo y tokenizer: {self.model_name}")

            # Carga del tokenizer y modelo
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            # Creación del pipeline de clasificación
            self.classifier = pipeline(
                "sentiment-analysis", 
                model=self.model, 
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device=0 if torch.cuda.is_available() else -1
            )
            self._model_loaded = True
            logger.info("Modelo y tokenizer cargados exitosamente.")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Modelo cargado en el dispositivo: {device}")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            self._model_loaded = False
            raise

    def is_model_loaded(self) -> bool:
        """Verifica si el modelo ha sido cargado correctamente."""
        return self._model_loaded
    
    def classify(self, text: str) -> List[Dict[str, Any]]:
        """
        Clasifica el texto dado y devuelve la etiqueta y la puntuación de confianza.
        Args:
            text (str): Texto a clasificar.
        Returns:
            Dict[str, Any]: Diccionario con la etiqueta y la puntuación de confianza.
        """
        if not self.is_model_loaded():
            raise RuntimeError("El modelo no ha sido cargado. Por favor, carga el modelo antes de clasificar.")
        # Clasificación del texto
        try:
            logger.info(f"Clasificando texto: {text}")
            results = self.classifier(text)
            label = results[0]["label"]
            score = results[0]["score"]
            logger.info(f"Resultado de la clasificación: {label} ({score})")
            return {"label": label, "score": score} if results else {"label": "unknown", "score": 0.0}
        except Exception as e:
            logger.error(f"Error al clasificar el texto: {e}")
            raise RuntimeError(f"Error al clasificar el texto: {e}") from e
    
    def unload_model(self) -> None:
        """Libera los recursos del modelo y el tokenizer."""
        if self.classifier is not None:
            del self.classifier
            self.classifier = None
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        self._model_loaded = False
        logger.info("Modelo y tokenizer liberados.")