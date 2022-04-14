from functools import singledispatch
from typing import Optional, Union, List, Dict, Any
from mimetypes import guess_type

from pydantic import BaseModel, Field

from .response_types import YandexResponseModel, YandexResponse
from .controls import Button, BigImage, ImageGallery, ItemsList
from .request_types import YandexCommands
from .utils import quote_url
from .utils.file_loader import file_loader


try:
    from dff_generic_response import GenericResponse
except (ImportError, ModuleNotFoundError):
    GenericResponse = None


class AliceOptions(BaseModel):
    gallery: Optional[ImageGallery] = None
    image_id: Optional[str] = None
    sound_id: Optional[str] = None
    card: Optional[Union[ItemsList, BigImage, ImageGallery]] = None
    tts: Optional[str] = None  # goes to Alice's tts response section
    commands: Optional[List[YandexCommands]] = None
    directives: Optional[dict] = None
    show_item_meta: Optional[BaseModel] = None
    should_listen: Optional[bool] = None

    def __init__(
        self,
        *,
        gallery=None,
        image_id=None,
        tts=None,
        commands=None,
        card=None,
        directives=None,
        show_item_meta=None,
        should_listen=None,
    ):

        if not commands:
            commands = []

        if not directives:
            directives = {}

        if YandexCommands.REQUEST_GEOLOCATION in commands or YandexCommands.REQUEST_GEOLOCATION.value in commands:
            directives[YandexCommands.REQUEST_GEOLOCATION.value] = {}

        super().__init__(**locals())


@singledispatch
def alice_adapter(response) -> YandexResponse:
    """
    An adapter that casts different kinds of responses to the YandexResponse type.
    Supported types are: str, dict, GenericResponse from dff-generic-response.
    """
    raise NotImplementedError


@alice_adapter.register
def _(response: str):
    return YandexResponse(response=YandexResponseModel(text=response))


@alice_adapter.register
def _(response: dict):
    return YandexResponse(response=YandexResponseModel(**response), **response)


if GenericResponse is not None:

    @alice_adapter.register
    def _(response: GenericResponse):
        response.misc_options = AliceOptions.parse_obj(response.misc_options)

        if YandexCommands.EXIT or "exit" in response.commands:
            response.end_session = True

        for link in response.links:
            link.url = quote_url(link.url)
        response.buttons = [Button(text=item) for item in response.buttons]
        response.buttons += [Button(**item.dict()) for item in response.links]

        if file_loader:
            if response.image_url:
                response.misc_options.image_id = file_loader.get_image_by_url(response.image_url)
            elif response.attachment and guess_type(response.attachment).startswith("image"):
                response.misc_options.image_id = file_loader.get_image_by_filename(response.attachment)

            if response.attachment and guess_type(response.attachment).startswith("audio"):
                audio_id = file_loader.get_sound_by_filename(response.attachment)
                response.misc_options.tts = (
                    (f"<speaker audio='dialogs-upload/{file_loader.skill_id}/{audio_id}.opus'>") if audio_id else None
                )

        init_args = {**dict(response), **dict(response.misc_options)}

        result = YandexResponse(response=YandexResponseModel(**init_args), **init_args)

        if not result.response.card:
            if response.misc_options.image_id:
                result.response.card = BigImage(image_id=response.misc_options.image_id)
            elif response.misc_options.gallery:
                result.response.card = response.misc_options.gallery

        return result
