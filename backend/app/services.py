from datetime import datetime, timezone
from typing import Iterable, Tuple

from sqlalchemy.orm import Session

from . import models


class WorkflowError(ValueError):
    pass


ORDER_STATUSES = {"Reserved", "Shipped", "Delivered", "Cancelled"}
SHIPMENT_TRANSITIONS = {
    "Planned": "In Transit",
    "In Transit": "Delivered",
}


def _utcnow():
    return datetime.now(timezone.utc)


def create_reserved_order(db: Session, order_id: str, buyer_id: str, lines: Iterable[Tuple[str, float]]):
    if db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first():
        raise WorkflowError("Order ID already exists")
    if not db.query(models.Buyer).filter(models.Buyer.id == buyer_id).first():
        raise WorkflowError("Buyer not found")

    normalized_lines = list(lines)
    if not normalized_lines:
        raise WorkflowError("An order requires at least one inventory line")
    if len({batch_id for batch_id, _ in normalized_lines}) != len(normalized_lines):
        raise WorkflowError("An inventory batch may appear only once per order")

    order = models.CustomerOrder(id=order_id, buyer_id=buyer_id, status="Reserved")
    db.add(order)

    try:
        for line_id, quantity_tons in normalized_lines:
            if quantity_tons <= 0:
                raise WorkflowError("Order quantities must be greater than zero")
            batch = (
                db.query(models.InventoryBatch)
                .filter(models.InventoryBatch.id == line_id)
                .with_for_update()
                .first()
            )
            if batch is None:
                raise WorkflowError(f"Inventory batch {line_id} not found")
            if batch.status != "Available":
                raise WorkflowError(f"Inventory batch {line_id} is not available")
            if quantity_tons > batch.available_tons:
                raise WorkflowError(f"Insufficient inventory for batch {line_id}")
            batch.reserved_tons += quantity_tons
            order.lines.append(
                models.OrderLine(
                    id=f"{order_id}-{line_id}",
                    inventory_batch_id=line_id,
                    quantity_tons=quantity_tons,
                )
            )
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        raise

    return db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()


def cancel_reserved_order(db: Session, order_id: str):
    order = (
        db.query(models.CustomerOrder)
        .filter(models.CustomerOrder.id == order_id)
        .with_for_update()
        .first()
    )
    if order is None:
        raise WorkflowError("Order not found")
    if order.status != "Reserved":
        raise WorkflowError("Only reserved orders can be cancelled")

    try:
        for line in order.lines:
            batch = (
                db.query(models.InventoryBatch)
                .filter(models.InventoryBatch.id == line.inventory_batch_id)
                .with_for_update()
                .one()
            )
            batch.reserved_tons -= line.quantity_tons
            if batch.reserved_tons < 0:
                raise WorkflowError("Inventory reservation would become negative")
        order.status = "Cancelled"
        order.canceled_at = _utcnow()
        db.commit()
    except Exception:
        db.rollback()
        raise
    return order


def create_shipment_for_order(db: Session, shipment_id: str, order_id: str, container_number: str, eta=None):
    if db.query(models.Shipment).filter(models.Shipment.id == shipment_id).first():
        raise WorkflowError("Shipment ID already exists")
    if db.query(models.Shipment).filter(models.Shipment.container_number == container_number).first():
        raise WorkflowError("Container number already exists")

    order = (
        db.query(models.CustomerOrder)
        .filter(models.CustomerOrder.id == order_id)
        .with_for_update()
        .first()
    )
    if order is None:
        raise WorkflowError("Order not found")
    if order.status != "Reserved":
        raise WorkflowError("Shipment creation requires a reserved order")

    try:
        shipment = models.Shipment(
            id=shipment_id,
            order_id=order.id,
            buyer_id=order.buyer_id,
            container_number=container_number,
            status="Planned",
            eta=eta,
        )
        order.status = "Shipped"
        db.add(shipment)
        db.flush()
        db.add(models.ShipmentEvent(id=f"{shipment_id}-created", shipment_id=shipment_id, status="Planned"))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return shipment


def advance_shipment_status(db: Session, shipment_id: str):
    shipment = (
        db.query(models.Shipment)
        .filter(models.Shipment.id == shipment_id)
        .with_for_update()
        .first()
    )
    if shipment is None:
        raise WorkflowError("Shipment not found")
    next_status = SHIPMENT_TRANSITIONS.get(shipment.status)
    if next_status is None:
        raise WorkflowError(f"Shipment cannot advance from {shipment.status}")

    try:
        shipment.status = next_status
        if next_status == "In Transit":
            shipment.internal_temp = 2.1
        if next_status == "Delivered" and shipment.order is not None:
            shipment.order.status = "Delivered"
        db.add(
            models.ShipmentEvent(
                id=f"{shipment_id}-{next_status.lower().replace(' ', '-')}",
                shipment_id=shipment_id,
                status=next_status,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return shipment
