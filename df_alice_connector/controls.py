from abc import ABC
from typing import Optional, List

from pydantic import BaseModel, Field, HttpUrl, root_validator, ValidationError


class BaseButton(BaseModel, ABC):
    url: Optional[HttpUrl] = Field(default=None, alias="source")
    payload: Optional[str] = Field(
        default=None, max_length=2048
    )  # We assume that the field is initialized with a jsonified dict


class CardButton(BaseButton):
    text: Optional[str] = Field(default=None, max_length=64, min_length=1)

    @root_validator(pre=False)
    def text_or_url(cls, values: dict):
        if bool(values["url"]) == bool(values["text"]):
            raise ValidationError("Card button requires exactly one parameter, text or url, to be set.")
        return values


class Button(BaseButton):
    title: str = Field(..., max_length=64, min_length=1, alias="text")
    hide: bool = True


class ItemsListHeader(BaseModel):
    text: str = Field(..., max_length=64, min_length=1)


class ItemsListFooter(BaseModel):
    text: str = Field(..., max_length=64, min_length=1)
    button: Optional[CardButton] = None


class Image(BaseModel):
    image_id: str = Field(..., alias="id")
    title: Optional[str] = Field(default=None, max_length=128)
    button: Optional[CardButton] = None


class ImageWithDescription(Image):
    description: Optional[str] = Field(default=None, max_length=256)


class BaseCard(BaseModel, ABC):
    type: str = ...


class BigImage(ImageWithDescription, BaseCard):
    type: str = Field("BigImage", const=True)
    image_id: str = Field(..., alias="id")
    title: Optional[str] = Field(default=None, alias="title", max_length=128)
    description: Optional[str] = None
    button: Optional[CardButton] = None


class ImageGallery(BaseCard):
    type: str = Field("ImageGallery", const=True)
    items: List[Image] = Field(default_factory=list, alias="files", max_items=10, min_items=2)


class ItemsList(BaseCard):
    type: str = Field("ItemsList", const=True)
    items: List[ImageWithDescription] = Field(default_factory=list, alias="files", max_items=5, min_items=2)
    header: Optional[ItemsListHeader] = None
    footer: Optional[ItemsListFooter] = None
