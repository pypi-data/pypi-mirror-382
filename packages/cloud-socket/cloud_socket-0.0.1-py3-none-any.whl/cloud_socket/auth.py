import os
import json
import inspect
import asyncio
from typing import Callable, Awaitable

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class EncryptionService:
    def __init__(self, key_string: str):
        self.key = self.derive_key(key_string)
        self.aesgcm = AESGCM(self.key)

    @staticmethod
    def derive_key(key_string: str) -> bytes:
        """Derive a 32-byte key from the input string using SHA-256"""
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(key_string.encode())
        return digest.finalize()

    def encrypt_data(self, data: dict) -> tuple[bytes, bytes]:
        """Encrypt data using AES-GCM"""
        # Convert data to JSON string and encode
        data_bytes = json.dumps(data).encode()

        # Generate 12-byte IV
        iv = os.urandom(12)

        # Encrypt data (includes auth tag automatically)
        encrypted = self.aesgcm.encrypt(iv, data_bytes, None)

        return encrypted, iv

    def decrypt_data(self, encrypted: bytes, iv: bytes) -> dict:
        """Decrypt data using AES-GCM"""
        try:
            # Decrypt data
            decrypted_bytes = self.aesgcm.decrypt(iv, encrypted, None)

            # Parse JSON data
            return json.loads(decrypted_bytes.decode())

        except Exception as e:
            print(f"Decryption error: {str(e)}")
            raise ValueError("Failed to decrypt data")


# # Initialize encryption service
# encryption_service = EncryptionService(crypto_key)

def get_encryption_service(crypto_key: str) -> EncryptionService:
    return EncryptionService(crypto_key)


class User:
    def __init__(self, uid, access_token, validate_access_token: Callable[['User'], bool | Awaitable[bool]], get_user_info: Callable[['User'], dict | Awaitable[dict]] | None = None,):
        self._valid = False
        self._validated = False
        self.info = {}
        self.uid = uid
        self.access_token = access_token
        self.validate_access_token = validate_access_token
        self._fetched_user_info = False
        self.get_user_info = get_user_info
    
    async def get_info(self):
        if self._fetched_user_info:
            return self.info
        if self.get_user_info:
            self.info = await self.ensure_async(self.get_user_info, self)
        else:
            self.info = {}
        self._fetched_user_info = True
        return self.info

    def __str__(self):
        return f'User(' + ', '.join([f'{k}={repr(v)}' for k, v in self.to_dict().items()]) + ')'

    def __cloud_socket_log__(self):
        name = ''
        if isinstance(self._info, dict):
            name = self._info.get('full_name')
        return f'''{name} | (User('{self.session_id}'), {self.to_dict()})'''

    def to_dict(self):
        return {
            'uid': self.uid,
            'access_token': self.access_token,
            'info': self.info,
            'valid': self._valid,
            'validated': self._validated,
        }

    def from_dict(self, data):
        self.uid = data.get('uid')
        self.access_token = data.get('access_token')
        self.info = data.get('info')
        self._valid = data.get('valid')
        self._validated = data.get('validated')

    async def is_valid(self):
        if self._validated and self._valid:
            return self._valid
        await self.validate()
        return self._valid

    async def validate(self) -> bool:
        self._valid = await self.ensure_async(self.validate_access_token, self)
        self._validated = True
    
    @staticmethod
    async def ensure_async(func, *args, **kwargs):
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return asyncio.to_thread(func, *args, **kwargs)


