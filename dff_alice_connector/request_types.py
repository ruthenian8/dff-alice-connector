from typing import Optional
from enum import Enum

from pydantic import BaseModel


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


class YandexEntity(BaseModel):
    pass


class GeoEntity(YandexEntity):
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    airport: Optional[str] = None


class FioEntity(YandexEntity):
    first_name: Optional[str] = None
    patronymic_name: Optional[str] = None
    last_name: Optional[str] = None


class DatetimeEntity(YandexEntity):
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


class YandexIntent(Enum):
    CONFIRM = "YANDEX.CONFIRM"
    REJECT = "YANDEX.REJECT"
    HELP = "YANDEX.HELP"
    REPEAT = "YANDEX.REPEAT"
