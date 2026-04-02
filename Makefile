# PageGlow 3.0 - Makefile для управления проектом

.PHONY: help up down restart ps logs logs-app logs-nginx logs-db migrate makemigrations dbshell backup restore createsuperuser collectstatic clearstatic shell bash test test-coverage clean clean-static update health ssl-cert ssl-renew ssl-enable ssl-disable

# ===========================================
# Основные команды
# ===========================================

help: ## Показать эту справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Запуск всех сервисов (первый раз или после down)
	./deploy.sh

dev: ## Запуск в режиме разработки (с adminer)
	docker compose --profile tools up -d
	@echo "✅ Приложение: http://localhost"
	@echo " Adminer: http://localhost:8080"

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

clean: ## Очистка временных файлов и контейнеров
	docker compose down -v
	docker system prune -f
	@echo "✅ Очистка завершена"

clean-static: ## Пересобрать статику
	docker compose exec pageglow python manage.py collectstatic --clear --noinput
	docker compose exec pageglow python manage.py collectstatic --noinput
	docker compose restart nginx

clean-build: ## Очистка Docker образов и пересборка
	docker compose down
	docker rmi pageglow:latest 2>/dev/null || true
	docker compose build --no-cache
	@echo "✅ Пересборка завершена"

# ===========================================
# Обновление
# ===========================================

update: ## Обновить приложение (pull + rebuild + restart)
	./deploy.sh

update-force: ## Полное обновление с пересборкой
	git pull
	docker compose build --no-cache
	docker compose down
	docker compose up -d
	docker compose exec pageglow python manage.py migrate --noinput
	docker compose exec pageglow python manage.py collectstatic --noinput
	@echo "✅ Обновление завершено"

# ===========================================
# Здоровье
# ===========================================

health: ## Проверка здоровья приложения
	@echo "Проверка health endpoint..."
	@curl -sf http://localhost/health/ | python3 -m json.tool 2>/dev/null || echo "❌ Не удалось получить статус"

# ===========================================
# SSL
# ===========================================

ssl-cert: ## Получить SSL сертификат (укажите DOMAIN)
	@if [ -z "$(DOMAIN)" ]; then \
		echo "❌ Укажите DOMAIN=ваш-домен.com"; \
		exit 1; \
	fi
	docker compose up -d nginx
	docker run --rm -it \
		-v $(PWD)/nginx/certbot:/var/www/certbot \
		-v $(PWD)/nginx/ssl:/etc/letsencrypt \
		certbot/certbot certonly --webroot \
		--webroot-path=/var/www/certbot \
		--email admin@$(DOMAIN) \
		--agree-tos --no-eff-email \
		-d $(DOMAIN) -d www.$(DOMAIN)
	@echo "✅ Сертификат получен"
	@echo "Теперь выполните: make ssl-enable"

ssl-enable: ## Включить HTTPS (после получения сертификатов)
	@if [ ! -f nginx/ssl/live/$(DOMAIN)/fullchain.pem ] && [ ! -f nginx/ssl/fullchain.pem ]; then \
		echo "❌ SSL сертификаты не найдены!"; \
		echo "Сначала получите сертификат: make ssl-cert DOMAIN=ваш-домен.com"; \
		exit 1; \
	fi
	cp nginx/ssl-enabled.conf nginx/pageglow.conf
	docker compose restart nginx
	@echo "✅ HTTPS включён"

ssl-disable: ## Отключить HTTPS (вернуться на HTTP)
	cp nginx/pageglow.conf nginx/pageglow-https-backup.conf 2>/dev/null || true
	@grep -q "ssl_certificate" nginx/pageglow.conf && \
		(echo "⚠️  backup сохранён как nginx/pageglow-https-backup.conf"; \
		 echo "Скопируйте базовый nginx конфиг вручную или используйте git checkout") || \
		echo "ℹ️  HTTPS уже отключён"

ssl-renew: ## Обновить SSL сертификаты
	docker compose run --rm certbot renew
	docker compose restart nginx
	@echo "✅ Сертификаты обновлены"
