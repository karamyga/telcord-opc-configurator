from decimal import Decimal

from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import CableVariant

def test_full_workbook_imports_only_explicit_cable_rows():
    with SessionLocal() as db:
        variants = list(db.scalars(select(CableVariant)))
    assert len(variants) == 59
    assert len({variant.key for variant in variants}) == 59
    assert all(variant.available for variant in variants)
    assert all(variant.raw_price is not None for variant in variants)

def test_representative_stable_cable_keys():
    expected = {
        "SX-SM-G652D-20-LSZH-YL",
        "SX-SM-G655-30-PVC-YL",
        "SX-SM-G657A1-30-LSZH-BK",
        "DX-OM3-2X20-LSZH-AQ",
        "DX-OM5-2X20-LSZH-LG",
    }
    with SessionLocal() as db:
        keys = set(db.scalars(select(CableVariant.key)))
    assert expected <= keys

def test_missing_price_variant_is_not_imported():
    with SessionLocal() as db:
        variant = db.scalar(select(CableVariant).where(CableVariant.key == "DX-OM2-2X18-LSZH-OR"))
    assert variant is None


def test_import_source_is_final_workbook():
    with SessionLocal() as db:
        sources = set(db.scalars(select(CableVariant.source)))
    assert sources
    assert all("telcord_cables_new.xlsx" in source for source in sources)

def test_known_om4_price_is_preserved():
    with SessionLocal() as db:
        variant = db.scalar(select(CableVariant).where(CableVariant.key == "DX-OM4-2X20-LSZH-MA"))
    assert Decimal(variant.raw_price) == Decimal("0.4182")
    assert variant.currency == "USD"
