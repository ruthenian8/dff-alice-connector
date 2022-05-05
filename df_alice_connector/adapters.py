import logging
from pathlib import Path
from typing import List, Optional, Union, ClassVar
from pydantic import BaseModel, ValidationError, root_validator, validator

from .response import YandexResponseModel, AdapterModel, ItemMeta
from .controls import Button, BigImage, ImageGallery, ItemsList
from .utils.file_loader import FileLoader
from .directives import (
    StartPurchaseDirective,
    AudioPlayerDirective,
    ConfirmPurchaseDirective,
    StartAccountLinkingDirective,
)

import df_generics


class AliceAdapter(AdapterModel):
    text: str = ...
    _file_loader: ClassVar[Optional[FileLoader]] = None
    ui: Optional[BaseModel] = None
    buttons: Optional[List[Button]] = None
    attachments: Optional[df_generics.Attachments] = None
    image: Optional[df_generics.Image] = None
    card: Optional[Union[ItemsList, BigImage, ImageGallery]] = None
    show_item_meta: Optional[ItemMeta] = None
    state: Optional[df_generics.Session] = None
    end_session: bool = False
    audio: Optional[df_generics.Audio] = None
    tts: Optional[str] = None
    response: Optional[YandexResponseModel] = None
    directives: Optional[
        Union[StartPurchaseDirective, AudioPlayerDirective, ConfirmPurchaseDirective, StartAccountLinkingDirective]
    ] = None

    @classmethod
    def get_file_loader(cls, *args, **kwargs):
        cls._file_loader = FileLoader(*args, **kwargs)

    @root_validator(pre=True)
    def image_or_attachments(cls, values: dict):
        if values["attachments"] is not None and values["image"] is not None:
            raise ValidationError("Alice can only send one image or a gallery of images during one turn")
        return values

    @validator("buttons", always=True, pre=True)
    def set_buttons(cls, btn, values: dict):
        ui = values.get("ui")
        if ui and ui.buttons:
            return ui.buttons

        return btn

    @validator("card", always=True, pre=True)
    def set_card(cls, card, values: dict):
        attachments: df_generics.Attachments = values.get("attachments")
        if attachments and isinstance(attachments.files[0], df_generics.Image):
            attachments.files = list(map(cls.upload_image, attachments.files))
            return attachments

        image: df_generics.Image = values.get("image")
        if image:
            if not hasattr(image, "type"):
                image.type = "BigImage"
            image = cls.upload_image(image)
            return image

        return card

    @validator("end_session", always=True, pre=True)
    def set_state(cls, s_end, values: dict):
        state = values["state"]
        if state is not None and state == df_generics.Session.FINISHED:
            return True
        return s_end

    @validator("tts")
    def set_tts(cls, tts, values: dict):
        if tts is not None:
            return tts

        audio: Union[None, df_generics.Audio] = values["audio"]
        if audio is not None and isinstance(audio.source, Path):
            if not cls._file_loader:
                raise ValueError("Bind a FileLoader object to the clas by calling `get_file_loader` method")

            skill_id = cls._file_loader.skill_id
            audio_id = cls._file_loader.get_sound_by_filename(audio.source)
            if audio_id is not None:
                return f"<speaker audio='dialogs-upload/{skill_id}/{audio_id}.opus'>"

        return None

    @validator("response", always=True, pre=False)
    def set_response(cls, resp, values):
        return YandexResponseModel.parse_obj(values)

    @classmethod
    def upload_image(cls, item: df_generics.Image):

        if item.id is None and item.source is not None:
            if not cls._file_loader:
                raise ValueError("Bind a FileLoader object to the clas by calling `get_file_loader` method")

            if isinstance(item.source, Path):
                item.id = cls._file_loader.get_image_by_filename(item.source)
            else:
                item.id = cls._file_loader.get_image_by_url(item.source)

        if not item.id:
            logging.warning(f"Failed to upload a file from source {item.source} for skill {cls._file_loader.skill_id}")
            return None
        return item
