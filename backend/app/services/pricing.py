from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..catalog import CONSTRUCTIONS
from ..models import ComponentPrice, ExchangeRate
from ..schemas import ConfigurationInput, PriceLine
from .cable_variants import resolve_cable_variant

def rounded(raw: Decimal) -> Decimal: return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calculate_price(c: ConfigurationInput, db: Session) -> tuple[Decimal,list[PriceLine]]:
    con=CONSTRUCTIONS[c.construction]; entries=[]
    def add(kind,code,label,qty,unit=None):
        row=db.scalar(select(ComponentPrice).where(ComponentPrice.component_type==kind,ComponentPrice.component_code==code))
        if row is None or row.raw_price is None: raise ValueError(f"Цена компонента не задана: {kind}/{code}")
        raw=Decimal(row.raw_price); calc=rounded(raw); entries.append(PriceLine(component=label,qty=qty,unit=unit,raw_price=raw,calculation_price=calc,subtotal=calc*qty))
    variant = resolve_cable_variant(db, c)
    if variant.raw_price is None:
        raise ValueError(f"Цена варианта кабеля не задана: {variant.key}")
    raw = Decimal(variant.raw_price); calc = rounded(raw)
    entries.append(PriceLine(component=variant.key, qty=c.length, unit="m", raw_price=raw, calculation_price=calc, subtotal=calc*c.length))
    suffix=":BK" if c.execution=="full_black" else ""
    cable_count=2 if con["duplex"] else 1
    for side in ("a","b"):
        connector=getattr(c,f"connector_{side}"); polish=getattr(c,f"polish_{side}")
        qty=1 if connector.startswith("MTRJ") else cable_count
        add("connector",f"{connector}:{polish}{suffix}",f"{connector}/{polish}{' black' if suffix else ''}",Decimal(qty),"pcs")
        if getattr(c,f"holder_{side}"): add("holder",connector+suffix,f"{connector}{' black' if suffix else ''} duplex holder",Decimal(1),"pcs")
    if c.corrugation:
        corr_len=c.length-(c.lead_a or Decimal(0))-(c.lead_b or Decimal(0))
        add("corrugation",c.corrugation,c.corrugation,corr_len,"m")
    usd=sum((x.subtotal for x in entries),Decimal(0)); rate=db.scalar(select(ExchangeRate).where(ExchangeRate.pair=="USD/RUB"))
    if not rate: raise ValueError("Курс USD/RUB не задан")
    return usd*Decimal(rate.rate), entries
