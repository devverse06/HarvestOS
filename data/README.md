# HarvestOS Data Pipeline

The files under `raw/` are deterministic synthetic records for local development and testing. They are not production or customer data.

## Run

From the repository root:

```bash
python data/pipeline/etl.py --generate --include-errors
```

The pipeline reads the raw CSV files, trims string fields, coerces numeric fields, rejects duplicate IDs, rejects invalid numeric values, validates foreign-key references, derives order totals and harvest yield bands, and writes `processing_summary.json`.

To load validated records into an already migrated PostgreSQL database:

```bash
python data/pipeline/etl.py --load
```

Set `DATABASE_URL` before using `--load`. Run `alembic upgrade head` from `backend/` first. The load operation is append-only and should be run against an empty development database unless the records have been cleared.

The summary is calculated from the files on each run and reports records read, accepted, rejected, duplicates, invalid records, and records loaded.
