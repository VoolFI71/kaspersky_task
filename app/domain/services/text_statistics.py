import re
from collections import Counter
from typing import Protocol

from app.domain.models.report_statistics import ReportStatistics, WordFrequency


WORD_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


class StatisticsLimitExceeded(Exception):
    pass


class Lemmatizer(Protocol):
    def normalize(self, word: str) -> str:
        ...


class WordStatsBuilder:
    def __init__(self, lemmatizer: Lemmatizer) -> None:
        self._lemmatizer = lemmatizer

    def collect(
        self,
        file_path: str,
        *,
        max_total_lines: int | None = None,
        max_unique_lemmas: int | None = None,
    ) -> ReportStatistics:
        statistics = ReportStatistics()
        encoding = self._detect_encoding(file_path)

        with open(file_path, "r", encoding=encoding, errors="ignore") as source:
            for line_index, line in enumerate(source):
                if max_total_lines is not None and statistics.total_lines >= max_total_lines:
                    raise StatisticsLimitExceeded(
                        f"Слишком много строк для отчёта: > {max_total_lines}. "
                        "Сократите файл или уменьшите число строк."
                    )

                counts_per_line = Counter(self._iter_lemmas(line))
                for lemma, count in counts_per_line.items():
                    if (
                        max_unique_lemmas is not None
                        and lemma not in statistics.words
                        and len(statistics.words) >= max_unique_lemmas
                    ):
                        raise StatisticsLimitExceeded(
                            f"Слишком много уникальных словоформ: > {max_unique_lemmas}. "
                            "Сократите файл или уменьшите словарь."
                        )
                    word_stat = statistics.words.setdefault(lemma, WordFrequency(lemma=lemma))
                    word_stat.add_occurrence(line_index=line_index, count=count)
                statistics.total_lines += 1

        return statistics

    def _iter_lemmas(self, line: str):
        for raw_word in WORD_PATTERN.findall(line.lower()):
            yield self._lemmatizer.normalize(raw_word)

    @staticmethod
    def _detect_encoding(file_path: str) -> str:
        with open(file_path, "rb") as source:
            start = source.read(4)

        if start.startswith(b"\xff\xfe"):
            return "utf-16-le"
        if start.startswith(b"\xfe\xff"):
            return "utf-16-be"
        if start.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"

        return "utf-8"
