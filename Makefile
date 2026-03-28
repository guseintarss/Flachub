# PageGlow 3.0 - Makefile для управления проектом

.PHONY: help dev prod backup restore logs shell restart clean

# ===========================================
# Основные команды
# ===========================================

help: ## Показать эту справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===========================================
# Разработка
# ===========================================

dev: ## Запуск в режиме разработки
	docker compose --profile tools up -d
	@echo "✅ Приложение запущено: http://localhost:8000"
	@echo "📊 Adminer: http://localhost:8080"

prod: ## Запуск в production режиме
	docker compose up -d
	@echo "✅ Production приложение запущено"

down: ## Остановка всех сервисов
	docker compose down

restart: ## Перезапуск всех сервисов
	docker compose restart

ps: ## Показать статус сервисов
	docker compose ps

# ===========================================
# Логи
# ===========================================

logs: ## Показать все логи
	docker compose logs -f

logs-app: ## Логи приложения
	docker compose logs -f pageglow

logs-nginx: ## Логи nginx
	docker compose logs -f nginx

logs-db: ## Логи базы данных
	docker compose logs -f postgres

# ===========================================
# База данных
# ===========================================

migrate: ## Применить миграции
	docker compose exec pageglow python manage.py migrate

makemigrations: ## Создать новые миграции
	docker compose exec pageglow python manage.py makemigrations

dbshell: ## Подключение к PostgreSQL
	docker compose exec postgres psql -U postgres -d pageglow_db

backup: ## Резервное копирование БД и медиа
	./backup.sh

restore: ## Восстановление из бэкапа (укажите BACKUP_FILE)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Укажите BACKUP_FILE=путь_к_файлу.sql.gz"; \
		exit 1; \
	fi
	gunzip < $(BACKUP_FILE) | docker compose exec -T postgres psql -U postgres pageglow_db
	@echo "✅ Восстановление завершено"

# ===========================================
# Суперпользователь
# ===========================================

createsuperuser: ## Создать суперпользователя
	docker compose exec pageglow python manage.py createsuperuser

# ===========================================
# Статика и медиа
# ===========================================

collectstatic: ## Собрать статику
	docker compose exec pageglow python manage.py collectstatic --noinput

clearstatic: ## Очистить статику
	docker compose exec pageglow python manage.py collectstatic --clear --noinput

# ===========================================
# Консоль
# ===========================================

shell: ## Django shell
	docker compose exec pageglow python manage.py shell

bash: ## Bash в контейнере приложения
	docker compose exec pageglow bash

# ===========================================
# Тесты
# ===========================================

test: ## Запустить тесты
	docker compose exec pageglow python manage.py test

test-coverage: ## Запустить тесты с покрытием
	docker compose exec pageglow coverage run manage.py test
	docker compose exec pageglow coverage report

# ===========================================
# Очистка
# ===========================================

clean: ## Очистка временных файлов
	docker compose down -v
	docker system prune -f
	@echo "✅ Очистка завершена"

clean-static: ## Пересобрать статику
	docker compose exec pageglow python manage.py collectstatic --clear --noinput
	docker compose exec pageglow python manage.py collectstatic --noinput
	docker compose restart nginx

# ===========================================
# Обновление
# ===========================================

update: ## Обновить приложение
	git pull
	docker compose build --no-cache
	docker compose down
	docker compose up -d
	@echo "✅ Обновление завершено"

# ===========================================
# Здоровье
# ===========================================

health: ## Проверка здоровья приложения
	@echo "Проверка health endpoint..."
	@curl -s http://localhost:8000/health/ | python3 -m json.tool || echo "❌ Не удалось получить статус"

# ===========================================
# SSL
# ===========================================

ssl-cert: ## Получить SSL сертификат (укажите DOMAIN)
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ Укажите DOMAIN=ваш-домен.com"; \
		exit 1; \
	fi
	docker run --rm -it \
		-v $(PWD)/nginx/certbot:/etc/letsencrypt \
		-v $(PWD)/nginx/ssl:/var/www/certbot \
		certbot/certbot certonly --webroot \
		--webroot-path=/var/www/certbot \
		--email admin@$(DOMAIN) \
		--agree-tos --no-eff-email \
		-d $(DOMAIN) -d www.$(DOMAIN)
	@echo "✅ Сертификат получен"

ssl-renew: ## Обновить SSL сертификаты
	docker run --rm -it \
		-v $(PWD)/nginx/certbot:/etc/letsencrypt \
		-v $(PWD)/nginx/ssl:/var/www/certbot \
		certbot/certbot renew
	docker compose restart nginx
	@echo "✅ Сертификаты обновлены"
