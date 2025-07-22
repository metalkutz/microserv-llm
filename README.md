# Microservicio LLM para Análisis de Sentimientos

Microservicio de inferencia para clasificación de sentimientos usando el modelo DistilBERT, desarrollado con FastAPI y preparado para despliegue en Kubernetes (AWS EKS).

## Contenido

- [Descripción](#descripción)

## Descripción

El microservicio utiliza el modelo `distilbert-base-uncased-finetuned-sst-2-english` disponible en Hugging Face el cual analiza el sentimiento de textos y los clasifica. Cabe mencionar que el lenguaje del modelo es en inglés por lo que el texto provisto debe ser en ese idioma. El modelo clasificará el texto como **positivo** o **negativo** con un nivel de confianza correspondiente.
