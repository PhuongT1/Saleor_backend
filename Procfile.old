import gunicorn

config = gunicorn.Config(
    "saleor.asgi:application", port=8000, reload=True, lifespan="off"
)
server = gunicorn.Server(config)
server.run()
web: gunicorn saleor.asgi:application --bind 0.0.0.0:8000
