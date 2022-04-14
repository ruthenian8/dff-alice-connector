from df_engine.core.keywords import GLOBAL, TRANSITIONS, RESPONSE
from df_engine.core import Context, Actor
import df_engine.conditions as cnd
from flask import Flask, request, Response

import dff_alice_connector as AliceConn
from dff_alice_connector.utils import get_user_id, set_state, get_initial_context

from dff_generic_response import GenericResponse

plot = {
    GLOBAL: {
        TRANSITIONS: {
            ("flow", "node_hi"): AliceConn.cnd.has_tokens(tokens=["привет", "хай", "здравствуй"]),
            ("flow", "node_ok"): AliceConn.cnd.has_tokens(tokens=["пока", "свидания", "прощай"]),
        }
    },
    "root": {
        "start": {RESPONSE: GenericResponse(text="что скажешь?", buttons=["привет", "до свидания"])},
        "fallback": {RESPONSE: GenericResponse(text="что скажешь?", buttons=["привет", "здравствуй"])},
    },
}

# initialize an actor
actor = Actor(plot=plot, start_label=("root", "start"), fallback_label=("root", "fallback"))

# initialize a state storage
connector = dict()

application = Flask(__name__)


@application.route("/alice-hook", methods=["POST"])
def respond() -> Response:
    update = request.form
    user_id = get_user_id(update)
    context: Context = connector.get(user_id, get_initial_context(user_id))
    # add newly received user data to the context
    context = set_state(context, update)  # this step is required for cnd.%_handler conditions to work

    # apply the actor
    updated_context = actor(context)

    response = updated_context.last_response

    # save the context
    connector[user_id] = updated_context

    yandex_response = AliceConn.alice_adapter(response)
    return yandex_response.dict(exclude_none=True)


if __name__ == "__main__":
    application.run(host="0.0.0.0")
