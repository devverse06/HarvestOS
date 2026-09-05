import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data.pipeline.etl import generate_dataset, validate_and_transform


def test_etl_reports_duplicate_and_invalid_records(tmp_path):
    generate_dataset(tmp_path, include_errors=True)
    frames, summary = validate_and_transform(tmp_path)
    assert summary["records_read"] == 10002
    assert summary["records_accepted"] == 10000
    assert summary["records_rejected"] == 2
    assert summary["duplicates_found"] == 1
    assert summary["invalid_records"] == 1
    assert len(frames["harvest_lots"]) == 3500


def test_etl_adds_derived_fields(tmp_path):
    generate_dataset(tmp_path)
    frames, summary = validate_and_transform(tmp_path)
    assert summary["records_rejected"] == 0
    assert "yield_band" in frames["harvest_lots"].columns
    assert "total_quantity_tons" in frames["orders"].columns
    assert frames["orders"]["total_quantity_tons"].notna().all()
