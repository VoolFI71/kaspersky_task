from openpyxl import Workbook

from app.domain.models.report_statistics import ReportStatistics


class XlsxReportWriter:
    def write(self, statistics: ReportStatistics, output_path: str) -> None:
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
            per_line_counts = ",".join(
                str(word.line_counts.get(line_index, 0))
                for line_index in range(statistics.total_lines)
            )
            worksheet.append([word.lemma, word.total_count, per_line_counts])

        workbook.save(output_path)
