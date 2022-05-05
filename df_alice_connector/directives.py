from typing import List, Literal, Optional, Dict
from uuid import UUID

from pydantic import BaseModel, HttpUrl, Field, validator


class Product(BaseModel):
    product_id: UUID = ...
    title: str = Field(..., max_length=256)
    price: float = Field(..., ge=0)
    user_price: float = Field(..., ge=0)
    nds_type: Literal["nds_20", "nds_10", "nds_0", "nds_none"] = Field(...)
    quantity: float = Field(..., ge=0)

    @validator("user_price")
    def validate_user_price(cls, uprice, values: dict):
        if values.get("price") and uprice > values["price"]:
            raise ValueError("user price should be equal or lower, than price")
        return uprice


class PurchaseData(BaseModel):
    purchase_request_id: str = Field(..., max_length=40)
    image_url: Optional[HttpUrl] = None
    caption: str = Field(..., max_length=512)
    description: str = Field(..., max_length=2048)
    currency: Literal["RUB"] = Field("RUB", const=True)
    type: Literal["BUY"] = Field("BUY", const=True)
    payload: str = Field(..., max_length=2048)
    merchant_key: str = Field(...)
    test_payment: bool = False
    products: List[Product] = Field(default_factory=list, min_items=1)


class StartPurchaseDirective(BaseModel):
    start_purchase: PurchaseData = ...


class AudioStream(BaseModel):
    url: str = ...
    offset_ms: str = ...
    token: str = ...


class AudioMeta(BaseModel):
    titile: Optional[str] = None
    sub_title: Optional[str] = None
    art: Optional[Dict[str, HttpUrl]] = None
    background_image: Optional[Dict[str, HttpUrl]] = None


class YandexAudio(BaseModel):
    stream: AudioStream = ...
    metadata: Optional[AudioMeta] = None


class AudioPlayerDirective(BaseModel):
    action: Literal["Play", "Stop"] = Field(default="Play", const=True)
    item: Optional[YandexAudio] = None


class StartAccountLinkingDirective(BaseModel):
    start_account_linking: Dict[str, str] = Field(default_factory=dict)


class ConfirmPurchaseDirective(BaseModel):
    confirm_purchase: Dict[str, str] = Field(default_factory=dict)
