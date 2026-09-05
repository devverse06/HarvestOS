"""Generate, validate, transform, and optionally load HarvestOS data.

This pipeline is intentionally deterministic. Generated records are synthetic and
must not be interpreted as production or customer data.
"""
import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
SUMMARY_PATH = ROOT / "data" / "processing_summary.json"

DATASET_SPECS = {
    "farms": ["id", "name", "owner", "location", "crop_type", "area_acres", "expected_yield_tons", "status"],
    "buyers": ["id", "company_name", "country", "contact_name", "email", "ltv", "status"],
    "warehouses": ["id", "name", "location", "capacity_tons", "status"],
    "harvest_lots": ["id", "farm_id", "weight_tons", "quality_grade", "status"],
    "inventory_batches": ["id", "lot_id", "warehouse_id", "quantity_tons", "status"],
    "orders": ["id", "buyer_id", "status"],
    "order_lines": ["id", "order_id", "inventory_batch_id", "quantity_tons"],
    "shipments": ["id", "order_id", "buyer_id", "container_number", "status"],
}


def generate_dataset(output_dir: Path, seed: int = 42, include_errors: bool = False) -> None:
    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    farm_ids = [f"FRM-{index:04d}" for index in range(1, 101)]
    buyer_ids = [f"BYR-{index:04d}" for index in range(1, 101)]
    warehouse_ids = [f"WH-{index:03d}" for index in range(1, 11)]
    lot_ids = [f"LOT-{index:05d}" for index in range(1, 3501)]
    inventory_ids = [f"INV-{index:05d}" for index in range(1, 2501)]
    order_ids = [f"ORD-{index:05d}" for index in range(1, 1801)]

    farms = pd.DataFrame([
        {
            "id": farm_id,
            "name": f"Farm {index:04d}",
            "owner": f"Grower {index:04d}",
            "location": rng.choice(["Nashik", "Pune", "Mysuru", "Coimbatore"]),
            "crop_type": rng.choice(["Grapes", "Mango", "Banana", "Pomegranate"]),
            "area_acres": round(rng.uniform(5, 80), 2),
            "expected_yield_tons": round(rng.uniform(10, 300), 2),
            "status": rng.choice(["Growing", "Harvesting", "Idle"]),
        }
        for index, farm_id in enumerate(farm_ids, start=1)
    ])
    buyers = pd.DataFrame([
        {
            "id": buyer_id,
            "company_name": f"Buyer {index:04d}",
            "country": rng.choice(["India", "Netherlands", "UAE", "United States"]),
            "contact_name": f"Contact {index:04d}",
            "email": f"buyer{index:04d}@example.com",
            "ltv": "$0",
            "status": "Active",
        }
        for index, buyer_id in enumerate(buyer_ids, start=1)
    ])
    warehouses = pd.DataFrame([
        {"id": warehouse_id, "name": f"Warehouse {index:03d}", "location": "Nashik", "capacity_tons": 1000, "status": "Active"}
        for index, warehouse_id in enumerate(warehouse_ids, start=1)
    ])
    harvest_lots = pd.DataFrame([
        {
            "id": lot_id,
            "farm_id": rng.choice(farm_ids),
            "weight_tons": round(rng.uniform(1, 25), 2),
            "quality_grade": rng.choice(["A", "B", "C"]),
            "status": rng.choice(["Intake", "Quality", "Packing", "Storage"]),
        }
        for lot_id in lot_ids
    ])
    inventory_batches = pd.DataFrame([
        {
            "id": inventory_id,
            "lot_id": lot_ids[index - 1],
            "warehouse_id": rng.choice(warehouse_ids),
            "quantity_tons": round(rng.uniform(1, 20), 2),
            "status": "Available",
        }
        for index, inventory_id in enumerate(inventory_ids, start=1)
    ])
    orders = pd.DataFrame([
        {"id": order_id, "buyer_id": rng.choice(buyer_ids), "status": "Reserved"}
        for order_id in order_ids
    ])
    order_lines = pd.DataFrame([
        {
            "id": f"LINE-{index:05d}",
            "order_id": order_id,
            "inventory_batch_id": inventory_ids[index - 1],
            "quantity_tons": round(rng.uniform(0.25, 2), 2),
        }
        for index, order_id in enumerate(order_ids, start=1)
    ])
    shipments = pd.DataFrame([
        {
            "id": f"SHP-{index:05d}",
            "order_id": order_id,
            "buyer_id": orders.iloc[index - 1]["buyer_id"],
            "container_number": f"MSCU{index:07d}",
            "status": rng.choice(["Planned", "In Transit", "Delivered"]),
        }
        for index, order_id in enumerate(order_ids[:190], start=1)
    ])

    frames = {
        "farms": farms,
        "buyers": buyers,
        "warehouses": warehouses,
        "harvest_lots": harvest_lots,
        "inventory_batches": inventory_batches,
        "orders": orders,
        "order_lines": order_lines,
        "shipments": shipments,
    }
    if include_errors:
        frames["harvest_lots"] = pd.concat([harvest_lots, harvest_lots.iloc[[0]]], ignore_index=True)
        invalid_inventory = inventory_batches.iloc[[0]].copy()
        invalid_inventory["id"] = "INV-INVALID"
        invalid_inventory["quantity_tons"] = -1
        frames["inventory_batches"] = pd.concat([inventory_batches, invalid_inventory], ignore_index=True)

    for name, frame in frames.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)


