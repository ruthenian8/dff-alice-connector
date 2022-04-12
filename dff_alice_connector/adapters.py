import inspect
from functools import singledispatch


from .response_types import YandexResponseModel, YandexResponse
from .controls import Button, BigImage
from .utils import quote_url

try:
    from dff_generic_response import GenericResponse
except (ImportError, ModuleNotFoundError):
    GenericResponse = None


@singledispatch
def alice_adapter(response) -> YandexResponse:
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
        for link in response.links:
            link.url = quote_url(link.url)
        response.buttons = [Button(text=item, hide=True) for item in response.buttons]
        response.buttons += [Button(**item.dict()) for item in response.links]

        result = YandexResponse(response=YandexResponseModel(**dict(response)), **dict(response))

        if response.image_id:
            result.response.card = BigImage(image_id=response.image_id)

        if response.gallery:
            result.response.card = response.gallery

        return result
