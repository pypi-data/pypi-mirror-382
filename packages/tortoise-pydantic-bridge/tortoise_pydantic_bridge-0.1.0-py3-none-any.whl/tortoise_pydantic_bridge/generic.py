from typing import TypeVar

from pydantic import BaseModel

RESPONSE_PROTOCOL = TypeVar("RESPONSE_PROTOCOL", bound=BaseModel)
