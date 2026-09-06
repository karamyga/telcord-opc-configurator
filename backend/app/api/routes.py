from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from decimal import Decimal, ROUND_HALF_UP
from ..database import SessionLocal
from ..models import AppSetting, CableVariant, ComponentPrice
from ..schemas import ConfigurationInput, PartialConfiguration
from ..services.generators import generate_name, generate_sku
from ..services.pricing import calculate_price
from ..services.rules import get_available_options, validate_configuration
from ..services.cable_variants import get_cable_options, resolve_cable_variant

router=APIRouter(prefix="/api")
def get_db():
    with SessionLocal() as db: yield db

@router.get("/config/options")
def options(db: Session=Depends(get_db)):
    configuration = PartialConfiguration()
    result = get_available_options(configuration)
    result.update(get_cable_options(db, configuration))
    return result
@router.post("/config/available-options")
def available(c: PartialConfiguration, db: Session=Depends(get_db)):
    result = get_available_options(c)
    result.update(get_cable_options(db, c))
    return result
@router.post("/config/validate")
def validate(c: PartialConfiguration, db: Session=Depends(get_db)):
    validation = validate_configuration(c)
    if validation.valid and c.fiber_type and c.construction:
        try: resolve_cable_variant(db, c)
        except ValueError as exc: return {"valid": False, "errors": [str(exc)]}
    return validation
@router.post("/config/calculate")
def calculate(c: ConfigurationInput, db: Session=Depends(get_db)):
    validation=validate_configuration(c)
    if not validation.valid: return {"valid":False,"errors":validation.errors,"sku":None,"name":None,"price":None,"breakdown":[]}
    try: value,breakdown=calculate_price(c,db)
    except ValueError as exc: return JSONResponse(status_code=422,content={"valid":False,"errors":[str(exc)]})
    display_value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"valid":True,"sku":generate_sku(c),"name":generate_name(c),"price":{"currency":"RUB","value":format(display_value, ".2f")},"breakdown":[x.model_dump(mode="json") for x in breakdown]}
@router.get("/prices")
def prices(db: Session=Depends(get_db)):
    result = [{"type":x.component_type,"code":x.component_code,"description":x.description,"raw_price":str(x.raw_price) if x.raw_price is not None else None,"currency":x.currency,"source":x.source} for x in db.scalars(select(ComponentPrice))]
    result.extend({"type":"cable","code":x.key,"description":f"{x.fiber_name} {x.construction} {x.jacket or ''} {x.color or ''}".strip(),"raw_price":str(x.raw_price) if x.raw_price is not None else None,"currency":x.currency,"source":x.source,"available":x.available} for x in db.scalars(select(CableVariant)))
    return result

@router.get("/settings/public")
def public_settings(db: Session=Depends(get_db)):
    settings = {item.key: item.value for item in db.scalars(select(AppSetting))}
    production_keys = (
        "production_status", "production_days_min", "production_days_max",
        "production_title", "production_message",
    )
    production = None
    if all(settings.get(key) for key in production_keys):
        production = {
            "status": settings["production_status"],
            "days_min": int(settings["production_days_min"]),
            "days_max": int(settings["production_days_max"]),
            "title": settings["production_title"],
            "message": settings["production_message"],
        }
    return {
        "exchange_rate_usd_rub": settings.get("exchange_rate_usd_rub"),
        "production": production,
    }
