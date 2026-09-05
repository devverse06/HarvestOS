from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Dict, List, Optional
from datetime import datetime
import re

# --- User Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError('Full name must be between 2 and 100 characters')
        if re.search(r'<[^>]*>', v):
            raise ValueError('Name cannot contain HTML tags')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('Password must be at least 10 characters')
        return v

class RoleUpdate(BaseModel):
    role: str

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {'Admin', 'Operations', 'Farmer', 'Buyer', 'Exporter'}
        if v not in allowed:
            raise ValueError(f'Role must be one of: {", ".join(sorted(allowed))}')
        return v

# --- Farm Schemas ---
class FarmBase(BaseModel):
    name: str
    owner: str
    location: str
    crop_type: str
    area_acres: float = Field(gt=0)
    expected_yield_tons: float = Field(gt=0)
    status: str = "Growing"

class FarmCreate(FarmBase):
    id: str

class Farm(FarmBase):
    id: str
    class Config:
        from_attributes = True

# --- HarvestLot Schemas ---
class HarvestLotBase(BaseModel):
    farm_id: str
    weight_tons: float = Field(gt=0)
    quality_grade: Optional[str] = None
    status: str = "Intake"

class HarvestLotCreate(HarvestLotBase):
    id: str

class HarvestLot(HarvestLotBase):
    id: str
    logged_at: datetime
    class Config:
        from_attributes = True

# --- Buyer Schemas ---
class BuyerBase(BaseModel):
    company_name: str
    country: str
    contact_name: str
    email: EmailStr
    ltv: str
    status: str = "Active"

class BuyerCreate(BuyerBase):
    id: str

class Buyer(BuyerBase):
    id: str
    class Config:
        from_attributes = True

# --- Shipment Schemas ---
class ShipmentBase(BaseModel):
    buyer_id: Optional[str] = None
    order_id: Optional[str] = None
    container_number: str
    status: str = "Planned"
    internal_temp: Optional[float] = None
    eta: Optional[datetime] = None

class ShipmentCreate(ShipmentBase):
    id: str

class Shipment(ShipmentBase):
    id: str
    class Config:
        from_attributes = True


class QualityInspectionCreate(BaseModel):
    id: str
    lot_id: str
    grade: str
    passed: bool
    notes: Optional[str] = None


class QualityInspection(QualityInspectionCreate):
    inspector_id: Optional[str] = None
    inspected_at: datetime

    class Config:
        from_attributes = True


class WarehouseCreate(BaseModel):
    id: str
    name: str
    location: str
    capacity_tons: float = Field(gt=0)
    status: str = "Active"


class Warehouse(WarehouseCreate):
    class Config:
        from_attributes = True


class InventoryBatchCreate(BaseModel):
    id: str
    lot_id: str
    warehouse_id: str
    quantity_tons: float = Field(gt=0)
    status: str = "Available"


class InventoryBatch(InventoryBatchCreate):
    reserved_tons: float
    received_at: datetime
    available_tons: float

    class Config:
        from_attributes = True


class OrderLineCreate(BaseModel):
    inventory_batch_id: str
    quantity_tons: float = Field(gt=0)


class OrderLine(OrderLineCreate):
    id: str

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    id: str
    buyer_id: str
    lines: List[OrderLineCreate] = Field(min_length=1)


class Order(BaseModel):
    id: str
    buyer_id: str
    status: str
    ordered_at: datetime
    lines: List[OrderLine]

    class Config:
        from_attributes = True


class ShipmentCreateWithOrder(BaseModel):
    id: str
    order_id: str
    container_number: str
    eta: Optional[datetime] = None


class ShipmentEvent(BaseModel):
    id: str
    shipment_id: str
    status: str
    location: Optional[str] = None
    notes: Optional[str] = None
    event_at: datetime

    class Config:
        from_attributes = True


class TraceabilityResponse(BaseModel):
    farm: Farm
    harvest_lot: HarvestLot
    quality_inspections: List[QualityInspection]
    inventory_batches: List[InventoryBatch]
    orders: List[Order]
    shipments: List[Shipment]


class AnalyticsSummary(BaseModel):
    procurement_volume_tons: float
    inventory_available_tons: float
    inventory_reserved_tons: float
    orders_by_status: Dict[str, int]
    shipments_by_status: Dict[str, int]
    warehouse_utilization: List[dict]
