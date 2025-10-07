import logging
import os
from datetime import datetime
from typing import Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient

import jwt
import requests

from . import exceptions

logger = logging.getLogger(__name__)


class TokensStorage:
    def get_access_token(self) -> Optional[str]:
        pass

    def get_refresh_token(self) -> Optional[str]:
        pass

    def save_tokens(self, access_token: str, refresh_token: str):
        pass


class MongoTokensStorage(TokensStorage):
    """Хранит токены в MongoDB."""

    def __init__(self, mongo_uri: str, db_name="medai"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["tokens"]

    async def get_access_token(self, client_id: str) -> Optional[str]:
        token_data = await self.collection.find_one({"client_id": client_id})
        return token_data["access_token"] if token_data else None

    async def get_refresh_token(self, client_id: str) -> Optional[str]:
        token_data = await self.collection.find_one({"client_id": client_id})
        return token_data["refresh_token"] if token_data else None

    async def get_subdomain(self, client_id: str) -> Optional[str]:
        """Получить subdomain из MongoDB."""
        token_data = await self.collection.find_one({"client_id": client_id})
        return token_data.get("subdomain") if token_data else None

    async def save_tokens(self, client_id: str, access_token: str, refresh_token: str, subdomain: str = None):
        """Сохраняем токены и subdomain в MongoDB (без дубликатов)."""
        print(f"🟢 [MongoTokensStorage] Сохраняем токены для {client_id} в MongoDB...")

        update_data = {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "updated_at": datetime.utcnow()
        }
        
        # Сохраняем subdomain только если он предоставлен
        if subdomain:
            update_data["subdomain"] = subdomain

        try:
            result = await self.collection.update_one(
                {"client_id": client_id},
                {"$set": update_data},
                upsert=True  # Создает запись, если её нет
            )

            if result.matched_count > 0:
                print(f"✅ [MongoTokensStorage] Токены обновлены.")
            else:
                print(f"✅ [MongoTokensStorage] Новая запись создана.")

        except Exception as e:
            print(f"🔴 [MongoTokensStorage] Ошибка при сохранении в MongoDB: {e}")


class TokenManager:
    def __init__(self, mongo_uri):
        self._client_id = None
        self._client_secret = None
        self.subdomain = None
        self._redirect_url = None
        self._storage = MongoTokensStorage(mongo_uri)  # Используем MongoDB

    def __call__(self, client_id: str, client_secret: str, subdomain: str, redirect_url: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_url = redirect_url
        self.subdomain = subdomain

    async def init(self, code, skip_error=False):
        """Инициализация токенов и сохранение в MongoDB."""
        print(f"🟢 [TokenManager] Запрашиваем токены для {self._client_id}...")

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_url,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        print(f"🟢 [TokenManager] Данные запроса: {data}")

        response = requests.post(f"https://{self.subdomain}.amocrm.ru/oauth2/access_token", json=data)

        print(f"🟢 [TokenManager] HTTP статус AmoCRM: {response.status_code}")
        print(f"🟢 [TokenManager] Ответ AmoCRM: {response.text}")
        
        if response.status_code == 200:
            tokens_data = response.json()
            print(f"🟢 [TokenManager] Токены получены: {tokens_data}")

            access_token = tokens_data.get("access_token")
            refresh_token = tokens_data.get("refresh_token")

            if access_token and refresh_token:
                print(f"🟢 [TokenManager] Вызываем save_tokens() для {self._client_id}...")
                # ВАЖНО: передаем subdomain при сохранении токенов
                await self._storage.save_tokens(
                    self._client_id, 
                    access_token, 
                    refresh_token, 
                    self.subdomain  # <-- Сохраняем subdomain в MongoDB
                )
                print(f"✅ [TokenManager] save_tokens() успешно выполнен.")
            else:
                print(f"🔴 [TokenManager] Ошибка: нет access_token или refresh_token")

        else:
            print(f"🔴 [TokenManager] Ошибка: {response.status_code} {response.text}")
            raise Exception(response.json().get("hint", "Ошибка инициализации"))


    async def _get_new_tokens(self):
        """Обновление токенов через refresh_token."""
        refresh_token = await self._storage.get_refresh_token(self._client_id)
        if not refresh_token:
            raise ValueError("Refresh token отсутствует")
        
        # Если subdomain не указан при инициализации, 
        # пытаемся получить его из MongoDB
        if not self.subdomain:
            self.subdomain = await self._storage.get_subdomain(self._client_id)
            if not self.subdomain:
                raise ValueError(f"Не удалось получить subdomain для {self._client_id} из MongoDB")
        
        body = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": self._redirect_url,
        }
        response = requests.post(f"https://{self.subdomain}.amocrm.ru/oauth2/access_token", json=body)
        if response.status_code == 200:
            data = response.json()
            await self._storage.save_tokens(self._client_id, data["access_token"], data["refresh_token"], self.subdomain)
            return data["access_token"]
        raise EnvironmentError("Не удалось обновить токены: {}".format(response.json()))

    async def get_access_token(self):
        """Получение access_token (обновляет, если истек)."""
        token = await self._storage.get_access_token(self._client_id)
        if not token:
            raise exceptions.NoToken("Инициализируйте токены методом 'init'")
        
        # Если subdomain не указан при инициализации, 
        # пытаемся получить его из MongoDB
        if not self.subdomain:
            self.subdomain = await self._storage.get_subdomain(self._client_id)
        
        if self._is_expired(token):
            token = await self._get_new_tokens()
        return token

    async def get_subdomain(self):
        """Получение subdomain из MongoDB, если не указан при инициализации."""
        if self.subdomain:
            return self.subdomain
            
        # Получаем subdomain из MongoDB
        subdomain = await self._storage.get_subdomain(self._client_id)
        if not subdomain:
            raise ValueError(f"Subdomain для {self._client_id} отсутствует в MongoDB")
            
        return subdomain

    @staticmethod
    def _is_expired(token: str):
        """Проверяем, истек ли токен."""
        token_data = jwt.decode(token, options={"verify_signature": False})
        exp = datetime.utcfromtimestamp(token_data["exp"])
        return datetime.utcnow() >= exp


# default_token_manager = TokenManager()
default_token_manager = TokenManager(mongo_uri="mongodb://localhost:27017")