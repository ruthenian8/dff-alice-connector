"""Main module"""
from argparse import ArgumentError
from typing import Callable, Optional, List, Union, NamedTuple
from functools import partialmethod

from pydantic import BaseModel
from df_engine.core import Context, Actor

from .request_types import YandexEntityType, YandexIntent, YandexRequestType, YandexEntity
from .utils import compare_func


class CndNamespace(object):
    def has_entities(
        self,
        ent_type: YandexEntityType,
        full_match: bool = True,
        entities: Optional[List[Union[dict, YandexEntity]]] = None,
        func: Optional[Callable] = None,
    ) -> Callable:
        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request_ents = ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {}).get("nlu", {}).get("entities", [])

            entities = [item.dict(exclude_none=True) if isinstance(item, YandexEntity) else item for item in entities]

            for ent in request_ents:
                if ent["type"] == ent_type.value:

                    evals = []
                    if func:
                        evals.append(func(ent["value"]))
                    if entities:
                        evals.append(compare_func(ent["value"], entities, full_match=full_match))
                    if evals and all(evals):
                        return True

            return False

        return handler

    has_datetime = partialmethod(has_entities, ent_type=YandexEntityType.DATETIME)

    has_geo = partialmethod(has_entities, ent_type=YandexEntityType.GEO)

    has_fio = partialmethod(has_entities, ent_type=YandexEntityType.FIO)

    has_number = partialmethod(has_entities, ent_type=YandexEntityType.NUMBER)

    def has_intents(self, intents: List[YandexIntent]):
        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request_intents = ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {}).get("nlu", {}).get("intents", {})

            intents = [item.value for item in intents]

            return bool(request_intents.keys() & intents)

        return handler

    def has_request_type(self, types: List[YandexRequestType]):
        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request_type = ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {}).get("type", "SimpleUtterance")

            types = [item.value for item in types]

            return request_type in types

        return handler

    def has_tokens(self, tokens: List[str] = None, banned_tokens: List[str] = None):
        if not tokens and not banned_tokens:
            raise ArgumentError("`tokens` or `banned_tokens` need to be provided.")

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request_tokens = ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {}).get("nlu", {}).get("tokens", [])

            if not request_tokens:
                return False

            evals = []

            if tokens:
                evals.append(bool(set(request_tokens) & set(tokens)))
            if banned_tokens:
                evals.append(not bool(set(request_tokens) & set(banned_tokens)))

            return all(evals) if evals else False

        return handler

    def has_payload(self, payload: Optional[dict] = None, func: Optional[Callable] = None):
        if not payload and not func:
            raise ArgumentError("`payload` or `func` need to be provided")

        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request_payload = ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {}).get("payload", {})

            if not request_payload:
                return False

            evals = []

            if payload:
                evals.append(request_payload == payload)
            if func:
                evals.append(func(request_payload))

            return all(evals) if evals else False

        return handler

    def apply(self, func: Callable):
        def handler(ctx: Context, actor: Actor, *args, **kwargs) -> bool:

            request = ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {})

            if not request:
                return False

            return bool(func(request))

        return handler


cnd = CndNamespace()

__all__ = ["cnd"]
