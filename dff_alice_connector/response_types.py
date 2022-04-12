from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator

from .controls import *


class YandexStateModel(BaseModel):
    value: BaseModel


class ItemMeta(BaseModel):
    content_id: Optional[str] = None
    title: Optional[str] = None
    title_tts: Optional[str] = None
    publication_date: Optional[str] = None
    expiration_date: Optional[str] = None


class YandexResponseModel(BaseModel):
    text: str = ...
    tts: Optional[str] = None
    buttons: Optional[List[Button]] = None
    card: Optional[BaseCard] = None
    end_session: bool = False
    show_item_meta: Optional[ItemMeta] = None
    directives: Optional[Dict[str, str]] = None

    def __init__(
        self,
        *,
        text,
        tts=None,
        buttons=None,
        card=None,
        end_session=False,
        show_item_meta=None,
        directives=None,
        **kwargs
    ) -> None:

        if not buttons:
            directives = list()

        if not directives:
            directives = dict()

        super().__init__(
            text=text,
            tts=tts,
            buttons=buttons,
            card=card,
            end_session=end_session,
            show_item_meta=show_item_meta,
            directives=directives,
        )


class YandexResponse(BaseModel):
    response: YandexResponseModel = ...
    session_state: Optional[YandexStateModel] = None
    user_state_update: Optional[YandexStateModel] = None
    application_state: Optional[YandexStateModel] = None
    analytics: Optional[Dict[str, Any]] = None
    version: Optional[str] = None

    def __init__(
        self,
        *,
        response,
        session_state=None,
        user_state_update=None,
        application_state=None,
        analytics=None,
        version=None,
        **kwargs
    ) -> None:

        if not version:
            version = "1.0"

        super().__init__(
            response=response,
            session_state=session_state,
            user_state_update=user_state_update,
            application_state=application_state,
            analytics=analytics,
            version=version,
        )
