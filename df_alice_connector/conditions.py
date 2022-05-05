"""Main module"""
from argparse import ArgumentError
from typing import Callable, Optional, List, Union
from functools import partialmethod

from df_engine.core import Context, Actor

from .request import (
    YandexEntityType,
    YandexEntityModel,
    YandexDefaultIntents,
    YandexRequestType,
    YandexEntity,
    YandexRequestModel,
)
from .utils import compare_func


class CndNamespace(object):
    def has_entities(
        self,
        ent_type: YandexEntityType,
        full_match: bool = True,
        entities: Optional[List[Union[dict, YandexEntity]]] = None,
        func: Optional[Callable] = None,
    ) -> Callable[[Context, Actor], bool]:
        """
        Use this method to filter out requests that include the specified entities of type {ent_type}

        Parameters
        -----------

        entities: Optional[List[Union[dict, YandexEntity]]]
            Entities to look up in the request (can be passed as a dict or as a pydantic model instance).
        func: Optional[Callable]
            A boolean function to apply to entities of the specified type.
        full_match: bool
            Whether the searched entity should fully match the ones in the request.

        """

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:
            request: YandexRequestModel = ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request")
            safe_ents = request and request.nlu and request.nlu.entities or []
            print(str(safe_ents))
            request_ents = [item.dict(exclude_none=True) for item in safe_ents]

            ents = [item.dict(exclude_none=True) if isinstance(item, YandexEntityModel) else item for item in entities]

            # print(str(request_ents))
            for ent in request_ents:
                if ent["type"] == ent_type.value:
                    evals = []
                    if func:
                        evals.append(func(ent["value"]))
                    if ents:
                        evals.append(compare_func(ent["value"], ents, full_match=full_match))
                    if evals and all(evals):
                        return True

            return False

        return handler

    has_datetime = partialmethod(has_entities, ent_type=YandexEntityType.DATETIME)

    has_geo = partialmethod(has_entities, ent_type=YandexEntityType.GEO)

    has_fio = partialmethod(has_entities, ent_type=YandexEntityType.FIO)

    has_number = partialmethod(has_entities, ent_type=YandexEntityType.NUMBER)

    def has_intents(
        self, intents: Optional[List[Union[YandexDefaultIntents, str]]] = None, func: Optional[Callable] = None
    ) -> Callable[[Context, Actor], bool]:
        """
        Use `has_intents` to filter requests that include a certain standard yandex intent.

        Parameters
        ----------

        intents: Optional[List[Union[YandexDefaultIntents, str]]]
            One or several target intent types. Can be passed a string if you use custom intents.
        func: Optional[Callable[[:py:class:`~df_alice_connector.request.Intent`], bool]]
            A boolean function to filter intents with.
        """

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request: YandexRequestModel = ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request")
            request_intents = request and request.nlu and request.nlu.intents or dict()

            if intents:
                intent_vals = {item if isinstance(item, str) else item.value for item in intents}
                filtered_intents = {key: value for key, value in request_intents.items() if key in intent_vals}
            else:
                filtered_intents = request_intents

            if func:
                filtered_intents = list(filter(func, filtered_intents.values()))

            return bool(filtered_intents)

        return handler

    def has_request_type(self, types: List[YandexRequestType]) -> Callable[[Context, Actor], bool]:
        """
        Use `has_request_type` to filter requests depending on the type.

        Parameters
        ----------

        types: List[YandexRequestType]
            One or several request types to filter.
        """

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request: YandexRequestModel = ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request")
            request_type = request and request.type or "SimpleUtterance"

            type_vals = [item.value for item in types]

            return request_type in type_vals

        return handler

    def has_tokens(self, tokens: List[str] = None, banned_tokens: List[str] = None) -> Callable[[Context, Actor], bool]:
        """
        Use `has_tokens` to filter requests depending on whether or not they include `tokens` or `banned_tokens`.

        Parameters
        -----------

        tokens: List[str]
            Tokens that should be included.
        banned_tokens: List[str]
            Tokens that should not be included.

        """
        if not tokens and not banned_tokens:
            raise ArgumentError("This method requires at least one parameter, `tokens` or `banned_tokens`, to be set.")

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request: YandexRequestModel = ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request")
            request_tokens = request and request.nlu and request.nlu.tokens or []

            if not request_tokens:
                return False

            evals = []

            if tokens:
                evals.append(bool(set(request_tokens) & set(tokens)))
            if banned_tokens:
                evals.append(not bool(set(request_tokens) & set(banned_tokens)))

            return all(evals) if evals else False

        return handler

    def has_payload(
        self, payload: Optional[dict] = None, func: Optional[Callable] = None
    ) -> Callable[[Context, Actor], bool]:
        """
        Use `has_payload` to process requests sent on button press.

        Parameters
        ----------

        payload: Optional[dict]
            You can provide a dictionary to compare against the request payload.
        func: Optional[Callable]
            Alternatively, provide a boolean function. The two options can be combined, but at least one is required.

        """
        if not payload and not func:
            raise ArgumentError("`payload` or `func` need to be provided")

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request: YandexRequestModel = ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request")
            request_payload = request and request.payload or dict()

            if not request_payload:
                return False

            evals = []

            if payload:
                evals.append(request_payload == payload)
            if func:
                evals.append(func(request_payload))

            return all(evals) if evals else False

        return handler

    def apply(self, func: Callable) -> Callable[[Context, Actor], bool]:
        """
        Use the `apply` method to compare the request against any boolean function.

        Parameters
        -----------

        func: Callable[[YandexRequestModel], bool]
            The function should take one parameter that has `YandexRequestModel` type.

        """

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request: YandexRequestModel = ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request", {})

            if not request:
                return False

            return bool(func(request))

        return handler


cnd = CndNamespace()

__all__ = ["cnd"]
