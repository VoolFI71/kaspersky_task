from pathlib import Path

from app.domain.services.text_statistics import WordStatsBuilder


class FakeLemmatizer:
    def __init__(self) -> None:
        self._mapping = {
            "житель": "житель",
            "жителем": "житель",
            "жители": "житель",
            "дом": "дом",
            "дома": "дом",
            "будет": "быть",
        }

    def normalize(self, word: str) -> str:
        return self._mapping.get(word, word)


def test_builder_counts_total_and_per_line(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text(
        "житель дом\n"
        "жителем дома дом будет\n",
        encoding="utf-8",
    )

    builder = WordStatsBuilder(lemmatizer=FakeLemmatizer())
    statistics = builder.collect(str(file_path))

    assert statistics.total_lines == 2

    assert statistics.words["житель"].total_count == 2
    assert statistics.words["житель"].line_counts == {0: 1, 1: 1}

    assert statistics.words["дом"].total_count == 3
    assert statistics.words["дом"].line_counts == {0: 1, 1: 2}

    assert statistics.words["быть"].total_count == 1
    assert statistics.words["быть"].line_counts == {1: 1}


def test_builder_ignores_digits_and_punctuation(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("дом, дом! 123 + 456\n", encoding="utf-8")

    builder = WordStatsBuilder(lemmatizer=FakeLemmatizer())
    statistics = builder.collect(str(file_path))

    assert statistics.total_lines == 1
    assert statistics.words["дом"].total_count == 2
