@echo off
REM Скрипт для запуска тестов PageGlow

echo ============================================
echo PageGlow - Запуск тестов
echo ============================================
echo.

if "%1"=="" goto :all
if "%1"=="cov" goto :cov
if "%1"=="html" goto :html
if "%1"=="fast" goto :fast
if "%1"=="unit" goto :unit
if "%1"=="views" goto :views
if "%1"=="api" goto :api
if "%1"=="models" goto :models
if "%1"=="clean" goto :clean

:all
echo Запуск всех тестов...
pytest
goto :end

:cov
echo Запуск тестов с покрытием...
pytest --cov=PageGlow --cov-report=term-missing
goto :end

:html
echo Запуск тестов с HTML отчетом...
pytest --cov=PageGlow --cov-report=html
echo Отчет доступен в htmlcov/index.html
goto :end

:fast
echo Запуск быстрых тестов...
pytest -m "not slow"
goto :end

:unit
echo Запуск unit тестов...
pytest -m unit
goto :end

:views
echo Запуск тестов views...
pytest tests/test_views.py -v
goto :end

:api
echo Запуск тестов API...
pytest tests/test_api.py -v
goto :end

:models
echo Запуск тестов моделей...
pytest tests/test_models.py -v
goto :end

:clean
echo Очистка...
if exist .coverage del .coverage
if exist coverage.xml del coverage.xml
if exist htmlcov rmdir /s /q htmlcov
if exist .pytest_cache rmdir /s /q .pytest_cache
echo Очистка завершена
goto :end

:end
echo.
echo ============================================
echo Тесты завершены
echo ============================================
