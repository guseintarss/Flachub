"""
Gunicorn configuration for PageGlow project.
Optimized for production performance.
"""
import os
import multiprocessing
from decouple import config

# Server settings
bind = config('GUNICORN_BIND', default='0.0.0.0:8000')
backlog = 2048

# Worker processes
# Formula: (CPU * 2) + 1 for worker-class=sync
# Formula: CPU * 2 + 1 for worker-class=gevent
workers = config('GUNICORN_WORKERS', default=multiprocessing.cpu_count() * 2 + 1, cast=int)

# Worker class: use gevent for I/O-bound applications (like Django with DB/Redis)
worker_class = config('GUNICORN_WORKER_CLASS', default='gevent')
worker_connections = config('GUNICORN_WORKER_CONNECTIONS', default=1000, cast=int)

# Timeouts
timeout = config('GUNICORN_TIMEOUT', default=30, cast=int)
keepalive = config('GUNICORN_KEEPALIVE', default=2, cast=int)
graceful_timeout = config('GUNICORN_GRACEFUL_TIMEOUT', default=30, cast=int)

# Logging
accesslog = config('GUNICORN_ACCESSLOG', default='-')  # stdout
errorlog = config('GUNICORN_ERRORLOG', default='-')     # stderr
loglevel = config('GUNICORN_LOGLEVEL', default='info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'pageglow'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (configure in nginx)
keyfile = None
certfile = None

# Performance
max_requests = config('GUNICORN_MAX_REQUESTS', default=1000, cast=int)
max_requests_jitter = config('GUNICORN_MAX_REQUESTS_JITTER', default=50, cast=int)

# Memory limits (restart worker after this many MB)
max_memory = config('GUNICORN_MAX_MEMORY', default=512, cast=int)

# Application
preload_app = config('GUNICORN_PRELOAD_APP', default='False') == 'True'
reload = config('GUNICORN_RELOAD', default='False') == 'True'
reload_extra_files = []
chdir = None
env = {
    'DJANGO_SETTINGS_MODULE': 'PageGlow.settings'
}

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_exit(server):
    """Called just before exiting Gunicorn."""
    pass

def when_ready(server):
    """Called just after the server is started."""
    print('🚀 Gunicorn server is ready. Spawning workers...')

def pre_fork(server, worker):
    """Called just prior to forking a worker."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    # Setup database connections for worker
    from django.db import connection
    connection.ensure_connection()

def post_worker_init(worker):
    """Called just after a worker has initialized the process."""
    pass

def worker_int(worker):
    """Called just after a worker received SIGINT/SIGQUIT."""
    pass

def worker_abort(worker):
    """Called just after a worker received SIGABRT."""
    pass

def pre_exec(server):
    """Called just prior to forking a new process."""
    pass

def post_exec(server):
    """Called just after a new process is spawned."""
    pass

def pre_reload(server):
    """Called just before Gunicorn reloads."""
    pass

def post_reload(server):
    """Called just after Gunicorn reloads."""
    pass
