from inspect import signature
from typing import Optional, MutableMapping
from copy import copy

from dialogic.dialog_manager.base import CascadableDialogManager
from dialogic.dialog import Context as DialogicContext
from dialogic.dialog import Response as DialogicResponse
from df_engine.core import Actor, Context

from .utils import to_int_key


RESPONSE_FORMAT = list(signature(DialogicResponse).parameters.keys())


class DFFManager(CascadableDialogManager):
    def __init__(self, actor: Actor, db_connector: Optional[MutableMapping], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_connector = db_connector
        self.actor = actor

    def __deepcopy__(self, *args, **kwargs):
        return copy(self)

    def try_to_respond(self, dialogic_context: DialogicContext) -> DialogicResponse:
        dff_id = to_int_key(dialogic_context.user_id)
        dff_context = self.db_connector.get(dff_id, Context(id=dff_id))

        dff_context.add_request(dialogic_context.message_text)
        new_context = self.actor(dff_context)

        self.db_connector[dff_id] = new_context

        response = new_context.last_response
        if isinstance(response, str):
            return DialogicResponse(text=response, user_object=dialogic_context.user_object).set_text(response)
        elif isinstance(response, dict):
            return DialogicResponse(user_object=dialogic_context.user_object, **response)
