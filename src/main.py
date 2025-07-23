import logging
from contextlib import asynccontextmanager

import uvicorn
import torch

from fastapi import FastAPI
from pydantic import BaseModel, Field
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    pipeline 
)

# configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# variables globales 
model = None
tokenizer = None
classifier = None

# modelo de datos Pydantic
class TextRequest(BaseModel):
    text: str = Field(..., 
                      min_length=1, 
                      max_length=512,
                      description="Texto a clasificar"
                      )

class SentimentResponse(BaseModel):
    label: str = Field(..., description="Etiqueta de sentimiento")
    score: float = Field(..., description="Puntuación de confianza")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado del servicio")
    model_loaded: bool = Field(..., description="Estado de carga del modelo")
    device: str = Field(..., description="Dispositivo en uso (cuda/cpu)")

# contexto de la aplicación para cargar el modelo al inicio
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer, classifier
    try:
        logger.info("Cargando modelo y tokenizer...")
        tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        classifier = pipeline(
            "sentiment-analysis", 
            model=model, 
            tokenizer=tokenizer, 
            # return_all_scores=True,
            # top_k=None,
            # truncation=True,
            # max_length=512,
            # padding=True,
            # batch_size=8,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device=0 if torch.cuda.is_available() else -1
        )
        # poner el modelo en modo evaluación
        model.eval()  
        logger.info("Modelo y tokenizer cargados correctamente.")
        yield
    finally:
        logger.info("Limpieza de recursos...")
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        del model
        del tokenizer
        del classifier
        logger.info("Recursos liberados.")

# crear la aplicación FastAPI
app = FastAPI(
    title="API para Análisis de Sentimientos con DistilBERT",
    description="Esta API permite clasificar el sentimiento de textos en inglés utilizando un modelo DistilBERT",
    version="1.0.0",
    lifespan=lifespan
)

# Endpoint raíz 
@app.get("/", tags=["root"])
async def root():
    """
    Endpoint raíz.
    - **return**: Mensaje de bienvenida
    """
    return {"message": "Microservicio de Análisis de Sentimientos con DistilBERT en FastAPI"}

# Endpoint de salud para verificar el estado del servicio
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica el estado del servicio.
    - **return**: Objeto con el estado del servicio
    """
    logger.info("Verificando estado del servicio...")
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        device="cuda" if torch.cuda.is_available() and model is not None else "cpu"
    )

# Endpoint para clasificar el sentimiento de un texto
@app.post("/predict_sentiment", response_model=SentimentResponse)
async def predict_sentiment(request: TextRequest):
    """
    Clasifica el sentimiento de un texto dado (en inglés).
    - **request**: Objeto que contiene el texto a clasificar.
    - **return**: Objeto con la etiqueta de sentimiento y la puntuación de confianza
    """
    global classifier

    if classifier is None:
        logger.error("El clasificador no está disponible. Asegúrate de que el modelo se ha cargado correctamente.")
        raise RuntimeError("El clasificador no está disponible. Asegúrate de que el modelo se ha cargado correctamente.")
    if not request.text:
        logger.error("El texto proporcionado está vacío.")
        raise ValueError("El texto proporcionado está vacío.")
    if len(request.text) > 512:
        logger.error("El texto proporcionado excede el límite de 512 caracteres.")
        raise ValueError("El texto proporcionado excede el límite de 512 caracteres.")
    if not isinstance(request.text, str):
        logger.error("El texto proporcionado no es una cadena de caracteres.")
        raise TypeError("El texto proporcionado debe ser una cadena de caracteres.")
    try:
        # clasificar el texto
        logger.info(f"Clasificando texto: {request.text}")
        result = classifier(request.text)
        print("resultado de la clasificación:", result)
        label = result[0]["label"]
        score = result[0]["score"]
        logger.info(f"Resultado de la clasificación: {label} ({score})")
        return SentimentResponse(label=label, score=score)
    except Exception as e:
        logger.error(f"Error al clasificar el texto: {e}")
        raise RuntimeError(f"Error al clasificar el texto: {e}") from e

def start_server():
    """
    Inicia el servidor FastAPI.
    """
    logger.info("Iniciando el servidor FastAPI...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000
    )

# Ejecutar la aplicación
if __name__ == "__main__":
    start_server()