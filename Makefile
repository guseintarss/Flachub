# PageGlow Makefile для тестирования и разработки

.PHONY: help test test-cov test-fast test-watch lint format clean install-dev db-migrate db-seed

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Показать эту справку
	@echo "$${BLUE}PageGlow - доступные команды:$${NC}"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$${BLUE}%-20s$${NC} %s\n", $$1, $$2}'

# ===== ТЕСТЫ =====

test: ## Запустить все тесты
	@echo "$${YELLOW}Запуск всех тестов...$${NC}"
	pytest

test-cov: ## Запустить тесты с покрытием
	@echo "$${YELLOW}Запуск тестов с покрытием...$${NC}"
	pytest --cov=PageGlow --cov-report=html --cov-report=term-missing

test-cov-xml: ## Запустить тесты с XML покрытием (для CI)
	pytest --cov=PageGlow --cov-report=xml --cov-report=term-missing

test-fast: ## Запустить только быстрые тесты (без медленных)
	pytest -m "not slow"

test-watch: ## Запустить тесты в режиме наблюдения
	pytest-watch -- --cov=PageGlow

test-unit: ## Запустить только unit тесты
	pytest -m unit

test-integration: ## Запустить integration тесты
	pytest -m integration

test-models: ## Запустить тесты моделей
	pytest tests/test_models.py -v

test-views: ## Запустить тесты представлений
	pytest tests/test_views.py -v

test-api: ## Запустить тесты API
	pytest tests/test_api.py -v

test-file: ## Запустить тесты из конкретного файла (usage: make test-file FILE=tests/test_models.py)
	pytest $(FILE) -v

test-failed: ## Запустить только упавшие тесты
	pytest --lf

test-new: ## Запустить только новые тесты
	pytest --nf

# ===== ЛИНИНГ И ФОРМАТИРОВАНИЕ =====

lint: ## Запустить линтеры
	@echo "$${YELLOW}Проверка кода...$${NC}"
	python -m flake8 PageGlow/ --exclude=migrations,__pycache__,static
	python -m black PageGlow/ --check --exclude=migrations
	python -m isort PageGlow/ --check-only --skip=migrations

lint-fix: ## Исправить ошибки линтера
	@echo "$${YELLOW}Исправление кода...$${NC}"
	python -m black PageGlow/ --exclude=migrations
	python -m isort PageGlow/ --skip=migrations

format: lint-fix ## Псевдоним для lint-fix

# ===== УСТАНОВКА ЗАВИСИМОСТЕЙ =====

install: ## Установить зависимости
	pip install -r PageGlow/requirements.txt

install-dev: ## Установить зависимости для разработки
	pip install -r PageGlow/requirements.txt
	pip install flake8 black isort mypy pytest-watch

install-prod: ## Установить production зависимости
	pip install -r PageGlow/requirements.txt

# ===== БАЗА ДАННЫХ =====

db-migrate: ## Применить миграции
	python PageGlow/manage.py migrate

db-makemigrations: ## Создать новые миграции
	python PageGlow/manage.py makemigrations

db-seed: ## Заполнить тестовыми данными
	python PageGlow/manage.py shell < scripts/seed_data.py

db-reset: ## Сбросить базу данных (ОПАСНО!)
	@echo "$${YELLOW}Вы уверены? Это удалит все данные!$${NC}"
	@read -p "Введите 'yes' для подтверждения: " confirm && \
	if [ "$$confirm" = "yes" ]; then \
		python PageGlow/manage.py flush --noinput; \
		echo "$${GREEN}База данных сброшена$${NC}"; \
	else \
		echo "$${YELLOW}Отменено$${NC}"; \
	fi

# ===== DJANGO КОМАНДЫ =====

runserver: ## Запустить сервер разработки (обычный Django)
	python PageGlow/manage.py runserver

runserver-ws: ## Запустить ASGI сервер с поддержкой WebSocket (Daphne)
	@echo "$${BLUE}Запуск ASGI сервера с поддержкой WebSocket...$${NC}"
	daphne -b 127.0.0.1 -p 8000 PageGlow.asgi:application

collectstatic: ## Собрать статику
	python PageGlow/manage.py collectstatic --noinput

createsuperuser: ## Создать суперпользователя
	python PageGlow/manage.py createsuperuser

shell: ## Запустить Django shell
	python PageGlow/manage.py shell

# ===== CLEAN =====

clean: ## Очистить временные файлы
	@echo "$${YELLOW}Очистка...$${NC}"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	@echo "$${GREEN}Очистка завершена$${NC}"

clean-all: clean ## Очистить всё (включая базу)
	rm -rf PageGlow/media/*
	rm -rf PageGlow/staticfiles/*

# ===== DOCKER =====

docker-build: ## Собрать Docker образ
	docker-compose build

docker-up: ## Запустить Docker контейнеры
	docker-compose up -d

docker-down: ## Остановить Docker контейнеры
	docker-compose down

docker-logs: ## Показать логи контейнеров
	docker-compose logs -f

docker-shell: ## Войти в контейнер
	docker-compose exec web bash

# ===== DEPLOYMENT =====

check: lint test ## Проверить код перед коммитом

deploy: check ## Задеплоить (заглушка)
	@echo "$${YELLOW}Настройте свой pipeline деплоя$${NC}"
