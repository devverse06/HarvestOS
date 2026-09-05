"""Create the HarvestOS relational schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), server_default="Farmer", nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    op.create_table(
        "farms",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("owner", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("crop_type", sa.String(), nullable=True),
        sa.Column("area_acres", sa.Float(), nullable=True),
        sa.Column("expected_yield_tons", sa.Float(), nullable=True),
        sa.Column("status", sa.String(), server_default="Growing", nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_farms_id", "farms", ["id"], unique=False)
    op.create_index("ix_farms_name", "farms", ["name"], unique=False)

    op.create_table(
        "buyers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("company_name", sa.String(), nullable=True),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("contact_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("ltv", sa.String(), nullable=True),
        sa.Column("status", sa.String(), server_default="Active", nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_buyers_id", "buyers", ["id"], unique=False)
    op.create_index("ix_buyers_company_name", "buyers", ["company_name"], unique=False)

    op.create_table(
        "warehouses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("capacity_tons", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), server_default="Active", nullable=False),
        sa.CheckConstraint("capacity_tons > 0", name="ck_warehouse_positive_capacity"),
        sa.CheckConstraint("status IN ('Active', 'Inactive')", name="ck_warehouse_status"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_warehouses_id", "warehouses", ["id"], unique=False)
    op.create_index("ix_warehouses_name", "warehouses", ["name"], unique=False)

    op.create_table(
        "harvest_lots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("farm_id", sa.String(), nullable=False),
        sa.Column("weight_tons", sa.Float(), nullable=True),
        sa.Column("quality_grade", sa.String(), nullable=True),
        sa.Column("status", sa.String(), server_default="Intake", nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.CheckConstraint("weight_tons > 0", name="ck_harvest_lot_positive_weight"),
        sa.CheckConstraint("status IN ('Intake', 'Quality', 'Packing', 'Storage')", name="ck_harvest_lot_status"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_harvest_lots_id", "harvest_lots", ["id"], unique=False)
    op.create_index("ix_harvest_lots_farm_id", "harvest_lots", ["farm_id"], unique=False)
    op.create_index("ix_harvest_lots_status_logged_at", "harvest_lots", ["status", "logged_at"], unique=False)

    op.create_table(
        "quality_inspections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("lot_id", sa.String(), nullable=False),
        sa.Column("inspector_id", sa.String(), nullable=True),
        sa.Column("grade", sa.String(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("inspected_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["inspector_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lot_id"], ["harvest_lots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quality_inspections_id", "quality_inspections", ["id"], unique=False)
    op.create_index("ix_quality_inspections_lot_id", "quality_inspections", ["lot_id"], unique=False)
    op.create_index("ix_quality_inspections_inspector_id", "quality_inspections", ["inspector_id"], unique=False)

    op.create_table(
        "inventory_batches",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("lot_id", sa.String(), nullable=False),
        sa.Column("warehouse_id", sa.String(), nullable=False),
        sa.Column("quantity_tons", sa.Float(), nullable=False),
        sa.Column("reserved_tons", sa.Float(), server_default="0", nullable=False),
        sa.Column("status", sa.String(), server_default="Available", nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("quantity_tons > 0", name="ck_inventory_positive_quantity"),
        sa.CheckConstraint("reserved_tons >= 0", name="ck_inventory_nonnegative_reserved"),
        sa.CheckConstraint("reserved_tons <= quantity_tons", name="ck_inventory_reserved_within_quantity"),
        sa.CheckConstraint("status IN ('Available', 'Depleted', 'Quarantined')", name="ck_inventory_status"),
        sa.ForeignKeyConstraint(["lot_id"], ["harvest_lots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lot_id", "warehouse_id", name="uq_inventory_lot_warehouse"),
    )
    op.create_index("ix_inventory_batches_id", "inventory_batches", ["id"], unique=False)
    op.create_index("ix_inventory_batches_lot_id", "inventory_batches", ["lot_id"], unique=False)
    op.create_index("ix_inventory_batches_warehouse_id", "inventory_batches", ["warehouse_id"], unique=False)
    op.create_index("ix_inventory_batches_status", "inventory_batches", ["status"], unique=False)

    op.create_table(
        "customer_orders",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("buyer_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="Reserved", nullable=False),
        sa.Column("ordered_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('Reserved', 'Shipped', 'Delivered', 'Cancelled')", name="ck_customer_order_status"),
        sa.ForeignKeyConstraint(["buyer_id"], ["buyers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customer_orders_id", "customer_orders", ["id"], unique=False)
    op.create_index("ix_customer_orders_buyer_id", "customer_orders", ["buyer_id"], unique=False)
    op.create_index("ix_customer_orders_status_ordered_at", "customer_orders", ["status", "ordered_at"], unique=False)

    op.create_table(
        "order_lines",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("order_id", sa.String(), nullable=False),
        sa.Column("inventory_batch_id", sa.String(), nullable=False),
        sa.Column("quantity_tons", sa.Float(), nullable=False),
        sa.CheckConstraint("quantity_tons > 0", name="ck_order_line_positive_quantity"),
        sa.ForeignKeyConstraint(["inventory_batch_id"], ["inventory_batches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["customer_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id", "inventory_batch_id", name="uq_order_line_batch"),
    )
    op.create_index("ix_order_lines_id", "order_lines", ["id"], unique=False)
    op.create_index("ix_order_lines_order_id", "order_lines", ["order_id"], unique=False)
    op.create_index("ix_order_lines_inventory_batch_id", "order_lines", ["inventory_batch_id"], unique=False)

    op.create_table(
        "shipments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("order_id", sa.String(), nullable=True),
        sa.Column("buyer_id", sa.String(), nullable=False),
        sa.Column("container_number", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="Planned", nullable=False),
        sa.Column("internal_temp", sa.Float(), nullable=True),
        sa.Column("eta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("status IN ('Planned', 'In Transit', 'Delivered', 'Cancelled')", name="ck_shipment_status"),
        sa.ForeignKeyConstraint(["buyer_id"], ["buyers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["order_id"], ["customer_orders.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("container_number"),
    )
    op.create_index("ix_shipments_id", "shipments", ["id"], unique=False)
    op.create_index("ix_shipments_order_id", "shipments", ["order_id"], unique=False)
    op.create_index("ix_shipments_buyer_id", "shipments", ["buyer_id"], unique=False)
    op.create_index("ix_shipments_container_number", "shipments", ["container_number"], unique=False)
    op.create_index("ix_shipments_status_eta", "shipments", ["status", "eta"], unique=False)

    op.create_table(
        "shipment_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("shipment_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("event_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["shipment_id"], ["shipments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shipment_events_id", "shipment_events", ["id"], unique=False)
    op.create_index("ix_shipment_events_shipment_id", "shipment_events", ["shipment_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_shipment_events_shipment_id", table_name="shipment_events")
    op.drop_index("ix_shipment_events_id", table_name="shipment_events")
    op.drop_table("shipment_events")
    op.drop_index("ix_shipments_status_eta", table_name="shipments")
    op.drop_index("ix_shipments_container_number", table_name="shipments")
    op.drop_index("ix_shipments_buyer_id", table_name="shipments")
    op.drop_index("ix_shipments_order_id", table_name="shipments")
    op.drop_index("ix_shipments_id", table_name="shipments")
    op.drop_table("shipments")
    op.drop_index("ix_order_lines_inventory_batch_id", table_name="order_lines")
    op.drop_index("ix_order_lines_order_id", table_name="order_lines")
    op.drop_index("ix_order_lines_id", table_name="order_lines")
    op.drop_table("order_lines")
    op.drop_index("ix_customer_orders_status_ordered_at", table_name="customer_orders")
    op.drop_index("ix_customer_orders_buyer_id", table_name="customer_orders")
    op.drop_index("ix_customer_orders_id", table_name="customer_orders")
    op.drop_table("customer_orders")
    op.drop_index("ix_inventory_batches_status", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_warehouse_id", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_lot_id", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_id", table_name="inventory_batches")
    op.drop_table("inventory_batches")
    op.drop_index("ix_quality_inspections_inspector_id", table_name="quality_inspections")
    op.drop_index("ix_quality_inspections_lot_id", table_name="quality_inspections")
    op.drop_index("ix_quality_inspections_id", table_name="quality_inspections")
    op.drop_table("quality_inspections")
    op.drop_index("ix_harvest_lots_status_logged_at", table_name="harvest_lots")
    op.drop_index("ix_harvest_lots_farm_id", table_name="harvest_lots")
    op.drop_index("ix_harvest_lots_id", table_name="harvest_lots")
    op.drop_table("harvest_lots")
    op.drop_index("ix_warehouses_name", table_name="warehouses")
    op.drop_index("ix_warehouses_id", table_name="warehouses")
    op.drop_table("warehouses")
    op.drop_index("ix_buyers_company_name", table_name="buyers")
    op.drop_index("ix_buyers_id", table_name="buyers")
    op.drop_table("buyers")
    op.drop_index("ix_farms_name", table_name="farms")
    op.drop_index("ix_farms_id", table_name="farms")
    op.drop_table("farms")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
