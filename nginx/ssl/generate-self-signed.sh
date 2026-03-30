#!/bin/bash
# Скрипт для генерации самоподписанных SSL сертификатов (для тестирования)

SSL_DIR="./nginx/ssl"

echo "🔐 Генерация самоподписанных SSL сертификатов..."

# Создаем директорию
mkdir -p "$SSL_DIR"

# Генерируем самоподписанный сертификат
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/privkey.pem" \
    -out "$SSL_DIR/fullchain.pem" \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=PageGlow/OU=IT/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:pageglow.ru,DNS:www.pageglow.ru,IP:127.0.0.1"

# Копируем сертификат как chain.pem (для OCSP stapling в тестовой среде)
cp "$SSL_DIR/fullchain.pem" "$SSL_DIR/chain.pem"

# Устанавливаем правильные права
chmod 600 "$SSL_DIR/privkey.pem"
chmod 644 "$SSL_DIR/fullchain.pem"
chmod 644 "$SSL_DIR/chain.pem"

echo "✅ Сертификаты сгенерированы в $SSL_DIR"
echo ""
echo "📁 Файлы:"
echo "   - fullchain.pem (публичный сертификат)"
echo "   - privkey.pem (приватный ключ)"
echo "   - chain.pem (цепочка сертификатов)"
echo ""
echo "⚠️  Внимание: Это самоподписанные сертификаты для тестирования!"
echo "   Для production используйте Let's Encrypt или коммерческие сертификаты."
