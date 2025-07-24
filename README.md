# Microservicio LLM para Análisis de Sentimientos

Microservicio de inferencia para clasificación de sentimientos usando el modelo DistilBERT, desarrollado con FastAPI y preparado para despliegue en AWS EKS (Elastic Kubernetes Service).

## Contenido

- [Descripción](#descripción)
- [Inicio Rápido](#inicio-rápido)


## Descripción

El microservicio utiliza el modelo `distilbert-base-uncased-finetuned-sst-2-english` disponible en Hugging Face el cual analiza el sentimiento de textos y los clasifica. Cabe mencionar que el lenguaje del modelo es en inglés por lo que el texto provisto debe ser en ese idioma. El modelo clasificará el texto como **positivo** o **negativo** con un nivel de confianza correspondiente.

### Componentes Principales

- **FastAPI**: API REST para recibir requests de clasificación
- **DistilBERT**: Modelo de Hugging Face para clasificación de sentimientos
- **Docker**: Containerización de la aplicación
- **Kubernetes**: Orquestación y despliegue
- **AWS Load Balancer**: Distribución de tráfico y alta disponibilidad

### Estructura del Proyecto

```bash
.
├── src/
│   ├── __init__.py
│   ├── main.py              # aplicación FastAPI 
│   └── model_service.py     # servicio DistilBERT
├── k8s/
│   ├── deployment.yaml      # Configuración de despliegue
│   ├── service.yaml         # Servicio para exposición
│   ├── loadbalancer.yaml    # AWS Load Balancer
│   ├── hpa.yaml             # Escalado automático horizontal
│   └── configmap.yaml       # Variables de configuración
├── tests/
│   ├── test_main.py         # test servicio FastAPI
│   └── test_model_service.py # test servicio modelo
├── Dockerfile
├── pyproject.toml           # gestión dependencias Poetry
├── Makefile                 # comandos de desarrollo y despliegue
└── README.md
```

## Inicio Rápido

### Configuración Inicial (Una sola línea)

```bash
# Iniciar servidor de desarrollo
make quick-start

# El servidor estará disponible en:
# - API: http://localhost:8000
```

Este comando:

- Verifica e instala Poetry si es necesario
- Instala todas las dependencias del proyecto
- Inicia el servicio de clasificación de forma local

> **Nota:** Es necesario tener instalado [Poetry](https://python-poetry.org/) en el sistema para la gestión de dependencias y ejecución de comandos. Se puede instalar siguiendo la [documentación oficial](https://python-poetry.org/docs/#installation).

### Comandos Make Esenciales

```bash
make setup          # Configurar entorno de desarrollo
make dev            # Iniciar servidor de desarrollo  
make test           # Ejecutar tests
make clean          # Limpiar archivos temporales

make docker-build   # Construir imagen Docker
make docker-run     # Ejecutar contenedor
make docker-stop    # Detener el contenedor
```

## Construcción y ejecución con Docker

```bash
# Construir la imagen
docker build -t microserv-llm:latest .

# Ejecutar el contenedor
docker run -p 8000:8000 microserv-llm:latest
```

## Documentación API

### GET `/`

Endpoint raíz del servicio

```bash
curl http://localhost:8000/
```

### GET `/health`

Health check del servicio

```bash
curl http://localhost:8000/health
```

### POST `/predict_sentiment`

Predicción de sentimientos

```bash
curl -X POST "http://localhost:8000/predict_sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this product!"
  }'
```

## Configuración de Recursos

Para el microservicio ML se recomienda:

- **CPU**: 500m-1000m por pod
- **Memory**: 1Gi-2Gi por pod
- **Replicas**: 2-10 (con HPA)