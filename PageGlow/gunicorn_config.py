"""
Gunicorn configuration for PageGlow project.
Optimized for production with Docker.
"""
import os
import multiprocessing

# ===========================================
# Server settings
# ===========================================
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = int(os.getenv('GUNICORN_BACKLOG', '2048'))

# ===========================================
# Worker processes
# ===========================================
# Formula: (CPU * 2) + 1 for sync workers
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

# Worker class: use gevent for I/O-bound applications
worker_class = os.getenv('GUNICORN_WORKER_CLASS', 'gevent')
worker_connections = int(os.getenv('GUNICORN_WORKER_CONNECTIONS', '1000'))

# Graceful timeout for worker restarts
graceful_timeout = int(os.getenv('GUNICORN_GRACEFUL_TIMEOUT', '30'))

# ===========================================
# Timeouts
# ===========================================
timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))
keepalive = int(os.getenv('GUNICORN_KEEPALIVE', '5'))

# ===========================================
# Logging
# ===========================================
accesslog = os.getenv('GUNICORN_ACCESSLOG', '-')  # stdout
errorlog = os.getenv('GUNICORN_ERRORLOG', '-')     # stderr
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')

# Custom access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ===========================================
# Process naming
# ===========================================
proc_name = 'pageglow'

# ===========================================
# Server mechanics
# ===========================================
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# ===========================================
# SSL (handled by nginx)
# ===========================================
keyfile = None
certfile = None

# ===========================================
# Performance & Memory
# ===========================================
# Restart worker after N requests (prevent memory leaks)
max_requests = int(os.getenv('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('GUNICORN_MAX_REQUESTS_JITTER', '50'))

# ===========================================
# Application
# ===========================================
preload_app = os.getenv('GUNICORN_PRELOAD_APP', 'False') == 'True'
reload = os.getenv('GUNICORN_RELOAD', 'False') == 'True'
chdir = '/app'

# Environment
env = {
    'DJANGO_SETTINGS_MODULE': 'PageGlow.settings'
}

# ===========================================
# Server hooks
# ===========================================

def on_starting(server):
    """Called just before the master process is initialized."""
    print('🚀 Starting PageGlow Gunicorn server...')


def on_exit(server):
    """Called just before exiting Gunicorn."""
    print('👋 Shutting down PageGlow Gunicorn server...')


def when_ready(server):
    """Called just after the server is started."""
    print('✅ Gunicorn server is ready. Spawning workers...')


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    # Setup database connections for worker
    try:
        from django.db import connection
        connection.ensure_connection()
        worker.log.info('Worker spawned and DB connection established')
    except Exception as e:
        worker.log.error(f'Error setting up DB connection: {e}')


def worker_int(worker):
    """Called just after a worker received SIGINT/SIGQUIT."""
    worker.log.info('Worker received interrupt signal')
