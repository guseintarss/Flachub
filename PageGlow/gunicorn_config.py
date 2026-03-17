"""
Gunicorn configuration for PageGlow project.
"""
import os
import multiprocessing
from decouple import config

# Server settings
bind = config('GUNICORN_BIND', default='0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = config('GUNICORN_WORKERS', default=multiprocessing.cpu_count() * 2 + 1, cast=int)
worker_class = config('GUNICORN_WORKER_CLASS', default='sync')
worker_connections = 1000
timeout = 30
keepalive = 2

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

# SSL
keyfile = None
certfile = None
ssl_version = 3
cert_reqs = 0
ca_certs = None
suppress_ragged_eof = True
do_handshake_on_connect = False
ciphers = None

# Performance
max_requests = config('GUNICORN_MAX_REQUESTS', default=1000, cast=int)
max_requests_jitter = config('GUNICORN_MAX_REQUESTS_JITTER', default=50, cast=int)

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
    pass

def on_exit(server):
    pass

def when_ready(server):
    print('Gunicorn server is ready. Spawning workers')

def pre_fork(server, worker):
    pass

def post_fork(server, worker):
    pass

def post_worker_init(worker):
    pass

def worker_int(worker):
    pass

def worker_abort(worker):
    pass

def pre_exec(server):
    pass

def post_exec(server):
    pass

def pre_reload(server):
    pass

def post_reload(server):
    pass
