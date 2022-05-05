import pytest

import df_alice_connector as AliceConn

from df_engine.core.keywords import GLOBAL, TRANSITIONS, RESPONSE
from df_engine.core import Context, Actor


@pytest.fixture
def script():
    script = {
        GLOBAL: {
            TRANSITIONS: {
                ("root", "start"): AliceConn.cnd.has_tokens(tokens=["привет", "хай", "здравствуй"]),
                ("root", "fallback"): AliceConn.cnd.has_tokens(tokens=["пока", "свидания", "прощай"]),
            }
        },
        "root": {
            "start": {RESPONSE: "привет"},
            "fallback": {RESPONSE: "пока"},
        },
    }
    yield script


@pytest.fixture
def actor(script):
    actor = Actor(script=script, start_label=("root", "start"), fallback_label=("root", "fallback"))
    yield actor


@pytest.fixture
def testing_request():
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
            "payload": {"quantity": 1},
            "nlu": {
                "tokens": ["включи", "свет", "на", "кухне", "пожалуйста"],
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
                    {
                        "type": "YANDEX.FIO",
                        "value": {"first_name": "антон", "patronymic_name": "павлович", "last_name": "чехов"},
                    },
                    {"type": "YANDEX.DATETIME", "value": {"day": -1, "day_is_relative": True}},
                ],
                "intents": {
                    "turn.on": {  # intent.
                        "slots": {  # slot list
                            "what": {"type": "YANDEX.STRING", "value": "свет"},
                            "where": {"type": "YANDEX.STRING", "value": "на кухне"},
                        }
                    },
                    "YANDEX.CONFIRM": {"slots": {}},
                },
            },
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
    yield request
