from functools import lru_cache

import pymorphy3


class RussianLemmatizer:
    def __init__(self) -> None:
        self._morph = pymorphy3.MorphAnalyzer()

    @lru_cache(maxsize=200_000)
    def normalize(self, word: str) -> str:
        parsed = self._morph.parse(word)
        if not parsed:
            return word
        return parsed[0].normal_form
