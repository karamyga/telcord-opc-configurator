from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import CableVariant
from ..schemas import PartialConfiguration

def get_available_cable_variants(db: Session) -> list[CableVariant]:
    return list(db.scalars(select(CableVariant).where(CableVariant.available.is_(True)).order_by(CableVariant.id)))

def _unique(values):
    return list(dict.fromkeys(value for value in values if value is not None))

def get_cable_options(db: Session, configuration: PartialConfiguration) -> dict:
    variants = get_available_cable_variants(db)
    if configuration.connector_a in {"MTRJ_M", "MTRJ_F"} or configuration.connector_b in {"MTRJ_M", "MTRJ_F"}:
        variants = [variant for variant in variants if variant.product_type == "DUPLEX"]
    fibers = _unique(v.fiber_type for v in variants)
    fiber = configuration.fiber_type if configuration.fiber_type in fibers else (fibers[0] if fibers else None)
    by_fiber = [v for v in variants if v.fiber_type == fiber]
    constructions = _unique(v.construction for v in by_fiber)
    construction = configuration.construction if configuration.construction in constructions else (constructions[0] if constructions else None)
    by_construction = [v for v in by_fiber if v.construction == construction]
    jackets = _unique(v.jacket for v in by_construction)
    jacket = configuration.jacket if configuration.jacket in jackets else (jackets[0] if jackets else None)
    by_jacket = [v for v in by_construction if v.jacket == jacket]
    colors = _unique(v.color for v in by_jacket)
    return {
        "fiber_types": fibers,
        "constructions": constructions,
        "jackets": jackets,
        "colors": colors,
        "cable_variants": [
            {"key": v.key, "product_type": v.product_type, "fiber_type": v.fiber_type,
             "construction": v.construction, "jacket": v.jacket, "color": v.color,
             "color_code": v.color_code, "has_price": v.raw_price is not None,
             "available": v.available}
            for v in variants
        ],
    }

def resolve_cable_variant(db: Session, configuration: PartialConfiguration) -> CableVariant:
    query = select(CableVariant).where(
        CableVariant.available.is_(True),
        CableVariant.fiber_type == configuration.fiber_type,
        CableVariant.construction == configuration.construction,
    )
    if configuration.jacket is not None:
        query = query.where(CableVariant.jacket == configuration.jacket)
    if configuration.color is not None:
        query = query.where(CableVariant.color == configuration.color)
    variants = list(db.scalars(query))
    if not variants:
        raise ValueError("Выбранный вариант кабеля недоступен")
    if len(variants) > 1:
        raise ValueError("Уточните оболочку и цвет кабеля")
    return variants[0]
