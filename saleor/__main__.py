import uvicorn
import os

config = uvicorn.Config(
    "saleor.asgi:application", port=os.environ.get("PORT",8000), reload=True, lifespan="off"
)
server = uvicorn.Server(config)
server.run()