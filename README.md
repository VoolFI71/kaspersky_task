# Тестовое задание

Сервис реализует endpoint `POST /public/report/export`.

Endpoint принимает текстовый файл `.txt`, строит статистику и возвращает `xlsx`
## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload
```

## Пример запроса

```bash
curl -X POST "http://127.0.0.1:8000/public/report/export" ^
  -F "file=@sample.txt"
```
