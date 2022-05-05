from df_engine.core import Context

from .common import get_positive_hash
from ..request import YandexRequest


def get_user_id(update: YandexRequest, use_application_id: bool = True) -> str:
    if use_application_id:
        uid = update.session.application.application_id
    else:
        uid = update.session.session_id

    return get_positive_hash(uid)


def set_state(ctx: Context, update: YandexRequest):
    ctx.add_request(update.request and update.request.original_utterance or "data")
    ctx.framework_states["ALICE_CONNECTOR"]["request"] = update.request


def get_request(ctx: Context) -> dict:
    return ctx.framework_states.get("ALICE_CONNECTOR", {}).get("request", {})


def get_initial_context(user_id: str):
    """
    Initialize a context with module-specific parameters.

    Parameters
    -----------

    user_id: str
        ID of the user from the update instance.

    """
    ctx = Context(id=user_id)
    ctx.framework_states.update({"ALICE_CONNECTOR": {"keep_flag": True, "request": None}})
    assert "ALICE_CONNECTOR" in ctx.framework_states
    return ctx
