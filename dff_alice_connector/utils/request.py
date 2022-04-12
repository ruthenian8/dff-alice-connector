from df_engine.core import Context

from .common import get_positive_hash


def get_user_id(update: dict, use_application_id: bool = True) -> str:
    if use_application_id:
        uid = update["request"]["session"]["application"]["application_id"]
    else:
        uid = update["request"]["session"]["session_id"]

    return get_positive_hash(uid)


def set_state(ctx: Context, update: dict):
    ctx.add_request(update.get("request", {}).get("original_utterance", "data"))
    ctx.misc["ALICE_CONNECTOR"]["request"] = update["request"]


def get_request(ctx: Context) -> dict:
    return ctx.misc.get("ALICE_CONNECTOR", {}).get("request", {})


def get_initial_context(user_id: str):
    """
    Initialize a context with module-specific parameters.

    Parameters
    -----------

    user_id: str
        ID of the user from the update instance.

    """
    ctx = Context(id=user_id)
    ctx.misc.update({"ALICE_CONNECTOR": {"keep_flag": True, "request": None}})
    assert "ALICE_CONNECTOR" in ctx.misc
    return ctx
