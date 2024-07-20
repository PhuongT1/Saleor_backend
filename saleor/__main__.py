import gunicorn

config = gunicorn.Config(
    "saleor.asgi:application", port=8000, reload=True, lifespan="off"
)
server = gunicorn.Server(config)
server.run()