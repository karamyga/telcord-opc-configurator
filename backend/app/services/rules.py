from decimal import Decimal
from ..catalog import CONSTRUCTIONS, CONNECTORS, CORRUGATIONS, FIBERS, POLISHES
from ..schemas import PartialConfiguration, ValidationResult

MTRJ = {"MTRJ_M", "MTRJ_F"}

def validate_configuration(c: PartialConfiguration) -> ValidationResult:
    e=[]
    f=FIBERS.get(c.fiber_type or ""); cons=CONSTRUCTIONS.get(c.construction or "")
    if not f: e.append("Неизвестный тип волокна")
    if not cons: e.append("Неизвестная конструкция")
    if f and cons and c.construction not in f["constructions"]: e.append("Конструкция недопустима для выбранного волокна")
    if c.construction == "ARM-2x2.0": e.append("ARM-2x2.0 не существует")
    for side in ("a","b"):
        connector=getattr(c,f"connector_{side}"); polish=getattr(c,f"polish_{side}"); holder=getattr(c,f"holder_{side}")
        if connector and connector not in CONNECTORS: e.append(f"Неизвестный разъём стороны {side.upper()}")
        if polish and polish not in POLISHES: e.append(f"Неизвестная полировка стороны {side.upper()}")
        if f and polish and ((f["multimode"] and polish != "PC") or (not f["multimode"] and polish not in {"UPC","APC"})): e.append(f"Недопустимая полировка стороны {side.upper()}")
        if holder and connector not in {"LC","SC"}: e.append(f"Holder стороны {side.upper()} разрешён только для LC/SC")
        if holder and cons and not cons["duplex"]: e.append(f"Holder стороны {side.upper()} недоступен для simplex-конструкции")
        if connector in MTRJ and cons and not cons["duplex"]: e.append("MTRJ требует duplex-конструкцию")
    if c.corrugation and c.corrugation not in CORRUGATIONS: e.append("Неизвестная гофра")
    if not c.corrugation and (c.lead_a is not None or c.lead_b is not None): e.append("Выводы доступны только при наличии гофры")
    if c.corrugation:
        a=c.lead_a or Decimal("0"); b=c.lead_b or Decimal("0")
        for label,v in (("A",a),("B",b)):
            if v < Decimal("0.1") or v > Decimal("5.0") or v % Decimal("0.1") != 0: e.append(f"Вывод {label}: диапазон 0.1–5.0 м, шаг 0.1 м")
        if c.length is not None and a+b >= c.length: e.append("Сумма выводов должна быть меньше полной длины")
    if c.execution not in {"standard","full_black"}: e.append("Неизвестное исполнение")
    return ValidationResult(valid=not e, errors=e)

def get_available_options(c: PartialConfiguration) -> dict:
    f=FIBERS.get(c.fiber_type or "")
    constructions=f["constructions"] if f else list(CONSTRUCTIONS)
    if c.connector_a in MTRJ or c.connector_b in MTRJ: constructions=[x for x in constructions if CONSTRUCTIONS[x]["duplex"]]
    polishes=["PC"] if f and f["multimode"] else (["UPC","APC"] if f else list(POLISHES))
    return {"fiber_types":list(FIBERS),"constructions":constructions,"connectors":list(CONNECTORS),"polishes":polishes,"holders":[False,True],"corrugations":[None,*CORRUGATIONS],"executions":["standard","full_black"]}
