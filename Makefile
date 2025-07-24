# Makefile para Microservicio LLM - Análisis de Sentimientos
# Autor: Ben Kutz
# Descripción: Scripts de desarrollo y despliegue simplificados

# Variables
DOCKER_IMAGE_NAME = microserv-llm
DOCKER_TAG ?= latest
DOCKER_REGISTRY ?= your-registry
PORT ?= 8000

# Comandos de desarrollo
setup: check-poetry ## Instalar dependencias del proyecto
	poetry install

dev: ## Iniciar servidor directamente con Poetry
	poetry run uvicorn src.main:app --host 0.0.0.0 --port $(PORT) --reload

# Comandos de testing
test: ## Ejecutar tests con Poetry
	poetry run pytest tests/ -v

# Comandos Docker
docker-build: check-docker ## Construir imagen Docker
	docker build -t $(DOCKER_IMAGE_NAME):$(DOCKER_TAG) .

docker-run: check-docker ## Ejecutar contenedor Docker
	docker run -p $(PORT):8000 --name $(DOCKER_IMAGE_NAME)-container $(DOCKER_IMAGE_NAME):$(DOCKER_TAG)

docker-stop: check-docker ## Detener contenedor Docker
	docker stop $(DOCKER_IMAGE_NAME)-container || true
	docker rm $(DOCKER_IMAGE_NAME)-container || true

# Comandos de utilidad
clean: ## Limpiar archivos temporales
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage 2>/dev/null || true
	docker stop $(DOCKER_IMAGE_NAME)-container 2>/dev/null || true
	docker rm $(DOCKER_IMAGE_NAME)-container 2>/dev/null || true

# Verificaciones de dependencias
check-poetry: ## Verificar si Poetry está instalado
	@which poetry > /dev/null || (echo "$(RED)Poetry no encontrado. Instalar desde: https://python-poetry.org$(NC)" && exit 1)

check-docker: ## Verificar si Docker está instalado
	@docker info > /dev/null 2>&1 || (echo "$(RED)Docker no encontrado o no está ejecutándose$(NC)" && exit 1)

# Comandos rápidos
quick-start: setup dev ## Configuración rápida e inicio

.PHONY: clean setup dev test \
	docker-build docker-run docker-stop \
	check-poetry check-docker quick-start