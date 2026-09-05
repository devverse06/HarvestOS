from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String, default="Farmer") # Admin, Operations, Farmer, Buyer

class Farm(Base):
    __tablename__ = "farms"

    id = Column(String, primary_key=True, index=True) # e.g., 'FRM-001'
    name = Column(String, index=True)
    owner = Column(String)
    location = Column(String)
    crop_type = Column(String)
    area_acres = Column(Float)
    expected_yield_tons = Column(Float)
    status = Column(String, default="Growing")
    
    # Relationships
    harvest_lots = relationship("HarvestLot", back_populates="farm", cascade="all, delete-orphan")

class HarvestLot(Base):
    __tablename__ = "harvest_lots"

    id = Column(String, primary_key=True, index=True) # e.g., 'LOT-BAN-001'
    farm_id = Column(String, ForeignKey("farms.id", ondelete="RESTRICT"), nullable=False, index=True)
    weight_tons = Column(Float)
    quality_grade = Column(String, nullable=True) # e.g., 'Grade A'
    status = Column(String, default="Intake") # Intake, Quality, Packing, Storage
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("weight_tons > 0", name="ck_harvest_lot_positive_weight"),
        CheckConstraint(
            "status IN ('Intake', 'Quality', 'Packing', 'Storage')",
            name="ck_harvest_lot_status",
        ),
        Index("ix_harvest_lots_status_logged_at", "status", "logged_at"),
    )
    
    # Relationships
    farm = relationship("Farm", back_populates="harvest_lots")
    inspections = relationship("QualityInspection", back_populates="harvest_lot", cascade="all, delete-orphan")
    inventory_batches = relationship("InventoryBatch", back_populates="harvest_lot", cascade="all, delete-orphan")


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    id = Column(String, primary_key=True, index=True)
    lot_id = Column(String, ForeignKey("harvest_lots.id", ondelete="CASCADE"), nullable=False, index=True)
    inspector_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    grade = Column(String, nullable=False)
    passed = Column(Boolean, nullable=False, default=False)
    notes = Column(String, nullable=True)
    inspected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    harvest_lot = relationship("HarvestLot", back_populates="inspections")
    inspector = relationship("User")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    location = Column(String, nullable=False)
    capacity_tons = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="Active")

    __table_args__ = (
        CheckConstraint("capacity_tons > 0", name="ck_warehouse_positive_capacity"),
        CheckConstraint("status IN ('Active', 'Inactive')", name="ck_warehouse_status"),
    )

    inventory_batches = relationship("InventoryBatch", back_populates="warehouse")


class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id = Column(String, primary_key=True, index=True)
    lot_id = Column(String, ForeignKey("harvest_lots.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = Column(String, ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_tons = Column(Float, nullable=False)
    reserved_tons = Column(Float, nullable=False, default=0)
    status = Column(String, nullable=False, default="Available")
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("quantity_tons > 0", name="ck_inventory_positive_quantity"),
        CheckConstraint("reserved_tons >= 0", name="ck_inventory_nonnegative_reserved"),
        CheckConstraint("reserved_tons <= quantity_tons", name="ck_inventory_reserved_within_quantity"),
        CheckConstraint(
            "status IN ('Available', 'Depleted', 'Quarantined')",
            name="ck_inventory_status",
        ),
        UniqueConstraint("lot_id", "warehouse_id", name="uq_inventory_lot_warehouse"),
        Index("ix_inventory_batches_status", "status"),
    )

    harvest_lot = relationship("HarvestLot", back_populates="inventory_batches")
    warehouse = relationship("Warehouse", back_populates="inventory_batches")
    order_lines = relationship("OrderLine", back_populates="inventory_batch")

    @property
    def available_tons(self):
        return self.quantity_tons - self.reserved_tons

class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(String, primary_key=True, index=True) # e.g., 'BYR-001'
    company_name = Column(String, index=True)
    country = Column(String)
    contact_name = Column(String)
    email = Column(String)
    ltv = Column(String) # Lifetime Value, e.g. '$1.2M'
    status = Column(String, default="Active")
    
    # Relationships
    shipments = relationship("Shipment", back_populates="buyer")
    orders = relationship("CustomerOrder", back_populates="buyer")


class CustomerOrder(Base):
    __tablename__ = "customer_orders"

    id = Column(String, primary_key=True, index=True)
    buyer_id = Column(String, ForeignKey("buyers.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(String, nullable=False, default="Reserved")
    ordered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    reserved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('Reserved', 'Shipped', 'Delivered', 'Cancelled')",
            name="ck_customer_order_status",
        ),
        Index("ix_customer_orders_status_ordered_at", "status", "ordered_at"),
    )

    buyer = relationship("Buyer", back_populates="orders")
    lines = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("customer_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    inventory_batch_id = Column(String, ForeignKey("inventory_batches.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity_tons = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity_tons > 0", name="ck_order_line_positive_quantity"),
        UniqueConstraint("order_id", "inventory_batch_id", name="uq_order_line_batch"),
    )

    order = relationship("CustomerOrder", back_populates="lines")
    inventory_batch = relationship("InventoryBatch", back_populates="order_lines")

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(String, primary_key=True, index=True) # e.g., 'SHP-8924'
    order_id = Column(String, ForeignKey("customer_orders.id", ondelete="RESTRICT"), nullable=True, index=True)
    buyer_id = Column(String, ForeignKey("buyers.id", ondelete="RESTRICT"), nullable=False, index=True)
    container_number = Column(String, nullable=False, unique=True, index=True)
    status = Column(String, default="Planned", nullable=False) # Planned, In Transit, Delivered
    internal_temp = Column(Float, nullable=True) # Live telemetry
    eta = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('Planned', 'In Transit', 'Delivered', 'Cancelled')",
            name="ck_shipment_status",
        ),
        Index("ix_shipments_status_eta", "status", "eta"),
    )
    
    # Relationships
    buyer = relationship("Buyer", back_populates="shipments")
    order = relationship("CustomerOrder", back_populates="shipments")
    events = relationship("ShipmentEvent", back_populates="shipment", cascade="all, delete-orphan")


class ShipmentEvent(Base):
    __tablename__ = "shipment_events"

    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    event_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    shipment = relationship("Shipment", back_populates="events")
