#!/bin/bash
# Script for quick deployment PageGlow 3.0 on VPS (Ubuntu/Debian)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 PageGlow 3.0 Deployment Script${NC}"
echo "======================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo ./deploy.sh)${NC}"
    exit 1
fi

# Configuration
DEPLOY_USER="${SUDO_USER:-$(whoami)}"
DEPLOY_DIR="/home/$DEPLOY_USER/PageGlow3.0"
APP_DIR="$DEPLOY_DIR/PageGlow"
VENV_DIR="$APP_DIR/venv"

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Deploy User: $DEPLOY_USER"
echo "  Deploy Dir: $DEPLOY_DIR"
echo "  App Dir: $APP_DIR"
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Install dependencies
echo -e "${YELLOW}[1/8] Installing dependencies...${NC}"
apt-get update
apt-get install -y python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib nginx git curl wget \
    build-essential libpq-dev libssl-dev zlib1g-dev

# Step 2: Setup PostgreSQL
echo -e "${YELLOW}[2/8] Setting up PostgreSQL...${NC}"
read -p "Database name (pageglow_db): " DB_NAME
DB_NAME=${DB_NAME:-pageglow_db}

read -p "Database user (pageglow_user): " DB_USER
DB_USER=${DB_USER:-pageglow_user}

read -sp "Database password: " DB_PASS
echo

sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Step 3: Clone repository
echo -e "${YELLOW}[3/8] Cloning repository...${NC}"
cd /home/$DEPLOY_USER
if [ -d "PageGlow3.0" ]; then
    echo -e "${YELLOW}Directory already exists. Pulling latest changes...${NC}"
    cd PageGlow3.0
    git pull
else
    git clone https://github.com/guseintarss/PageGlow3.0.git
fi

# Step 4: Setup virtual environment
echo -e "${YELLOW}[4/8] Setting up Python virtual environment...${NC}"
cd $APP_DIR
python3 -m venv venv
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Step 5: Create .env file
echo -e "${YELLOW}[5/8] Creating .env file...${NC}"
cp ../.env.example .env

read -p "Your domain (example.com): " DOMAIN
DOMAIN=${DOMAIN:-example.com}

read -sp "Secret key (press enter to generate): " SECRET_KEY
echo
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -base64 64)
fi

read -sp "Email for notifications: " EMAIL_USER
echo

cat > .env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=$DB_NAME
DATABASE_USERNAME=$DB_USER
DATABASE_PASSWORD=$DB_PASS

# Email
EMAIL_HOST_USER=$EMAIL_USER
EMAIL_HOST_PASSWORD=your-app-password

# Cache
REDIS_URL=redis://localhost:6379/0
EOF

chmod 600 .env
echo -e "${GREEN}✓ .env created${NC}"

# Step 6: Django setup
echo -e "${YELLOW}[6/8] Setting up Django...${NC}"
source $VENV_DIR/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput

echo -e "${GREEN}Create superuser?${NC}"
read -p "Create superuser now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Step 7: Create systemd service
echo -e "${YELLOW}[7/8] Creating systemd service...${NC}"
cat > /etc/systemd/system/pageglow.service << EOF
[Unit]
Description=PageGlow Web Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers 4 \\
    --worker-class sync \\
    --bind unix:/run/gunicorn.sock \\
    --access-logfile /var/log/pageglow/access.log \\
    --error-logfile /var/log/pageglow/error.log \\
    --capture-output \\
    PageGlow.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

mkdir -p /var/log/pageglow
chown www-data:www-data /var/log/pageglow

systemctl daemon-reload
systemctl start pageglow
systemctl enable pageglow

echo -e "${GREEN}✓ Systemd service created${NC}"

# Step 8: Configure Nginx
echo -e "${YELLOW}[8/8] Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/pageglow << EOF
upstream pageglow_app {
    server unix:/run/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    client_max_body_size 75M;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $APP_DIR/media/;
        expires 7d;
    }

    # Django app
    location / {
        proxy_pass http://pageglow_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/pageglow /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl restart nginx

echo -e "${GREEN}✓ Nginx configured${NC}"

# Setup SSL (optional)
echo
echo -e "${YELLOW}Setup SSL with Let's Encrypt?${NC}"
read -p "Setup SSL now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    apt-get install -y certbot python3-certbot-nginx
    certbot certonly --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL_USER --agree-tos --non-interactive
    
    # Update Nginx config for HTTPS
    cat > /etc/nginx/sites-available/pageglow << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    client_max_body_size 75M;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $APP_DIR/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://pageglow_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        proxy_redirect off;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

    systemctl restart nginx
    echo -e "${GREEN}✓ SSL configured${NC}"
fi

# Final checks
echo
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}======================================${NC}"
echo
echo -e "${YELLOW}📊 Service Status:${NC}"
systemctl status pageglow --no-pager | grep -E "Active|Loaded"
echo
echo -e "${YELLOW}🌐 Website:${NC} http://$DOMAIN"
echo -e "${YELLOW}🔧 Admin Panel:${NC} https://$DOMAIN/admin/"
echo -e "${YELLOW}📝 Logs:${NC} tail -f /var/log/pageglow/error.log"
echo
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "  1. Configure email password in .env"
echo "  2. Setup backup script (see DEPLOYMENT_CHECKLIST.md)"
echo "  3. Configure firewall (UFW): sudo ufw allow 'Nginx Full'"
echo "  4. Setup monitoring and alerts"
echo
echo -e "${GREEN}Done! 🎉${NC}"
