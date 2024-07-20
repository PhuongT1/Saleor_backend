import uvicorn

config = uvicorn.Config(
    "saleor.asgi:application", port=10000, reload=True, lifespan="off"
)
server = uvicorn.Server(config)
server.run()
