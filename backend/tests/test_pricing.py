from decimal import Decimal
from fastapi.testclient import TestClient
from app.database import SessionLocal
from app.main import app
from app.schemas import ConfigurationInput
from app.services.pricing import calculate_price, rounded
from app.models import CableVariant, ComponentPrice
from sqlalchemy import select
from scripts.seed import seed

def test_critical_rounding():
    assert rounded(Decimal("0.5153"))==Decimal("0.52")
    assert rounded(Decimal("0.2264"))==Decimal("0.23")
    assert rounded(Decimal("0.7040"))==Decimal("0.70")
def test_explicit_duplex_connector_quantities():
    c=ConfigurationInput(fiber_type="OM3",construction="2x3.0",jacket="LSZH",color="аква",connector_a="LC",polish_a="PC",connector_b="SC",polish_b="PC",length=Decimal("15"))
    with SessionLocal() as db: _,lines=calculate_price(c,db)
    assert [x.qty for x in lines if x.unit=="pcs"]==[Decimal(2),Decimal(2)]
def test_api_calculate():
    response=TestClient(app).post("/api/config/calculate",json={"fiber_type":"OM3","construction":"2x2.0","jacket":"LSZH","color":"аква","connector_a":"LC","polish_a":"PC","connector_b":"LC","polish_b":"PC","length":"1.2"})
    assert response.status_code==200 and response.json()["valid"] and response.json()["breakdown"]
    assert response.json()["price"]["value"].count(".")==1 and len(response.json()["price"]["value"].split(".")[1])==2
def test_single_file_interface_is_served():
    response=TestClient(app).get("/")
    assert response.status_code==200 and "TELCORD" in response.text and "<select" not in response.text
def test_full_black_has_explicit_nullable_prices():
    response=TestClient(app).post("/api/config/calculate",json={"fiber_type":"OM3","construction":"2x2.0","jacket":"LSZH","color":"аква","connector_a":"LC","polish_a":"PC","connector_b":"LC","polish_b":"PC","length":"1.2","execution":"full_black"})
    assert response.status_code==422 and "Цена компонента не задана" in response.json()["errors"][0]
def test_prices_are_imported_from_current_workbook():
    expected={"SX-SM-G657A1-20-LSZH-WH":Decimal("0.0880"),"DX-OM1-2X20-LSZH-GY":Decimal("0.2263"),"DX-OM2-2X20-LSZH-OR":Decimal("0.2090"),"DX-OM3-2X20-LSZH-AQ":Decimal("0.2332"),"DX-OM4-2X20-LSZH-MA":Decimal("0.4182"),"DX-OM5-2X20-LSZH-LG":Decimal("0.7040")}
    with SessionLocal() as db:
        for key,value in expected.items():
            row=db.scalar(select(CableVariant).where(CableVariant.key==key))
            assert row and Decimal(row.raw_price)==value and "telcord_cables_new.xlsx" in row.source
def test_excel_holder_and_corrugation_prices():
    with SessionLocal() as db:
        values={(x.component_type,x.component_code):Decimal(x.raw_price) for x in db.scalars(select(ComponentPrice).where(ComponentPrice.raw_price.is_not(None)))}
    assert values["holder","LC"]==Decimal("0.1107")
    assert values["holder","SC"]==Decimal("0.0221")
    assert values["corrugation","G16-PVC-GY"]==Decimal("0.5560")
    assert values["corrugation","G16-PVC-BK"]==Decimal("0.6111")

def test_seeded_price_is_visible_without_app_restart():
    client = TestClient(app)
    payload = {
        "fiber_type": "OM4", "construction": "2x2.0", "jacket": "LSZH", "color": "маджента",
        "connector_a": "LC", "polish_a": "PC",
        "connector_b": "LC", "polish_b": "PC", "length": "1",
    }
    with SessionLocal() as db:
        cable = db.scalar(select(CableVariant).where(CableVariant.key == "DX-OM4-2X20-LSZH-MA"))
        cable.raw_price = Decimal("9.9999")
        db.commit()
    before = client.post("/api/config/calculate", json=payload).json()
    assert before["breakdown"][0]["raw_price"] == "9.9999"

    seed()

    after = client.post("/api/config/calculate", json=payload).json()
    assert after["breakdown"][0]["raw_price"] == "0.4182"

def test_variant_without_price_is_absent_from_available_options():
    client = TestClient(app)
    options = client.post("/api/config/available-options", json={}).json()
    assert all(item["key"] != "DX-OM2-2X18-LSZH-OR" for item in options["cable_variants"])

def test_unavailable_variant_disappears_from_all_options():
    client = TestClient(app)
    key = "SX-SM-G655-30-PVC-YL"
    with SessionLocal() as db:
        variants = list(db.scalars(select(CableVariant).where(CableVariant.fiber_type == "G655")))
        for variant in variants:
            variant.available = False
        db.commit()
    try:
        options = client.post("/api/config/available-options", json={}).json()
        assert "G655" not in options["fiber_types"]
        assert all(item["key"] != key for item in options["cable_variants"])
    finally:
        with SessionLocal() as db:
            variants = list(db.scalars(select(CableVariant).where(CableVariant.fiber_type == "G655")))
            for variant in variants:
                variant.available = True
            db.commit()

def test_options_follow_only_existing_terminal_variants():
    client = TestClient(app)
    options = client.post("/api/config/available-options", json={"fiber_type":"G652D","construction":"DUPLEX FLAT","jacket":"LSZH"}).json()
    assert "DUPLEX FLAT" in options["constructions"]
    assert "LSZH" in options["jackets"]
    assert options["colors"] == ["желтый"]
