from abc import ABC, abstractmethod
from typing import Dict, Optional, List

from pydantic import BaseModel, Field, validator

from .utils import get_size_validator, get_len_validator


class BaseButton(BaseModel, ABC):
    url: str
    payload: Dict[str, str]

    _url_validator = validator("url", allow_reuse=True)(get_size_validator(1024))
    _payload_validator = validator("payload", allow_reuse=True)(get_size_validator(4096))


class CardButton(BaseButton):
    text: str = ...

    _text_validator = validator("text", allow_reuse=True)(get_len_validator(64))


class Button(BaseButton):
    title: str = ...
    hide: bool = False

    _title_validator = validator("title", allow_reuse=True)(get_len_validator(64))


class ItemsListHeader(BaseModel):
    text: str = ...

    _text_validator = validator("text", allow_reuse=True)(get_len_validator(64))


class ItemsListFooter(BaseModel):
    text: str = ...
    button: Optional[CardButton] = None

    _text_validator = validator("text", allow_reuse=True)(get_len_validator(64))


class Image(BaseModel):
    image_id: str = ...
    title: Optional[str] = None
    button: Optional[CardButton] = None

    _title_valdiator = validator("title", allow_reuse=True)(get_len_validator(128))


class ImageWithDescription(Image):
    description: Optional[str] = None

    _desc_validator = validator("description", allow_reuse=True)(get_len_validator(256))


class BaseCard(BaseModel, ABC):
    type: str = ...

    @abstractmethod
    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class BigImage(ImageWithDescription, BaseCard):
    type: str = Field("BigImage", const=True)


class ImageGallery(BaseCard):
    type: str = Field("ImageGallery", const=True)
    items: List[Image] = Field(default_factory=list)

    _items_validator = validator("items", allow_reuse=True)(get_len_validator(10))


class ItemsList(BaseCard):
    type: str = Field("ItemsList", const=True)
    items: List[ImageWithDescription] = Field(default_factory=list)
    header: Optional[ItemsListHeader] = None
    footer: Optional[ItemsListFooter] = None

    _items_validator = validator("items", allow_reuse=True)(get_len_validator(5))
