import asyncio
from dataclasses import dataclass

from cloud_socket.auth import User
from cloud_socket.app import serve, aserve
from cloud_socket.registry import register
from cloud_socket.logger import CloudSocketLog


@dataclass
class Echo:
    message: str


@register('/echo')
async def echo(user: User, body: Echo):
    """
    client side:
    import { api } from './cloudSocket'

    const r = await api({
        method: '/echo', 
        body: {message: 'echo'}
    });
    """
    return {'status': 'ok', 'message': body.message}


@dataclass
class Echo2:
    message: str


@register('echo2')
async def echo2(info: Echo2):
    """
    client side:
    import { api } from './cloudSocket'

    const r = await api({
        method: 'echo2', 
        body: {
            info: {message: 'echo'}
        }
    });
    """
    return {'status': 'ok', 'message': info.message}


@register('hi 😘')
async def hello(user: User, body: dict):
    return {'body': body, 'user': user.to_dict()}


async def validate_access_token(user: User):
    return bool(user.access_token)


async def get_crytpo_key(user: User):
    return user.uid + '123'


def log_handler(log: CloudSocketLog):
    print(log)


async def get_user_info(user: User):
    all_user_info = {}
    return all_user_info.get(user.uid, {})


async def aserve_cloud_socket():
    """
    client setup:
    import { setup, api } from './cloudSocket'

    const uid = 'user456';
    setup({
        url: 'ws://localhost:8003/ws',
        uid, 
        access_token: 'token', 
        crypto_key: uid + '123',
    });
    """
    await aserve(
        get_crytpo_key, 
        validate_access_token,
        host='localhost',
        port=8003,

        # optional
        log_handler=log_handler,
        get_user_info=get_user_info,
    )

    # import uvicorn
    # from fastapi import FastAPI
    # from fastapi.middleware.cors import CORSMiddleware
    # from cloud_socket.app import asign_websocket

    # app = FastAPI()
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=['https://example.com'],
    #     allow_credentials=True,
    #     allow_methods=['*'],
    #     allow_headers=['*'],
    # )
    
    # asign_websocket(app, get_crytpo_key, validate_access_token, log_handler, get_user_info)

    # @app.get('/')
    # async def root():
    #     return {'message': 'Hello World'}

    # config = uvicorn.Config(app, host='localhost', port=8003, log_level='info')
    # server = uvicorn.Server(config)
    # await server.serve()


if __name__ == '__main__':
    asyncio.run(aserve_cloud_socket())




