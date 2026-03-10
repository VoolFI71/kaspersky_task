import asyncio
from concurrent.futures import Executor
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

import aiofiles

from fastapi import HTTPException, UploadFile, status

from app.core.settings import Settings
from app.domain.services.text_statistics import WordStatsBuilder
from app.infrastructure.excel.xlsx_report_writer import XlsxReportWriter
from app.infrastructure.morphology.russian_lemmatizer import RussianLemmatizer


@dataclass(slots=True)
class GeneratedReport:
    output_path: str
    download_name: str
    input_path: str


class ReportExportService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def export(
        self,
        upload_file: UploadFile,
        process_pool: Executor,
        semaphore: asyncio.Semaphore,
    ) -> GeneratedReport:
        self._validate_upload(upload_file)
        input_path = await self._persist_upload(upload_file)
        output_path = self._create_temp_path(suffix=".xlsx")
        download_name = self._build_download_name(upload_file.filename)

        try:
            await asyncio.wait_for(
                semaphore.acquire(),
                timeout=self._settings.semaphore_acquire_timeout_seconds,
            )
        except TimeoutError as error:
            Path(input_path).unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    "Сервис обрабатывает слишком много тяжелых файлов. "
                    "Повторите запрос позже."
                ),
            ) from error

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(process_pool, build_report_file, input_path, output_path)
        except Exception:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
            raise
        finally:
            semaphore.release()

        return GeneratedReport(
            output_path=output_path,
            download_name=download_name,
            input_path=input_path,
        )

    async def _persist_upload(self, upload_file: UploadFile) -> str:
        input_path = self._create_temp_path(suffix=".txt")

        try:
            async with aiofiles.open(input_path, "wb") as target:
                await self._copy_upload(upload_file, target)
        finally:
            await upload_file.close()

        return input_path

    async def _copy_upload(self, upload_file: UploadFile, target) -> None:
        while chunk := await upload_file.read(self._settings.upload_chunk_size):
            await target.write(chunk)

    @staticmethod
    def _validate_upload(upload_file: UploadFile) -> None:
        filename = upload_file.filename or ""
        if not filename.lower().endswith(".txt"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ожидается текстовый файл в формате .txt.",
            )

    def _build_download_name(self, filename: str | None) -> str:
        source_name = Path(filename or "report.txt").stem or "report"
        return f"{source_name}_report.xlsx"

    @staticmethod
    def _create_temp_path(suffix: str) -> str:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            return temp_file.name


def build_report_file(input_path: str, output_path: str) -> None:
    builder = WordStatsBuilder(lemmatizer=RussianLemmatizer())
    statistics = builder.collect(input_path)
    writer = XlsxReportWriter()
    writer.write(statistics=statistics, output_path=output_path)
