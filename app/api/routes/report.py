from pathlib import Path

from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.application.services.report_export_service import ReportExportService
from app.core.settings import Settings, get_settings

router = APIRouter(prefix="/public/report")


def get_report_export_service(
    settings: Settings = Depends(get_settings),
) -> ReportExportService:
    return ReportExportService(settings=settings)


@router.post("/export")
async def export_report(
    request: Request,
    file: UploadFile = File(...),
    service: ReportExportService = Depends(get_report_export_service),
):
    generated_report = await service.export(
        upload_file=file,
        process_pool=request.app.state.process_pool,
        semaphore=request.app.state.export_semaphore,
    )

    return FileResponse(
        path=generated_report.output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=generated_report.download_name,
        background=BackgroundTask(
            _cleanup_files,
            generated_report.output_path,
            generated_report.input_path,
        ),
    )


def _cleanup_files(*paths: str) -> None:
    for path in paths:
        Path(path).unlink(missing_ok=True)
