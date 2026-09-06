from decimal import Decimal
import pytest
from app.schemas import ConfigurationInput, PartialConfiguration
from app.services.generators import generate_name, generate_sku
from app.services.rules import validate_configuration

def cfg(**kw):
    base=dict(fiber_type="OM3",construction="2x2.0",connector_a="LC",polish_a="PC",holder_a=True,connector_b="LC",polish_b="PC",holder_b=True,length=Decimal("1.2"))
    base.update(kw); return ConfigurationInput(**base)

def test_sku_and_holder(): assert generate_sku(cfg())=="TELCORD ШОС-2x2.0-2LC/PC(dx)-2LC/PC(dx)-MM503-1.2м-LSZH-AQ"
def test_name(): assert generate_name(cfg())=="Шнур оптический duplex (ШОС), LC/PC duplex - LC/PC duplex, MM50(OM3), 2.0мм, LSZH, 1.2м"
def test_name_includes_selected_color_once():
    name = generate_name(cfg(color="аква"))
    assert name == "Шнур оптический duplex (ШОС), LC/PC duplex - LC/PC duplex, MM50(OM3), 2.0мм, LSZH, цвет аква, 1.2м"
    assert name.count("цвет аква") == 1
def test_simplex():
    c=cfg(fiber_type="G657A1",construction="2.0",polish_a="UPC",polish_b="UPC",holder_a=False,holder_b=False)
    assert "-LC/U-LC/U-SM(A1)-" in generate_sku(c) and validate_configuration(c).valid
def test_duplex_not_encoded_as_holder(): assert "-2LC/PC-" in generate_sku(cfg(holder_a=False))
def test_holder_is_invalid_for_simplex():
    result=validate_configuration(cfg(fiber_type="G657A1",construction="2.0",polish_a="UPC",polish_b="UPC",holder_a=True,holder_b=False))
    assert not result.valid
    assert any("simplex" in error.lower() and "holder" in error.lower() for error in result.errors)
def test_holder_and_lead_order():
    c=cfg(corrugation="G16-PVC-GY",lead_a=Decimal("0.1"),lead_b=Decimal("0.2"))
    assert "2LC/PC(dx)(0.1)" in generate_sku(c)
def test_arm():
    c=cfg(construction="ARM-2x3.0",length=Decimal("10"),holder_a=False,holder_b=False)
    assert "ШОС-ARM-2x3.0" in generate_sku(c) and "армированный duplex" in generate_name(c)
@pytest.mark.parametrize("fiber",["G657A1","G657A2","OM1","OM2","OM3","OM4","OM5"])
def test_fibers(fiber):
    polish="PC" if fiber.startswith("OM") else "UPC"
    assert validate_configuration(cfg(fiber_type=fiber,polish_a=polish,polish_b=polish)).valid
@pytest.mark.parametrize("fiber", ["OM1", "OM2", "OM3", "OM4"])
def test_multimode_simplex_valid_when_catalogued(fiber):
    assert validate_configuration(cfg(fiber_type=fiber, construction="2.0", holder_a=False, holder_b=False)).valid

def test_om5_simplex_invalid_when_not_catalogued():
    assert not validate_configuration(cfg(fiber_type="OM5", construction="2.0")).valid
def test_arm_2x2_invalid(): assert not validate_configuration(PartialConfiguration(fiber_type="OM3",construction="ARM-2x2.0")).valid
def test_lead_without_corrugation_invalid(): assert not validate_configuration(cfg(lead_a=Decimal("0.1"))).valid
def test_leads_must_be_shorter_than_total(): assert not validate_configuration(cfg(length=Decimal("1"),corrugation="G16-PVC-GY",lead_a=Decimal("0.5"),lead_b=Decimal("0.5"))).valid
def test_mtrj_requires_duplex(): assert not validate_configuration(cfg(fiber_type="G657A1",construction="2.0",connector_a="MTRJ_M",polish_a="UPC",polish_b="UPC")).valid
