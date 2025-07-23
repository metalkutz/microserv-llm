# Microservicio LLM para Análisis de Sentimientos

Microservicio de inferencia para clasificación de sentimientos usando el modelo DistilBERT, desarrollado con FastAPI y preparado para despliegue en Kubernetes (AWS EKS).

## Contenido

- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)

## Descripción

El microservicio utiliza el modelo `distilbert-base-uncased-finetuned-sst-2-english` disponible en Hugging Face el cual analiza el sentimiento de textos y los clasifica. Cabe mencionar que el lenguaje del modelo es en inglés por lo que el texto provisto debe ser en ese idioma. El modelo clasificará el texto como **positivo** o **negativo** con un nivel de confianza correspondiente.

### Componentes Principales

- **FastAPI**: API REST para recibir requests de clasificación
- **DistilBERT**: Modelo de Hugging Face para clasificación de sentimientos
- **Docker**: Containerización de la aplicación
- **Kubernetes**: Orquestación y despliegue
- **AWS Load Balancer**: Distribución de tráfico y alta disponibilidad

### Estructura del Proyecto

```
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
├── scripts/
│   ├── deploy.sh            # despliegue en AWS
│   └── dev.sh               # entorno desarrollo 
├── tests/
│   ├── test_main.py         # test servicio FastAPI
│   └── test_model_service.py # test servicio modelo
├── Dockerfile
├── pyproject.toml           # gestion dependencias Poetry
└── README.md
```
