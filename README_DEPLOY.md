# Развёртывание TELCORD Configurator

Пакет предназначен для полной чистой установки текущей версии на Linux-сервере через Docker Compose.

> **LOCAL DOCKER BUILD: NOT VERIFIED**
>
> На компьютере подготовки пакета Docker отсутствует. Код проверен unit-тестами, а Compose, пути и Docker-конфигурация — статически. Первая реальная Docker-сборка и проверка контейнеров должны быть выполнены на Linux-сервере по инструкции ниже.

## Состав и схема работы

- `frontend` — nginx, раздаёт production-интерфейс на порту контейнера `80`.
- `backend` — FastAPI/Uvicorn на внутреннем порту `8000`.
- Запросы браузера к `/api/` проксируются nginx в `http://backend:8000`.
- Внешний порт по умолчанию: `8080`.
- SQLite и исходные XLSX находятся в каталоге `data/`, подключённом в backend как `/app/data`.
- Если `data/telcord.db` отсутствует, backend один раз создаст БД из включённых XLSX-файлов.
- Пользовательская спецификация хранится только в `localStorage` браузера.

## 1. Удалить только старые контейнеры TELCORD

Сначала убедитесь, что старые контейнеры остановлены:

```bash
docker ps -a --filter name=telcord-configurator
```

Удалите только два известных старых контейнера:

```bash
docker rm telcord-configurator-frontend-1 telcord-configurator-backend-1
```

Если один из них уже удалён, Docker сообщит об этом — остальные проекты это не затрагивает.

## 2. Необязательно удалить только старые образы TELCORD

Посмотрите только образы TELCORD:

```bash
docker image ls --filter reference='telcord-configurator-*'
```

При необходимости удалите только образы с точными именами из показанного списка, например:

```bash
docker image rm telcord-configurator-frontend telcord-configurator-backend
```

Не используйте глобальную очистку Docker. Проекты `pricetrunk` и `dkc_magadel`, их контейнеры, образы и volumes трогать нельзя.

## 3. Распаковать новый проект

В каталоге, куда загружен архив:

```bash
unzip telcord-configurator-deploy.zip
cd telcord-configurator
```

При необходимости скопируйте пример настроек:

```bash
cp .env.example .env
```

По умолчанию интерфейс будет доступен на порту `8080`. Для другого порта измените только `TELCORD_HTTP_PORT` в `.env`.

## 4. Проверить и собрать с нуля

```bash
docker compose config
docker compose build --no-cache --pull
docker compose up -d --force-recreate
```

Команда `build --no-cache --pull` заново собирает только сервисы этого Compose-проекта и получает актуальные базовые образы. `--force-recreate` пересоздаёт только контейнеры TELCORD.

## 5. Проверить запуск

```bash
docker compose ps
docker compose logs --tail=100
```

Оба сервиса должны перейти в состояние `healthy`.

Проверка frontend и API непосредственно на сервере:

```bash
curl -f http://127.0.0.1:8080/
curl -f http://127.0.0.1:8080/healthz
curl -f http://127.0.0.1:8080/api/config/options
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
```

Затем откройте в браузере:

```text
http://IP_СЕРВЕРА:8080/
```

Если используется firewall, разрешите входящие подключения только к нужному порту `8080` согласно правилам вашего сервера.

## Управление только TELCORD

Остановить текущий stack без удаления данных:

```bash
docker compose down
```

Запустить снова:

```bash
docker compose up -d
```

Не добавляйте `-v` к `docker compose down`: данные SQLite находятся в подключённом каталоге `data/`. Не выполняйте `docker system prune`, `docker system prune -a` или `docker volume prune` на сервере с другими проектами.

## Rollback при неудачной первой сборке или запуске

До распаковки рекомендуется не удалять предыдущую папку проекта, а переименовать её, например в `telcord-configurator-previous`. Старые контейнеры могут быть удалены: предыдущая версия восстанавливается сборкой из сохранённой папки.

Если новая версия не собралась или не запустилась:

```bash
cd /ПУТЬ/К/НОВОЙ/telcord-configurator
docker compose down

cd /ПУТЬ/К/telcord-configurator-previous
docker compose config
docker compose build
docker compose up -d --force-recreate
docker compose ps
docker compose logs --tail=100
```

`docker compose down` выполняйте из папки новой версии и без `-v`. Он затронет только Compose-проект TELCORD. Не удаляйте каталог `data` предыдущей версии до успешной проверки новой установки.

Для проверки восстановленной версии:

```bash
curl -f http://127.0.0.1:8080/
curl -f http://127.0.0.1:8080/api/config/options
```

Не используйте `docker system prune`, `docker volume prune`, `docker image prune -a` и любые другие глобальные команды очистки: они могут затронуть `pricetrunk`, `dkc_magadel` и другие проекты сервера.
