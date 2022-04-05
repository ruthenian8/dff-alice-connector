"""Main module"""
from typing import Callable, Optional, Union, Dict, Any, List, NamedTuple
from functools import lru_cache
from copy import copy

from dialogic.nlu.matchers import BaseMatcher, make_matcher, register_matcher
from dialogic.nlu.basic_nlu import fast_normalize

from df_engine.core import Context, Actor


class MatcherData(NamedTuple):
    matcher: BaseMatcher
    phrases: List[str] = list()
    labels: List[Union[str, int]] = list()


def make_cached_matcher(matcher_type: str, **kwargs) -> BaseMatcher:
    matcher: BaseMatcher = make_matcher(matcher_type, **kwargs)
    matcher.match = lru_cache(maxsize=1)(matcher.match)
    return matcher


class Matchers(object):
    def __init__(self):
        self._matcher_registry: Dict[str, MatcherData] = dict()
        self.condition_counter = 0
        self.initialized = False

    def __deepcopy__(self, *args, **kwargs):
        return copy(self)

    def make_condition(self, matcher_type: str, phrases: str, threshold: Optional[float] = None) -> Callable:
        """"""
        if matcher_type not in self._matcher_registry:
            self._matcher_registry[matcher_type] = MatcherData(matcher=make_cached_matcher(matcher_type))

        self.condition_counter += 1
        index = self.condition_counter

        def condition(ctx: Context, actor: Actor, *args, **kwargs) -> bool:
            if not self.initialized:
                raise Exception("`initialize` method of the parent object should be called first.")

            matcher: BaseMatcher = self._matcher_registry[matcher_type].matcher
            normalized_request = fast_normalize(ctx.last_request)
            index, score = matcher.match(normalized_request)  # get highest prediction from the matcher
            if threshold and score < threshold:
                return False
            return index == condition.index

        condition.index = index
        self._matcher_registry[matcher_type].phrases.extend(phrases)
        self._matcher_registry[matcher_type].labels.extend([index] * len(phrases))

        return condition

    def initialize(self):
        """
        Fit all the matcher algorithms.
        Call this function after you've defined the plot, including all matcher conditions.
        """
        for matcher_data in self._matcher_registry.values():
            matcher_data.matcher.fit(matcher_data.phrases, matcher_data.labels)
        self.initialized = True
