import inspect
import asyncio
import logging
import traceback
from typing import Callable, Any, Awaitable

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from cloud_socket.auth import User
from cloud_socket.registry import METHOD_HANDLERS, handle_request
from cloud_socket.logger import CloudSocketLog
import cloud_socket.registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
VERSION = '0.0.1'


class Request(BaseModel):
    uid: str
    request_id: int
    method: str
    body: dict


async def ensure_async(func, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return asyncio.to_thread(func, *args, **kwargs)


def asign_websocket(
    app: FastAPI,
    get_crytpo_key: Callable[[User], str | Awaitable[str]],
    validate_access_token: Callable[[User], bool | Awaitable[bool]],
    log_handler: Callable[[CloudSocketLog], None] | None = None,
    get_user_info: Callable[[User], dict | Awaitable[dict]] | None = None,
):
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        logger.info("WebSocket connection accepted.")
        user: User = User(None, None, validate_access_token, get_user_info)

        try:
            while True:
                # Wait for a message
                data = await websocket.receive_json()

                # Parse and validate the request
                try:
                    req = Request(**data)
                    logger.info(f"Received request_id={req.request_id}, method={req.method}")

                    if req.uid:
                        user.uid = req.uid
                    
                    handler = METHOD_HANDLERS.get(req.method)

                    if handler:
                        # response_body = await handler(req.body)
                        crypto_key = await ensure_async(get_crytpo_key, user)
                        response_body = await handle_request(user, crypto_key, req.method, websocket, handler, req.body, log_handler)
                        response = {
                            "request_id": req.request_id,
                            "body": response_body
                        }
                    else:
                        raise ValueError(f"Unknown method: {req.method}")

                except Exception as e:
                    # Handle parsing or method errors
                    logger.error(f"Error processing request: {e}")
                    request_id = data.get("request_id", -1)
                    response = {
                        "request_id": request_id,
                        "error": str(e)
                    }

                # Send the response
                await websocket.send_json(response)

        except WebSocketDisconnect:
            logger.info("WebSocket connection closed.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")


async def aserve(
    get_crytpo_key: Callable[[User], str | Awaitable[str]],
    validate_access_token: Callable[[User], bool | Awaitable[bool]],
    host='localhost', 
    port=8003,
    log_level='info',
    app: FastAPI | None = None, 
    allow_origins: list[str] | None = None,
    use_cors: bool = True,
    log_handler: Callable[[CloudSocketLog], None] | None = None,
    get_user_info: Callable[[User], dict | Awaitable[dict]] | None = None,
) -> None:
    if not app:
        app = FastAPI()
        
        if use_cors:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=(allow_origins or ['*']),
                allow_credentials=True,
                allow_methods=['*'],
                allow_headers=['*'],
            )
    
    asign_websocket(app, get_crytpo_key, validate_access_token, log_handler, get_user_info)

    config = uvicorn.Config(app, host=host, port=port, log_level=log_level)
    server = uvicorn.Server(config)
    logger.info(f"Starting server on {host}:{port} | Version: {VERSION}")
    await server.serve()


def serve(
    get_crytpo_key: Callable[[User], str | Awaitable[str]],
    validate_access_token: Callable[[User], bool | Awaitable[bool]],
    host='localhost',
    port=8003,
    log_level='info',
    app: FastAPI | None = None,
    allow_origins: list[str] | None = None,
    use_cors: bool = True,
    log_handler: Callable[[CloudSocketLog], None] | None = None,
    get_user_info: Callable[[User], dict | Awaitable[dict]] | None = None,
) -> None:
    asyncio.run(aserve(get_crytpo_key, validate_access_token, host, port, log_level, app, allow_origins, use_cors, log_handler, get_user_info))


if __name__ == "__main__":
    serve(lambda u: 'secret', lambda u: True)



