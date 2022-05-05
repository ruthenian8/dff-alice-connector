import sys

import pytest

# uncomment the following line, if you want to run your examples during the test suite or import from them
sys.path.insert(0, "../")

import df_alice_connector as AliceConn

from df_alice_connector.request import (
    DatetimeEntity,
    FioEntity,
    GeoEntity,
    YandexDefaultIntents,
    YandexRequestModel,
    YandexRequest,
    YandexRequestType,
)
from df_alice_connector.utils import get_initial_context, set_state


def test_request_model_parsing(testing_request):
    request = testing_request.get("request")
    parsed = YandexRequestModel.parse_obj(request)
    assert parsed


def test_request_object_parsing(testing_request):
    parsed = YandexRequest.parse_obj(testing_request)
    assert parsed


# AliceConn.cnd.has_geo(entities=[GeoEntity(...), GeoEntity(...)], full_match=...)
@pytest.mark.parametrize(
    "params,expected",
    [
        (
            dict(
                entities=[
                    GeoEntity(
                        **{"country": "россия", "city": "москва", "street": "улица льва толстого", "house_number": "16"}
                    )
                ]
            ),
            True,
        ),
        (
            dict(
                entities=[GeoEntity(**{"country": "россия", "city": "москва", "street": "улица пушкина"})],
                full_match=False,
            ),
            True,
        ),
        (dict(entities=[{"country": "россия", "city": "москва", "street": "улица пушкина"}], full_match=False), True),
        (
            dict(
                entities=[
                    GeoEntity(
                        **{"country": "монако", "city": "монако", "street": "улица льва толстого", "house_number": "16"}
                    )
                ]
            ),
            False,
        ),
        (
            dict(
                entities=[GeoEntity(**{"country": "россия", "city": "москва", "street": "улица пушкина"})],
                full_match=True,
            ),
            False,
        ),
    ],
)
def test_has_geo(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_geo(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.has_fio(entities=[FioEntity(...), FioEntity(...)], full_match=...)
@pytest.mark.parametrize(
    "params,expected",
    [
        (
            dict(
                entities=[FioEntity(**{"first_name": "антон", "patronymic_name": "павлович", "last_name": "чехов"})],
                full_match=True,
            ),
            True,
        ),
        (dict(entities=[FioEntity(**{"first_name": "антон", "last_name": "чехов"})], full_match=False), True),
        (dict(entities=[FioEntity(**{"first_name": "александр", "last_name": "пушкин"})], full_match=False), False),
    ],
)
def test_has_fio(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_fio(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.has_datetime(entities=[DatetimeEntity(...), DatetimeEntity(...)], full_match=...)
@pytest.mark.parametrize(
    "params,expected",
    [
        (dict(entities=[DatetimeEntity(**{"day": -1})], full_match=False), True),
        (dict(entities=[DatetimeEntity(**{"day": 1})], full_match=False), False),
    ],
)
def test_has_datetime(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_datetime(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.has_request_type(types=[YandexRequestType.SIMPLEUTTERANCE, ...])
@pytest.mark.parametrize(
    "params,expected",
    [
        (dict(types=[YandexRequestType.SIMPLEUTTERANCE, YandexRequestType.PLAYBACKSTARTED]), True),
        (dict(types=[YandexRequestType.PLAYBACKFINISHED, YandexRequestType.PLAYBACKSTARTED]), False),
    ],
)
def test_has_request_type(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_request_type(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.has_payload(func = lambda x: ..., payload={"key": "value"})
@pytest.mark.parametrize(
    "params,expected",
    [
        (dict(payload={"quantity": 1}), True),
        (dict(payload={"quantity": 2}), False),
        (dict(func=lambda x: x["quantity"] == 1), True),
        (dict(func=lambda x: x["quantity"] != 1), False),
    ],
)
def test_has_payload(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_payload(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.has_intents(intents=[YandexDefaultIntents.CONFIRM, ...])
@pytest.mark.parametrize(
    "params,expected",
    [
        (dict(intents=[YandexDefaultIntents.CONFIRM]), True),
        (dict(intents=[YandexDefaultIntents.CONFIRM], func=lambda x: bool(x)), True),
        (dict(intents=[YandexDefaultIntents.REJECT]), False),
    ],
)
def test_has_intents(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_intents(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.has_tokens(tokens=["token_1", ...], banned_tokens=["token_3", ...])
@pytest.mark.parametrize(
    "params,expected",
    [
        (dict(tokens=["кухне"]), True),
        (dict(tokens=["столовой"]), False),
        (dict(banned_tokens=["столовой"]), True),
        (dict(banned_tokens=["пожалуйста"]), False),
    ],
)
def test_has_tokens(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.has_tokens(**params)
    assert condition(ctx, actor) == expected


# AliceConn.cnd.apply(func=lambda request: request.command.startswith("включи свет"))
@pytest.mark.parametrize(
    "params,expected",
    [
        ({"func": lambda request: request.command.startswith("включи свет")}, True),
        ({"func": lambda request: request.command.startswith("выключи свет")}, False),
    ],
)
def test_apply(testing_request, actor, params, expected):
    parsed = YandexRequest.parse_obj(testing_request)
    ctx = get_initial_context("123123")
    set_state(ctx, parsed)
    condition = AliceConn.cnd.apply(**params)
    assert condition(ctx, actor) == expected
