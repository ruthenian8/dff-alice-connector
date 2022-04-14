import sys

import pytest

import dff_alice_connector as AliceConn
from dff_alice_connector.response_types import YandexResponseModel, YandexResponse
from dff_alice_connector.request_types import YandexRequestModel, YandexRequest
from dff_alice_connector.adapters import GenericResponse

# uncomment the following line, if you want to run your examples during the test suite or import from them
# sys.path.insert(0, "../")


def test_generic_init():
    gr = GenericResponse(text="Иван родил девчонку", tts="Иван родил девчонку")
    assert gr.misc_options["tts"] == "Иван родил девчонку"
    response = AliceConn.alice_adapter(gr)
    assert isinstance(response, YandexResponse)
    assert response.response.tts == "Иван родил девчонку"


def test_start():
    response_1 = AliceConn.alice_adapter("Иван родил девчонку")
    response_2 = AliceConn.alice_adapter({"text": "Иван родил девчонку", "tts": "Иван родил девчонку"})
    assert isinstance(response_1, YandexResponse)
    assert isinstance(response_2, YandexResponse)


def test_request_model_parsing():
    request = {
        "command": "включи свет на кухне, пожалуйста",
        "type": "SimpleUtterance",
        "nlu": {
            "entities": [
                {
                    "type": "YANDEX.GEO",
                    "value": {
                        "country": "россия",
                        "city": "москва",
                        "street": "улица льва толстого",
                        "house_number": "16",
                    },
                },
                {"type": "YANDEX.DATETIME", "value": {"day": -1, "day_is_relative": True}},
            ],
            "intents": {
                "turn.on": {  # Интент.
                    "slots": {  # Список слотов.
                        "what": {"type": "YANDEX.STRING", "value": "свет"},
                        "where": {"type": "YANDEX.STRING", "value": "на кухне"},
                    }
                }
            },
        },
    }

    parsed = YandexRequestModel.parse_obj(request)
    assert parsed


def test_request_object_parsing():
    request = {
        "meta": {
            "locale": "ru-RU",
            "timezone": "Europe/Moscow",
            "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
            "interfaces": {"screen": {}, "payments": {}, "account_linking": {}, "audio_player": {}},
        },
        "request": {
            "command": "включи свет на кухне, пожалуйста",
            "type": "SimpleUtterance",
        },
        "session": {
            "message_id": 0,
            "session_id": "2eac4854-fce721f3-b845abba-20d60",
            "skill_id": "3ad36498-f5rd-4079-a14b-788652932056",
            "user_id": "47C73714B580ED2469056E71081159529FFC676A4E5B059D629A819E857DC2F8",
            "user": {
                "user_id": "6C91DA5198D1758C6A9F63A7C5CDDF09359F683B13A18A151FBF4C8B092BB0C2",
                "access_token": "AgAAAAAB4vpbAAApoR1oaCd5yR6eiXSHqOGT8dT",
            },
            "application": {"application_id": "47C73714B580ED2469056E71081159529FFC676A4E5B059D629A819E857DC2F8"},
            "new": True,
        },
        "state": {"session": {"value": 10}, "user": {"value": 42}, "application": {"value": 37}},
        "version": "1.0",
    }

    parsed = YandexRequest.parse_obj(request)
    assert parsed
