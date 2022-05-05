from df_engine.core.keywords import GLOBAL, TRANSITIONS, RESPONSE
from df_engine.core import Context, Actor
from flask import Flask, request, Response

import df_alice_connector as AliceConn
from df_alice_connector.request import YandexRequest
from df_alice_connector.response import YandexResponse
from df_alice_connector.utils import get_user_id, set_state, get_initial_context

import df_generics as dfg

script = {
    GLOBAL: {
        TRANSITIONS: {
            ("root", "start"): AliceConn.cnd.has_tokens(tokens=["привет", "хай", "здравствуй"]),
            ("root", "fallback"): AliceConn.cnd.has_tokens(tokens=["пока", "свидания", "прощай"]),
        }
    },
    "root": {
        "start": {RESPONSE: dfg.Response(text="hello sound", audio="hello.mp3")},
        "fallback": {RESPONSE: dfg.Response(text="goodbye sound", audio="bye.mp3")},
    },
}

# initialize an actor
actor = Actor(script=script, start_label=("root", "start"), fallback_label=("root", "fallback"))

# initialize a state storage
connector = dict()

application = Flask(__name__)


@application.route("/alice-hook", methods=["POST"])
def respond() -> Response:
    update = YandexRequest.parse_obj(request.form)
    user_id = get_user_id(update)
    context: Context = connector.get(user_id, get_initial_context(user_id))
    # add newly received user data to the context
    set_state(context, update)  # this step is required for cnd.%_handler conditions to work

    # apply the actor
    updated_context = actor(context)

    response = updated_context.last_response

    # save the context
    connector[user_id] = updated_context

    adapted_response = AliceConn.AliceAdapter.parse_obj(response)
    yandex_response = YandexResponse.parse_obj(adapted_response)
    return yandex_response.dict(exclude_none=True)


if __name__ == "__main__":
    application.run(host="0.0.0.0")
