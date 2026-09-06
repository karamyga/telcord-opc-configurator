from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class CodeNameMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255))

class FiberType(CodeNameMixin, Base):
    __tablename__ = "fiber_types"
    sku_code: Mapped[str] = mapped_column(String(32))
    color_code: Mapped[str] = mapped_column(String(8))
    is_multimode: Mapped[bool] = mapped_column(Boolean)

class CableConstruction(CodeNameMixin, Base):
    __tablename__ = "cable_constructions"
    duplex: Mapped[bool] = mapped_column(Boolean)
    armored: Mapped[bool] = mapped_column(Boolean)
    diameter: Mapped[str] = mapped_column(String(8))

class ConnectorType(CodeNameMixin, Base):
    __tablename__ = "connector_types"
    physical_qty: Mapped[int] = mapped_column(default=1)
    always_duplex: Mapped[bool] = mapped_column(default=False)

class PolishType(CodeNameMixin, Base):
    __tablename__ = "polish_types"
    sku_suffix: Mapped[str] = mapped_column(String(8))

class HolderType(CodeNameMixin, Base):
    __tablename__ = "holder_types"

class CorrugationType(CodeNameMixin, Base):
    __tablename__ = "corrugation_types"
    color_code: Mapped[str] = mapped_column(String(8))

class ProductExecution(CodeNameMixin, Base):
    __tablename__ = "product_executions"

class ComponentPrice(Base):
    __tablename__ = "component_prices"
    __table_args__ = (UniqueConstraint("component_type", "component_code", "currency"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    component_type: Mapped[str] = mapped_column(String(32))
    component_code: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(255))
    raw_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    source: Mapped[str | None] = mapped_column(Text, nullable=True)

class CableVariant(Base):
    __tablename__ = "cable_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    product_type: Mapped[str] = mapped_column(String(16))
    fiber_type: Mapped[str] = mapped_column(String(32), index=True)
    fiber_name: Mapped[str] = mapped_column(String(64))
    construction: Mapped[str] = mapped_column(String(32), index=True)
    jacket: Mapped[str | None] = mapped_column(String(16), nullable=True)
    color: Mapped[str | None] = mapped_column(String(32), nullable=True)
    color_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    raw_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    available: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id: Mapped[int] = mapped_column(primary_key=True)
    pair: Mapped[str] = mapped_column(String(7), unique=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    effective_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

class AppSetting(Base):
    __tablename__ = "app_settings"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

class Configuration(Base):
    __tablename__ = "configurations"
    id: Mapped[int] = mapped_column(primary_key=True)
    payload: Mapped[str] = mapped_column(Text)
    sku: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
