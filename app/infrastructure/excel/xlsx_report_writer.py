from openpyxl import Workbook

from app.domain.models.report_statistics import ReportStatistics


class ExcelLimitExceeded(Exception):
    pass


class XlsxReportWriter:
    def write(
        self,
        statistics: ReportStatistics,
        output_path: str,
        *,
        excel_max_cell_chars: int = 32_767,
    ) -> None:
        workbook = Workbook(write_only=True)
        worksheet = workbook.create_sheet(title="report")
        worksheet.append(
            [
                "словоформа",
                "кол-во во всём документе",
                "кол-во в каждой из строк",
            ]
        )

        for lemma in sorted(statistics.words):
            word = statistics.words[lemma]
            parts: list[str] = []
            parts_append = parts.append
            for line_index in range(statistics.total_lines):
                parts_append(str(word.line_counts.get(line_index, 0)))

            per_line_counts = ",".join(parts)
            if len(per_line_counts) > excel_max_cell_chars:
                raise ExcelLimitExceeded(
                    "Сформированная строка 'кол-во в каждой из строк' не помещается в ячейку Excel "
                    f"(лимит {excel_max_cell_chars} символов). "
                    "Сократите число строк входного файла."
                )
            worksheet.append([word.lemma, word.total_count, per_line_counts])

        workbook.save(output_path)
