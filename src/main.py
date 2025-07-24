import logging
from contextlib import asynccontextmanager

import uvicorn
import torch

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from .model_service import TextClassifierService

# configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# modelo de datos Pydantic
class TextRequest(BaseModel):
    text: str = Field(..., 
                      min_length=1, 
                      max_length=512,
                      description="Texto a clasificar",
                      examples=["I love this product!"]
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
    try:
        logger.info("Cargando modelo y servicio de clasificación...")
        classification_service = TextClassifierService()
        # Cargar el modelo y el tokenizer
        if not classification_service.is_model_loaded():
            classification_service.load_model()

        # Asignar el modelo y el clasificador a variables globales
        app.state.classification_service = classification_service
        app.state.classifier = classification_service.classifier
        app.state.model = classification_service.model

        logger.info("Modelo y servicio de clasificación cargados correctamente.")
        yield
    finally:
        logger.info("Limpieza de recursos...")
        if hasattr(app.state, 'classification_service'):
            app.state.classification_service.unload_model()
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
    model_loaded = hasattr(app.state, 'model') and app.state.model is not None

    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded,
        device="cuda" if torch.cuda.is_available() and model_loaded else "cpu"
    )

def get_classifier():
    if not hasattr(app.state, 'classifier') or app.state.classifier is None:
        raise HTTPException(
            status_code=503, 
            detail="Clasificador no disponible. Modelo no cargado."
        )
    return app.state.classifier

# Endpoint para clasificar el sentimiento de un texto
@app.post("/predict_sentiment", response_model=SentimentResponse)
async def predict_sentiment(
    request: TextRequest, 
    classifier = Depends(get_classifier)
):
    """
    Clasifica el sentimiento de un texto dado (en inglés).
    - **request**: Objeto que contiene el texto a clasificar.
    - **return**: Objeto con la etiqueta de sentimiento y la puntuación de confianza
    """

    try:
        # clasificar el texto
        logger.info(f"Clasificando texto: {request.text}")
        result = classifier(request.text)
        label = result[0].get("label", "unknown")
        score = result[0].get("score", 0.0)

        return SentimentResponse(label=label, score=score)
    
    except Exception as e:
        logger.error(f"Error al clasificar el texto: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al clasificar el texto: {str(e)}"
        )

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