def _clean_frame(name: str, frame: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:
    frame = frame.copy()
    frame.columns = [column.strip() for column in frame.columns]
    for column in frame.select_dtypes(include="object").columns:
        frame[column] = frame[column].astype(str).str.strip()
    duplicate_mask = frame["id"].duplicated(keep="first")
    duplicates = int(duplicate_mask.sum())
    frame = frame.loc[~duplicate_mask].copy()

    invalid_mask = frame["id"].eq("") | frame["id"].isna()
    for column in ["area_acres", "expected_yield_tons", "weight_tons", "quantity_tons", "capacity_tons"]:
        if column in frame:
            numeric = pd.to_numeric(frame[column], errors="coerce")
            frame[column] = numeric
            invalid_mask |= numeric.isna() | numeric.le(0)
    invalid = int(invalid_mask.sum())
    return frame.loc[~invalid_mask].copy(), duplicates, invalid


def _apply_foreign_key_rules(frames: Dict[str, pd.DataFrame]) -> int:
    invalid = 0
    rules = [
        ("harvest_lots", "farm_id", "farms"),
        ("inventory_batches", "lot_id", "harvest_lots"),
        ("inventory_batches", "warehouse_id", "warehouses"),
        ("orders", "buyer_id", "buyers"),
        ("order_lines", "order_id", "orders"),
        ("order_lines", "inventory_batch_id", "inventory_batches"),
        ("shipments", "order_id", "orders"),
        ("shipments", "buyer_id", "buyers"),
    ]
    for child, column, parent in rules:
        valid_ids = set(frames[parent]["id"])
        mask = frames[child][column].isin(valid_ids)
        invalid += int((~mask).sum())
        frames[child] = frames[child].loc[mask].copy()
    return invalid


def validate_and_transform(input_dir: Path) -> Tuple[Dict[str, pd.DataFrame], Dict[str, int]]:
    frames: Dict[str, pd.DataFrame] = {}
    summary = {"records_read": 0, "records_accepted": 0, "records_rejected": 0, "duplicates_found": 0, "invalid_records": 0, "records_loaded": 0}
    for name, columns in DATASET_SPECS.items():
        frame = pd.read_csv(input_dir / f"{name}.csv")
        summary["records_read"] += len(frame)
        cleaned, duplicates, invalid = _clean_frame(name, frame)
        frames[name] = cleaned[columns]
        summary["duplicates_found"] += duplicates
        summary["invalid_records"] += invalid
    summary["invalid_records"] += _apply_foreign_key_rules(frames)
    summary["records_accepted"] = sum(len(frame) for frame in frames.values())
    summary["records_rejected"] = summary["records_read"] - summary["records_accepted"]
    frames["orders"]["total_quantity_tons"] = frames["order_lines"].groupby("order_id")["quantity_tons"].transform("sum")
    frames["harvest_lots"]["yield_band"] = pd.cut(
        frames["harvest_lots"]["weight_tons"],
        bins=[0, 5, 15, float("inf")],
        labels=["small", "medium", "large"],
    )
    return frames, summary


def load_to_postgres(frames: Dict[str, pd.DataFrame], database_url: str) -> int:
    sys.path.insert(0, str(ROOT / "backend"))
    from sqlalchemy import create_engine

    engine = create_engine(database_url)
    load_map = {
        "farms": "farms",
        "buyers": "buyers",
        "warehouses": "warehouses",
        "harvest_lots": "harvest_lots",
        "inventory_batches": "inventory_batches",
        "orders": "customer_orders",
        "order_lines": "order_lines",
        "shipments": "shipments",
    }
    loaded = 0
    with engine.begin() as connection:
        for name, table in load_map.items():
            frame = frames[name].copy()
            drop_columns = {"yield_band", "total_quantity_tons"}
            frame = frame[[column for column in frame.columns if column not in drop_columns]]
            if name == "inventory_batches":
                reservations = frames["order_lines"].groupby("inventory_batch_id")["quantity_tons"].sum()
                frame["reserved_tons"] = frame["id"].map(reservations).fillna(0.0)
            if name == "orders":
                shipped_orders = set(frames["shipments"]["order_id"])
                frame.loc[frame["id"].isin(shipped_orders), "status"] = "Shipped"
            frame.to_sql(table, connection, if_exists="append", index=False, method="multi")
            loaded += len(frame)
        inspections = frames["harvest_lots"][["id", "quality_grade"]].rename(columns={"id": "lot_id", "quality_grade": "grade"})
        inspections.insert(0, "id", "ETL-QI-" + inspections["lot_id"])
        inspections["inspector_id"] = None
        inspections["passed"] = True
        inspections["notes"] = "Synthetic ETL quality record"
        inspections.to_sql("quality_inspections", connection, if_exists="append", index=False, method="multi")
        loaded += len(inspections)
    return loaded


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="Generate deterministic synthetic raw CSV files")
    parser.add_argument("--include-errors", action="store_true", help="Include one duplicate and one invalid raw record")
    parser.add_argument("--input-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--load", action="store_true", help="Load validated frames into DATABASE_URL")
    args = parser.parse_args()

    if args.generate:
        generate_dataset(args.input_dir, include_errors=args.include_errors)
    frames, summary = validate_and_transform(args.input_dir)
    if args.load:
        import os
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is required for --load")
        summary["records_loaded"] = load_to_postgres(frames, database_url)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
