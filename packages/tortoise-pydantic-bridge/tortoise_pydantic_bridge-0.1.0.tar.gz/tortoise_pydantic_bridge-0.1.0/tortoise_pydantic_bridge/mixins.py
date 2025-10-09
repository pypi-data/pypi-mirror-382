from typing import Any, Generic, List, Optional

from .base import TortoisePydanticBridge
from .generic import RESPONSE_PROTOCOL


class Create(TortoisePydanticBridge, Generic[RESPONSE_PROTOCOL]):
    async def create(self, data: dict[str, Any]) -> RESPONSE_PROTOCOL:
        obj = await self.get_model().create(**data)
        return await self.to_pydantic(obj)


class Retrieve(TortoisePydanticBridge, Generic[RESPONSE_PROTOCOL]):
    async def get_by_id(self, id: int) -> Optional[RESPONSE_PROTOCOL]:
        """Получает запись по ID и возвращает её в виде Pydantic-модели."""
        obj = await self.get_model().get_or_none(id=id)
        if obj is None:
            return None
        return await self.to_pydantic(obj)

    async def get_by(self, filters: dict[str, Any]) -> Optional[RESPONSE_PROTOCOL]:
        """Получает запись по ID и возвращает её в виде Pydantic-модели."""
        obj = await self.get_model().get_or_none(**filters)
        if obj is None:
            return None
        return await self.to_pydantic(obj)

    async def get_all(self) -> List[RESPONSE_PROTOCOL]:
        objs = await self.get_model().all()
        return [await self.to_pydantic(obj) for obj in objs]

    async def filter(self, filters: dict[str, Any]) -> List[RESPONSE_PROTOCOL]:
        objs = await self.get_model().filter(**filters)
        return [await self.to_pydantic(obj) for obj in objs]


class Update(TortoisePydanticBridge, Generic[RESPONSE_PROTOCOL]):
    async def update(self, filters: dict[str, Any], data: dict[str, Any]) -> int:
        return await self.get_model().filter(**filters).update(**data)

    async def update_and_get(
        self, filters: dict[str, Any], data: dict[str, Any]
    ) -> List[RESPONSE_PROTOCOL]:
        update_count = await self.get_model().filter(**filters).update(**data)

        if update_count > 0:
            objs = await self.get_model().filter(**filters).all()
            return [await self.to_pydantic(obj) for obj in objs]
        return []

    async def update_or_create(
        self, filters: dict[str, Any], data: dict[str, Any]
    ) -> tuple[RESPONSE_PROTOCOL, bool]:
        obj, is_created = await self.get_model().update_or_create(
            defaults=data,
            **filters,
        )
        return await self.to_pydantic(obj), is_created


class Delete(TortoisePydanticBridge):
    async def delete(self, filters: dict[str, Any]) -> None:
        obj = await self.get_model().get(**filters)
        await obj.delete()

    async def delete_by_id(self, id: int) -> None:
        obj = await self.get_model().get(id=id)
        await obj.delete()
