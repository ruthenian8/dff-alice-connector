from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Extra, Field

from . import controls
from .directives import (
    StartPurchaseDirective,
    AudioPlayerDirective,
    ConfirmPurchaseDirective,
    StartAccountLinkingDirective,
)


class AdapterModel(BaseModel):
    class Config:
        extra = Extra.ignore
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class YandexStateModel(BaseModel):
    # value field should be initialized with a json-encoded object
    value: str = Field(..., max_length=500)  # state object size should not exceed 1024 bytes


class ItemMeta(BaseModel):
    content_id: Optional[str] = None
    title: Optional[str] = None
    title_tts: Optional[str] = None
    publication_date: Optional[str] = None
    expiration_date: Optional[str] = None


class YandexResponseModel(AdapterModel):
    text: str = ...
    tts: Optional[str] = None
    buttons: Optional[List[controls.Button]] = Field(default_factory=list)
    card: Optional[Union[controls.ItemsList, controls.BigImage, controls.ImageGallery]] = None
    end_session: bool = False
    show_item_meta: Optional[ItemMeta] = None
    directives: Optional[
        Union[StartPurchaseDirective, AudioPlayerDirective, ConfirmPurchaseDirective, StartAccountLinkingDirective]
    ] = None


class YandexResponse(AdapterModel):
    response: YandexResponseModel = ...
    session_state: Optional[YandexStateModel] = None
    user_state_update: Optional[YandexStateModel] = None
    application_state: Optional[YandexStateModel] = None
    analytics: Optional[Dict[str, Any]] = None
    version: Optional[str] = Field(default="1.0", const=True)
