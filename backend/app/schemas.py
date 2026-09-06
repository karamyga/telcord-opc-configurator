from decimal import Decimal
from pydantic import BaseModel, Field, field_serializer

class PartialConfiguration(BaseModel):
    fiber_type: str | None = None
    construction: str | None = None
    jacket: str | None = None
    color: str | None = None
    connector_a: str | None = None
    polish_a: str | None = None
    holder_a: bool = False
    connector_b: str | None = None
    polish_b: str | None = None
    holder_b: bool = False
    length: Decimal | None = None
    corrugation: str | None = None
    lead_a: Decimal | None = None
    lead_b: Decimal | None = None
    execution: str = "standard"

class ConfigurationInput(PartialConfiguration):
    fiber_type: str
    construction: str
    connector_a: str
    polish_a: str
    connector_b: str
    polish_b: str
    length: Decimal = Field(gt=0)

class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []

class PriceLine(BaseModel):
    component: str
    qty: Decimal
    unit: str | None = None
    raw_price: Decimal
    calculation_price: Decimal
    subtotal: Decimal
    @field_serializer("qty", "raw_price", "calculation_price", "subtotal")
    def decimal_string(self, value: Decimal) -> str:
        return str(value)
