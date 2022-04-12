# -*- coding: utf-8 -*-

__author__ = "Daniil Ignatiev"
__email__ = "ruthenian8@gmail.com"
__version__ = "0.0.1"

from .conditions import cnd
from .adapters import alice_adapter
from .utils import get_initial_context, get_user_id, set_state

__all__ = ["cnd"]
