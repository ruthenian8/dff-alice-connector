import sys

import pytest

sys.path.insert(0, "../")
from df_alice_connector.adapters import AliceAdapter
from df_alice_connector.controls import ItemsListHeader, Button as AliceButton
from df_alice_connector.response import YandexResponse

import df_generics as dfg


@pytest.mark.parametrize(
    "generic_response",
    [
        dfg.Response(text="some_text"),
        dfg.Response(text="some_text", image=dfg.Image(id="someid")),
        dfg.Response(text="some_text", image=dfg.Image(id="someid", type="BigImage")),
        dfg.Response(
            text="some_text", ui=dfg.Keyboard(buttons=[dfg.Button(text="button_text", payload='{"info":"1"}')] * 2)
        ),
    ],
)
def test_response_parsing(generic_response):
    adapter = AliceAdapter.parse_obj(generic_response)
    response = YandexResponse.parse_obj(adapter)
    assert response
    assert response.response
    assert response.response.text == "some_text"


@pytest.mark.parametrize(
    "generic_response",
    [
        dfg.Response(
            text="some_text", attachments=dfg.Attachments(files=[dfg.Image(id="someid")] * 2, type="ImageGallery")
        ),
        dfg.Response(
            text="some_text",
            attachments=dfg.Attachments(
                files=[dfg.Image(id="someid")] * 2,
            ),
        ),
        dfg.Response(
            text="some_text",
            attachments=dfg.Attachments(
                files=[dfg.Image(id="someid")] * 2, type="ItemsList", header=ItemsListHeader(text="item_list")
            ),
        ),
    ],
)
def test_response_card(generic_response):
    adapter = AliceAdapter.parse_obj(generic_response)
    response = YandexResponse.parse_obj(adapter)
    assert response
    assert response.response
    assert response.response.text == "some_text"
    assert response.response.card
    assert response.response.card.type
