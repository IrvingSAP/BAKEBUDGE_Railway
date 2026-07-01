"""Configuración Gunicorn — producción Railway.

Concurrencia por defecto: 3 procesos × 2 hilos (gthread) = 6 requests simultáneos.
Ajustar con variables de entorno en Railway sin tocar código.
"""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# gthread: mejor para Django I/O (PostgreSQL, correo) que sync con 1 worker
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gthread")
workers = int(os.environ.get("WEB_CONCURRENCY", "3"))
threads = int(os.environ.get("GUNICORN_THREADS", "2"))

# Tope de seguridad en planes con mucha RAM y CPU compartida limitada
_workers_max = int(os.environ.get("GUNICORN_WORKERS_MAX", "4"))
if worker_class == "sync":
    workers = min(workers, _workers_max)
else:
    workers = min(max(workers, 1), _workers_max)

timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# Reciclar workers tras N requests (evita fugas de memoria lentas)
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "100"))

preload_app = os.environ.get("GUNICORN_PRELOAD", "true").lower() in {"1", "true", "yes"}

accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Railway / contenedores: logs sin buffer
capture_output = True

# Evitar warning si cpu_count() es bajo en el plan compartido
if workers < 1:
    workers = 1
