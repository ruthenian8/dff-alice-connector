from abc import ABC
import json
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, validator


class YandexCommands(Enum):
    EXIT = "exit"
    REQUEST_GEOLOCATION = "request_geolocation"


class YandexRequestType(Enum):
    PLAYBACKSTARTED = "AudioPlayer.PlaybackStarted"
    PLAYBACKFINISHED = "AudioPlayer.PlaybackFinished"
    PLAYBACKNEARLYFINISHED = "AudioPlayer.PlaybackNearlyFinished"
    PLAYBACKSTOPPED = "AudioPlayer.PlaybackStopped"
    PLAYBACKFAILED = "AudioPlayer.PlaybackFailed"
    BUTTONPRESSED = "ButtonPressed"
    CONFIRMATION = "Purchase.Confirmation"
    PULL = "Show.Pull"
    SIMPLEUTTERANCE = "SimpleUtterance"


class YandexEntityType(Enum):
    GEO = "YANDEX.GEO"
    DATETIME = "YANDEX.DATETIME"
    NUMBER = "YANDEX.NUMBER"
    FIO = "YANDEX.FIO"


class YandexDefaultIntents(Enum):
    """
    This type can be used in `has_intent` instead of a string name.
    For custom intents use the string name of the intent.
    """

    CONFIRM = "YANDEX.CONFIRM"
    REJECT = "YANDEX.REJECT"
    HELP = "YANDEX.HELP"
    REPEAT = "YANDEX.REPEAT"


class YandexEntityModel(BaseModel, ABC):
    pass


class GeoEntity(YandexEntityModel):
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    airport: Optional[str] = None


class FioEntity(YandexEntityModel):
    first_name: Optional[str] = None
    patronymic_name: Optional[str] = None
    last_name: Optional[str] = None


class DatetimeEntity(YandexEntityModel):
    year: Optional[int] = None
    year_is_relative: Optional[bool] = None
    month: Optional[int] = None
    month_is_relative: Optional[bool] = None
    day: Optional[int] = None
    day_is_relative: Optional[bool] = None
    hour: Optional[int] = None
    hour_is_relative: Optional[bool] = None
    minute: Optional[int] = None
    minute_is_relative: Optional[bool] = None


class YandexEntity(BaseModel, use_enum_values=True):
    type: YandexEntityType = ...
    value: Any = ...

    @validator("value", pre=False)
    def set_value_type(cls, val, values):
        _type = values["type"]
        if _type == YandexEntityType.FIO.value:
            val = FioEntity.parse_obj(val)
        elif _type == YandexEntityType.GEO.value:
            val = GeoEntity.parse_obj(val)
        elif _type == YandexEntityType.DATETIME.value:
            val = DatetimeEntity.parse_obj(val)
        elif _type == YandexEntityType.NUMBER.value:
            val = float(val)
        return val


class Span(BaseModel):
    start: int = ...
    end: int = ...


class Slot(BaseModel):
    type: str = ...
    tokens: Optional[Span] = None
    value: Optional[Any] = None


class Intent(BaseModel):
    slots: Dict[str, Slot] = Field(default_factory=dict)


class NLU(BaseModel):
    tokens: List[str] = Field(default_factory=list)
    entities: List[YandexEntity] = Field(default_factory=list)
    intents: Dict[str, Intent] = Field(default_factory=dict)

    def has_intent(self, intent: str):
        return intent in self.intents

    def get_forms(self):
        return self.dict(include={"intents"})


class Meta(BaseModel):
    locale: str = ...
    timezone: str = ...
    client_id: str = ...
    interfaces: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class YandexRequestModel(BaseModel, use_enum_values=True):
    command: Optional[str] = None
    original_utterance: Optional[str] = None
    type: YandexRequestType = ...
    markup: Optional[Dict[str, str]] = None
    payload: Optional[Dict[str, Any]] = None
    nlu: Optional[NLU] = None
    show_type: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

    @validator("payload", pre=True)
    def set_payload(cls, pl):
        if isinstance(pl, str):
            return json.loads(pl)
        return pl


class Application(BaseModel):
    application_id: str = ...


class Session(BaseModel):
    session_id: str
    message_id: int
    skill_id: str
    user_id: Optional[str] = None
    user: Optional[Dict[str, str]] = None
    application: Optional[Application] = None
    new: bool = False


class State(BaseModel):
    session: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None
    application: Optional[Dict[str, Any]] = None
    audio_player: Optional[Dict[str, Any]] = None


class YandexRequest(BaseModel):
    meta: Meta = ...
    request: YandexRequestModel = ...
    session: Optional[Session] = None
    state: Optional[State] = None
    version: str = Field("1.0", const=True)

    def is_new_session(self):
        return self.session and self.session.new is True
