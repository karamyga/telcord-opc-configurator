import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.database import SessionLocal
from app.main import app
from app.models import AppSetting

client = TestClient(app)

def set_setting(key: str, value: str) -> None:
    with SessionLocal() as db:
        setting = db.scalar(select(AppSetting).where(AppSetting.key == key))
        if setting:
            setting.value = value
        else:
            db.add(AppSetting(key=key, value=value))
        db.commit()

@pytest.mark.parametrize(
    ("status", "days_min", "days_max", "title"),
    [
        ("NORMAL", 2, 3, "Обычная загрузка производства"),
        ("MEDIUM", 10, 14, "Средняя загрузка производства"),
        ("HIGH", 25, 30, "Производство загружено"),
    ],
)
def test_public_production_statuses(status, days_min, days_max, title):
    try:
        set_setting("production_status", status)
        set_setting("production_days_min", str(days_min))
        set_setting("production_days_max", str(days_max))
        set_setting("production_title", title)
        response = client.get("/api/settings/public")
        assert response.status_code == 200
        assert response.json()["production"] == {
            "status": status,
            "days_min": days_min,
            "days_max": days_max,
            "title": title,
            "message": "Ориентировочный срок изготовления при заказе сегодня. Фактический срок зависит от количества.",
        }
    finally:
        set_setting("production_status", "NORMAL")
        set_setting("production_days_min", "2")
        set_setting("production_days_max", "3")
        set_setting("production_title", "Обычная загрузка производства")

def test_public_settings_fallback_when_production_is_missing():
    with SessionLocal() as db:
        saved = db.scalar(select(AppSetting).where(AppSetting.key == "production_message"))
        message = saved.value
        db.execute(delete(AppSetting).where(AppSetting.key == "production_message"))
        db.commit()
    try:
        response = client.get("/api/settings/public")
        assert response.status_code == 200
        assert response.json()["production"] is None
    finally:
        set_setting("production_message", message)

def test_seeded_exchange_rate_is_public():
    assert client.get("/api/settings/public").json()["exchange_rate_usd_rub"] == "90"
