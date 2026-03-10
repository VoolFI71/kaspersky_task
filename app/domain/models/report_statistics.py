from dataclasses import dataclass, field


@dataclass(slots=True)
class WordFrequency:
    lemma: str
    total_count: int = 0
    line_counts: dict[int, int] = field(default_factory=dict)

    def add_occurrence(self, line_index: int, count: int) -> None:
        self.total_count += count
        self.line_counts[line_index] = self.line_counts.get(line_index, 0) + count


@dataclass(slots=True)
class ReportStatistics:
    total_lines: int = 0
    words: dict[str, WordFrequency] = field(default_factory=dict)
