from datetime import datetime

import aiohttp
from pydantic import BaseModel, HttpUrl, TypeAdapter

from ..settings import BACKEND_URL


class APIModel(BaseModel):
    @classmethod
    def _get_client(cls):
        return aiohttp.ClientSession(BACKEND_URL)

    @classmethod
    async def _api_get(cls, url: HttpUrl, **params):
        async with (
            cls._get_client() as client,
            client.get(url, params=params) as response,
        ):
            if not response.ok:
                return None
            return cls.model_validate_json(await response.read())

    @classmethod
    async def _api_get_list(cls, url: HttpUrl, **params):
        async with (
            cls._get_client() as client,
            client.get(url, params=params) as response,
        ):
            if not response.ok:
                return None
            return TypeAdapter(list[cls]).validate_json(await response.read())

    @classmethod
    async def _api_patch(cls, url: HttpUrl, params: dict | None = None, **body):
        if params is None:
            params = {}
        async with (
            cls._get_client() as client,
            client.patch(url, params=params, json=body) as response,
        ):
            if not response.ok:
                return None
            return cls.model_validate_json(await response.read())

    @classmethod
    async def _api_create(
        cls,
        url: HttpUrl,
        params: dict | None = None,
        **body,
    ):
        if params is None:
            params = {}
        async with (
            cls._get_client() as client,
            client.post(url=url, params=params, json=body) as response,
        ):
            return cls.model_validate_json(await response.read())


class TelegramUser(BaseModel):
    telegram_id: int


class SupportManager(BaseModel):
    pass


class Ticket(APIModel):
    id: int
    user: TelegramUser
    support_manager: SupportManager | None
    created_at: datetime
    title: str
    resolved: bool
    viewed: bool

    @classmethod
    async def api_get(cls, id: int):
        return await cls._api_get(f'tickets/{id}/')

    @classmethod
    async def api_get_list(cls, user_id: int, resolved: bool):
        return await cls._api_get_list(
            'tickets/',
            user_id=user_id,
            resolved=str(resolved).lower(),
        )

    @classmethod
    async def api_update(cls, id: int, **kwargs):
        return await cls._api_patch(
            f'tickets/{id}/',
            body=kwargs,
        )

    @classmethod
    async def api_create(cls, user_id: int, title: str):
        return await cls._api_create(
            'tickets/',
            user_id=user_id,
            title=title,
        )


class Message(APIModel):
    id: int
    created_at: datetime
    ticket: int
    sender: str
    text: str

    @classmethod
    async def api_get_list(cls, ticket_id: int):
        return await cls._api_get_list(f'tickets/{ticket_id}/messages/')

    @classmethod
    async def api_create(cls, ticket_id: int, text: str):
        return await cls._api_create(
            f'tickets/{ticket_id}/messages/',
            text=text,
        )
