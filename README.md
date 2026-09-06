# TELCORD Configurator

Конфигуратор оптических патч-кордов. FastAPI обслуживает API и актуальный
одностраничный интерфейс из `backend/app/static/index.html`. Nginx используется
только как reverse proxy.

## Данные

Единственный рабочий каталог данных — `./data`:

- `data/telcord_cables_73.xlsx` — лист «Кабели» с конечными физическими вариантами, постоянными `key` и `available`;
- `data/telcord_prices_full.xlsx` — справочник цен разъёмов, holders и гофры;
- `data/telcord.db` — рабочая SQLite-база, создаваемая seed-командой.

Excel читается только при импорте. Каждый пользовательский расчёт читает
актуальные цены непосредственно из SQLite.

## Запуск через Docker

Первый запуск:

```powershell
docker compose up -d --build
docker compose exec backend python -m scripts.seed
```

Интерфейс: `http://localhost:8080`.

Повторная сборка после изменения кода:

```powershell
docker compose up -d --build
```

## Обновление цен

1. Заменить `data/telcord_cables_73.xlsx` новым файлом с листом «Кабели» того же формата.
2. Выполнить импорт без пересборки и перезапуска контейнеров:

```powershell
docker compose exec backend python -m scripts.seed
```

Backend увидит новые записи SQLite при следующем запросе расчёта.

Импорт произвольного файла, доступного внутри контейнера:

```powershell
docker compose exec backend python -m scripts.seed --excel /app/data/telcord_cables_73.xlsx
```

## Управление сервисами

```powershell
# Логи всех сервисов
docker compose logs -f

# Только backend
docker compose logs -f backend

# Перезапуск
docker compose restart

# Перезапуск одного сервиса
docker compose restart backend

# Остановка
docker compose down
```

## Локальный запуск без Docker

```powershell
cd backend
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m scripts.seed
python -m pytest -q
python -m uvicorn app.main:app --reload
```

Интерфейс: `http://localhost:8000`.
