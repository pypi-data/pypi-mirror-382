import os
import uuid
import json
import time
import pickle
import threading
import inspect
import traceback
from dataclasses import dataclass, asdict
from typing import Callable

from cloud_socket.auth import User


# 3 MB
MAX_SIZE = 3 * 1024 * 1024
LARGE_DATA_TOKEN = ':large data:'


@dataclass
class CloudSocketLog:
    id: str
    epoch: float
    user_data: str
    status: str 
    name: str  
    module: str 
    file: str 
    server_data: str
    request_data: str
    response_data: str

    def to_dict(self):
        return asdict(self)


def force_json(data):
    try:
        if hasattr(data, '__cloud_socket_log__') and callable(data.__cloud_socket_log__):
            try:
                return data.__cloud_socket_log__()
            except:
                traceback.print_exc()

        try:
            if len(pickle.dumps(data)) > MAX_SIZE:
                return LARGE_DATA_TOKEN
        except: pass

        return json.dumps(data)
    except:
        return f'{data}'


def thread(func):
    # @wraps(func)
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t
    return wrapper


@thread
def log(log_handler: Callable[[CloudSocketLog], None] | None, status, user: User, func, server_data, request_data, response_data):
    if log_handler:
        csl = CloudSocketLog(
            id=f'{uuid.uuid4()}',
            epoch=time.time(),
            user_data=force_json(user.to_dict()),
            status=status,
            name=func.__name__,
            module=func.__module__,
            file=inspect.getfile(func),
            server_data=server_data,
            request_data=request_data,
            response_data=response_data
        )

        log_handler(csl)



















