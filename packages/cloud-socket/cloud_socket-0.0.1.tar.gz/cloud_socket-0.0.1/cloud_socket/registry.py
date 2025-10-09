import inspect
import traceback
import dataclasses
from typing import Any, Callable

from fastapi import WebSocket

from cloud_socket.auth import User, get_encryption_service
from cloud_socket.logger import log, CloudSocketLog


METHOD_HANDLERS = {}
SHOULD_CACHE_USERS = True
cached_users: dict[str, User] = {}


async def call_with_optional_kwargs(func, **kwargs):
    """
    https://chatgpt.com/c/68d47c63-222c-8328-98ce-12f776828ea6
    """
    # sig = inspect.signature(func)
    # accepted = {
    #     k: v
    #     for k, v in kwargs.items()
    #     if k in sig.parameters
    # }
    # return await func(**accepted)

    sig = inspect.signature(func)
    accepted = {}

    for name, param in sig.parameters.items():
        if name in kwargs:
            value = kwargs[name]
            anno = param.annotation

            # If dataclass and value is a dict
            if inspect.isclass(anno) and dataclasses.is_dataclass(anno) and isinstance(value, dict):
                # Get valid field names
                valid_fields = {f.name for f in dataclasses.fields(anno)}
                # Filter out keys not in dataclass (e.g., uid if not present)
                filtered = {k: v for k, v in value.items() if k in valid_fields}
                accepted[name] = anno(**filtered)
            else:
                accepted[name] = value

    if inspect.iscoroutinefunction(func):
        return await func(**accepted)

    return func(**accepted)


def get_request_data(method: str, websocket: WebSocket):
    return {
        "method": method,
        "path": websocket.url.path,
        "remote_addr": websocket.client.host if websocket.client else None,
        "headers": dict(websocket.headers),
    }


def get_user(uid: str) -> User:
    if uid not in cached_users:
        cached_users[uid] = User(uid)

    return cached_users[uid]


def dict_without_keys(obj: dict | Any, without_keys: list[str]):
    if not isinstance(obj, dict):
        return {}
    return {k: v for k, v in obj.items() if k not in without_keys}


async def handle_request(user: User, crypto_key: str, method: str, websocket: WebSocket, afunc, data, log_handler: Callable[[CloudSocketLog], None] | None = None):
    # Convert arrays to bytes
    encrypted = bytes(data['encrypted'])
    iv = bytes(data['iv'])

    # Decrypt the request data
    encryption_service = get_encryption_service(crypto_key)
    decrypted_data = encryption_service.decrypt_data(encrypted, iv)

    decrypted_data = decrypted_data
    user.access_token = decrypted_data['access_token']

    if not await user.is_valid():
        user.validate()

    if not await user.is_valid():
        r = {
            'status': 'error',
            'error': 'Invalid access token'
        }
        encrypted_response, response_iv = encryption_service.encrypt_data(r)

        log(log_handler, 'invalid-auth', user, afunc, get_request_data(method, websocket), decrypted_data, r)
        
        return {
            "encrypted": True,
            "data": {
                "encrypted": list(encrypted_response),
                "iv": list(response_iv)
            }
        }

    try:
        # response_data = await afunc(user=user, data=decrypted_data)  # (user, decrypted_data)
        response_data = await call_with_optional_kwargs(
            func=afunc,
            user=user,
            body=decrypted_data,
            **dict_without_keys(decrypted_data, ['func', 'user', 'body']),
        )
        log(log_handler, 'success', user, afunc, get_request_data(method, websocket), decrypted_data, response_data)
    except Exception as e:
        traceback.print_exc()
        response_data = {'status': 'error', 'error': str(e)}
        log(log_handler, 'error', user, afunc, get_request_data(method, websocket), decrypted_data, response_data)

    # Encrypt the response
    encrypted_response, response_iv = encryption_service.encrypt_data(response_data)

    # Prepare encrypted response
    return {
        "encrypted": True,
        "data": {
            "encrypted": list(encrypted_response),
            "iv": list(response_iv)
        }
    }


def register(method: str):
    def wrapper(func):
        METHOD_HANDLERS[method] = func
        return func

    return wrapper



