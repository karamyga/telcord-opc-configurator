from decimal import Decimal
from ..catalog import COLOR_CODES, CONSTRUCTIONS, FIBERS, POLISHES
from ..schemas import ConfigurationInput

def fmt_decimal(v: Decimal) -> str:
    return format(v.normalize(), "f")

def _side(c, side: str, sku: bool) -> str:
    connector=getattr(c,f"connector_{side}"); polish=getattr(c,f"polish_{side}"); holder=getattr(c,f"holder_{side}"); lead=getattr(c,f"lead_{side}")
    con=CONSTRUCTIONS[c.construction]
    if sku:
        base=("MTRJ(M)" if connector=="MTRJ_M" else "MTRJ(F)" if connector=="MTRJ_F" else (("2" if con["duplex"] else "")+connector))+"/"+POLISHES[polish]["sku"]
        if holder: base += "(dx)"
        if lead is not None: base += f"({fmt_decimal(lead)})"
        return base
    label=("MTRJ Male" if connector=="MTRJ_M" else "MTRJ Female" if connector=="MTRJ_F" else connector)+"/"+POLISHES[polish]["label"]
    return label+(" duplex" if holder else "")

def generate_sku(c: ConfigurationInput) -> str:
    fiber=FIBERS[c.fiber_type]; color="BK" if c.execution=="full_black" else COLOR_CODES.get(c.color, fiber["color"]); jacket=c.jacket or "LSZH"
    parts=["TELCORD ШОС",c.construction,_side(c,"a",True),_side(c,"b",True),fiber["sku"],fmt_decimal(c.length)+"м",jacket,color]
    if c.corrugation: parts.append(c.corrugation)
    return "-".join(parts)

def generate_name(c: ConfigurationInput) -> str:
    con=CONSTRUCTIONS[c.construction]; fiber=FIBERS[c.fiber_type]
    kind="армированный duplex" if con["armored"] else ("duplex" if con["duplex"] else "simplex")
    color=f", цвет {c.color}" if c.color else ""
    return f"Шнур оптический {kind} (ШОС), {_side(c,'a',False)} - {_side(c,'b',False)}, {fiber['name']}, {con['diameter']}мм, {c.jacket or 'LSZH'}{color}, {fmt_decimal(c.length)}м"
