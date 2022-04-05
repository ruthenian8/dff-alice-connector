import dialogic

from df_engine.core.keywords import GLOBAL, TRANSITIONS, RESPONSE
from df_engine.core import Context, Actor
import df_engine.conditions as cnd

from dff_alice_connector.manager import DFFManager
import dff_alice_connector.cnd as match_cnd

cnd_factory = match_cnd.Matchers()

plot = {
    GLOBAL: {
        TRANSITIONS: {
            ("flow", "node_hi"): cnd_factory.make_condition(
                phrases=["Hi", "Hello", "Hey there"], matcher_type="cosine"
            ),
            ("flow", "node_ok"): cnd_factory.make_condition(
                phrases=["Bye", "Goodbye", "See you"], matcher_type="cosine"
            ),
        }
    },
    "root": {
        "start": {RESPONSE: "Hi!!!"},
        "fallback": {RESPONSE: "Bye!!!"},
    },
}

cnd_factory.initialize()

# initialize an actor
actor = Actor(plot=plot, start_label=("root", "start"), fallback_label=("root", "fallback"))

# initialize a state storage
db_connector = dict()

if __name__ == "__main__":
    manager = dialogic.dialog_manager.CascadeDialogManager(DFFManager(actor=actor, db_connector=db_connector))
    connector = dialogic.dialog_connector.DialogConnector(
        dialog_manager=manager, storage=dialogic.storage.session_storage.BaseStorage()
    )
    server = dialogic.server.flask_server.FlaskServer(connector=connector)
    server.parse_args_and_run()
