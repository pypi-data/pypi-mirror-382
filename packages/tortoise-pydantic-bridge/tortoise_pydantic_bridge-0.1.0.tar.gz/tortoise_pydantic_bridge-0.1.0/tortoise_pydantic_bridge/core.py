from typing import Type

from pydantic import BaseModel
from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator
from tortoise.models import Model

from .generic import RESPONSE_PROTOCOL


class TortoisePydanticBridge:
    """
    Мост между Tortoise ORM и Pydantic для конвертации моделей.

    Attributes:
        model: Класс модели Tortoise ORM
        pydantic_model: Опциональный класс Pydantic модели (если None - модель создастся динамически
       с учётом всех связей)
    """

    model: Type[Model]
    pydantic_model: Type[PydanticModel]
    base_model: Type[BaseModel]

    def get_model(self) -> Type[Model]:
        assert self.model is not None, f'{self.__class__.__name__}: не указана модель'
        return self.model

    def get_pydantic_model(self) -> Type[PydanticModel]:
        """
        Возвращает Pydantic модель:
        - Если pydantic_model задан - возвращает его
        - Если pydantic_model==None - создаёт динамически через pydantic_model_creator
        """
        return (
            self.pydantic_model
            if self.pydantic_model
            else pydantic_model_creator(self.get_model())
        )

    def get_base_model(self) -> Type[BaseModel]:
        assert (
            self.base_model is not None
        ), f'{self.__class__.__name__}: не указана base_model'
        return self.base_model

    async def to_pydantic_model(self, obj: Model) -> PydanticModel:
        return await self.get_pydantic_model().from_tortoise_orm(obj)

    async def to_pydantic(self, obj: Model) -> RESPONSE_PROTOCOL:
        py_model = await self.get_pydantic_model().from_tortoise_orm(obj)
        return self.get_base_model()(**py_model.model_dump())  # type: ignore[return-value]
