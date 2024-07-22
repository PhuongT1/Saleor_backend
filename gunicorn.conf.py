# gunicorn.conf.py
import os

workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'
host = '0.0.0.0'
port = os.environ.get("PORT",8000)
loglevel = 'info'
timeout=1000
