import sys

import pytest

import dff_alice_connector as AliceConn
from dff_alice_connector.response_types import YandexResponseModel, YandexResponse

# uncomment the following line, if you want to run your examples during the test suite or import from them
# sys.path.insert(0, "../")


def test_start():
    response_1 = AliceConn.alice_adapter("Иван родил девчонку")
    response_2 = AliceConn.alice_adapter({"text": "Иван родил девчонку", "tts": "Иван родил девчонку"})
    assert isinstance(response_1, YandexResponse)
    assert isinstance(response_2, YandexResponse)
