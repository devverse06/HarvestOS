# HarvestOS

## Agricultural Supply Chain & Export Operations Platform

HarvestOS is a full-stack system for managing agricultural procurement, farms, harvest lots, buyers, orders, inventory, shipments, and operational dashboards. It was built as an engineering project to explore how a relational data model, REST APIs, authentication, role-based authorization, and a React interface can support traceable supply-chain workflows.

## Overview

The application connects a React and TypeScript client to a FastAPI backend backed by PostgreSQL. Users can register, authenticate, manage farm and buyer records, create harvest lots, record quality inspections, manage warehouses and inventory, reserve customer orders, create shipments, advance workflow statuses, and view operational information through the dashboard.

The repository also contains frontend views for packhouse operations, quality grading, route planning, market intelligence, export documents, and reports. Some of these views are interface prototypes or use local/demo data rather than complete backend workflows.

## Why I Built This

Agricultural supply chains involve multiple stages between harvest and delivery, including procurement, quality inspection, storage, transportation, and documentation. I built HarvestOS to explore how these workflows could be represented as a single software system with relational data, role-based access, traceability, and operational analytics.

## Key Features

- Farm, harvest lot, quality inspection, warehouse, inventory, buyer, order, and shipment records stored through a relational backend.
- Harvest-lot status flow from `Intake` to `Quality`, `Packing`, and `Storage`.
- Quality inspection requirements before inventory can be created.
- Inventory reservation and release through customer order workflows.
- Traceability from a farm and harvest lot through quality, inventory, orders, and shipments.
- Operational dashboard and frontend pages built with React, TypeScript, Tailwind CSS, and Recharts.
- JWT login and registration with server-side password validation.
- Role-based authorization for administrative actions and data mutations.
- Admin user listing and role management.
- Shipment status advancement and temperature/ETA fields.
- ETL utilities for validating and transforming supply-chain data.
- PostgreSQL-compatible SQLAlchemy models with foreign-key relationships.
- FastAPI OpenAPI documentation available at `/docs` while the API is running.

## Engineering Highlights

- Designed an **11-entity relational data model** with **11 foreign-key constraints** for users, farms, harvest lots, quality inspections, warehouses, inventory, buyers, orders, order lines, shipments, and shipment events.
- Implemented **35 REST API endpoints** using FastAPI, SQLAlchemy, and Pydantic schemas.
- Added JWT authentication with short-lived access tokens and bcrypt password hashing.
- Added server-side RBAC guards for admin-only and write operations.
- Implemented a traceability path from farm to harvest lot and from buyer to shipment.
- Added password-strength validation, common-password rejection, and input validation.
- Added rate limits for login, registration, and the root API endpoint.
- Added CORS restrictions and security headers middleware.
- Built reusable dashboard and navigation components in React and TypeScript.
- Added **19 automated tests** covering backend functionality, achieving **81% total backend test coverage**.

## Application Preview

The repository includes `thumbnail.png` as a project preview. Additional screenshots can be added here as implemented screens are captured:

- Dashboard
- Farms and harvest lots
- Packhouse workflow
- Shipment tracking
- Buyer management

## System Architecture

```text
React + TypeScript
        |
        | REST API with Bearer JWT
        v
FastAPI Backend
        |
   +----+----+
   |         |
SQLAlchemy  Auth and domain logic
   |
   v
PostgreSQL
```

The client calls protected FastAPI routes with a bearer token. FastAPI validates request data with Pydantic, resolves the current user, applies role checks where required, and uses SQLAlchemy sessions to read or update the database. The frontend then renders the returned records in dashboard, CRUD, and workflow views.

## Key Workflows

### Harvest Traceability

```text
Farm
  |
  v
Harvest Lot
  |
  v
Quality Inspection
  |
  v
Inventory -> Order -> Shipment
  |
  v
Operational Dashboard
```

Each harvest lot stores a `farm_id`, weight, quality grade, status, and timestamp. Operators can update the lot status as it moves through the current workflow. Quality inspections and inventory records extend the traceability chain beyond the lot itself.

### Buyer and Shipment Management

```text
Buyer
  |
  v
Customer Order
  |
  v
Shipment
  |
  v
Planned -> In Transit -> Delivered
```

Orders reserve inventory for a buyer. Shipments reference orders and buyers and store container information, status, internal temperature, and ETA. The API exposes shipment listing, creation, status advancement, telemetry lookup, and deletion.

## Database Design

The current SQLAlchemy model contains **11 entities** supporting the application's authentication, farm, harvest, quality, warehouse, inventory, buyer, order, shipment, and operational workflows.

Key entities include:

- `User`: credentials, profile information, and role.
- `Farm`: location, crop type, area, expected yield, and status.
- `HarvestLot`: farm relationship, weight, grade, pipeline status, and logged time.
- `QualityInspection`: lot inspection grade, pass/fail result, inspector, and notes.
- `Warehouse`: storage location, capacity, and status.
- `InventoryBatch`: lot and warehouse relationships, quantity, reservations, and status.
- `Buyer`: company and contact information.
- `CustomerOrder`: buyer relationship, status, timestamps, and order lines.
- `Shipment`: order and buyer relationships, container number, status, temperature, and ETA.

The relational model contains **11 foreign-key constraints**, providing the relationships required for traceability and consistent operational data.

Important relationships include:

```text
Farm -> HarvestLot -> QualityInspection
                    |
                    v
              InventoryBatch -> CustomerOrder -> Shipment
Buyer ----------------------^                 |
                                               v
                                         ShipmentEvent
```

## API Design

The backend exposes **35 REST API endpoints** under `/api`, covering authentication, administration, farm management, harvest-lot workflows, quality inspections, warehouse and inventory management, buyer and order management, shipment operations, traceability, and analytics.

| Area | Examples |
| --- | --- |
| Authentication | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Administration | `GET /api/admin/users`, `PATCH /api/admin/users/{user_id}/role` |
| Farms | `GET`, `POST`, `PUT`, and `DELETE /api/farms` |
| Harvest lots | `GET`, `POST`, `PUT`, `DELETE /api/harvest-lots`, plus status updates |
| Quality | `POST /api/quality-inspections` |
| Warehouses and inventory | `GET` and `POST /api/warehouses`, `GET` and `POST /api/inventory` |
| Buyers and orders | Buyer CRUD, order creation/listing, and order cancellation |
| Shipments | Listing, creation, deletion, telemetry lookup, and status advancement |
| Operations | `GET /api/traceability/{lot_id}`, `GET /api/analytics/summary` |

Interactive API documentation is generated by FastAPI at `http://localhost:8000/docs`.

## Security & Authorization

The implemented security controls include:

- JWT access tokens with a 30-minute expiry.
- bcrypt password hashing.
- Server-assigned roles; users cannot choose a role during registration.
- Admin-only user and role management.
- Admin and Operations checks for write operations.
- Password validation requiring at least 10 characters and rejecting common passwords or identity-based passwords.
- IP-based rate limiting for authentication routes and the root API endpoint.
- Explicit CORS origins and security response headers.
- Generic login errors to avoid revealing whether an email exists.

These controls are implemented for this project and should not be interpreted as a production security audit or certification.

## Testing

HarvestOS includes **19 automated backend tests** covering authentication, authorization, ETL validation, farm and harvest workflows, quality prerequisites, inventory reservation, order cancellation, shipment transitions, traceability, analytics, and duplicate-record handling.

The current test run passes all 19 tests and reports **81% total coverage** for the `backend/app` package.

### Testing Metrics

| Metric | Result |
| --- | --- |
| Automated tests | **19** |
| Backend test coverage | **81%** |

## Tech Stack

### Frontend

- React 18
- TypeScript
- Vite
- React Router
- Tailwind CSS
- Recharts
- React Three Fiber and Three.js
- Framer Motion

### Backend

- Python
- FastAPI
- SQLAlchemy 2.0
- Pydantic 2
- PostgreSQL via `psycopg2-binary`
- Alembic for database migrations
- `python-jose` and bcrypt for authentication
- SlowAPI for rate limiting

### Testing

- Pytest
- Automated backend tests
- Coverage analysis

## Project Structure

```text
HarvestOS/
├── backend/
│   ├── app/
│   │   ├── auth.py          JWT and password handling
│   │   ├── database.py      SQLAlchemy engine and sessions
│   │   ├── main.py          FastAPI routes and middleware
│   │   ├── models.py        SQLAlchemy data model
│   │   └── schemas.py       Pydantic request and response schemas
│   ├── tests/               Backend test suite
│   └── requirements.txt
├── client/
│   ├── src/
│   │   ├── components/      Shared layout and dashboard components
│   │   ├── context/         Authentication context
│   │   ├── pages/           Application screens
│   │   └── services/        API client
│   └── package.json
├── data/
│   ├── pipeline/            ETL processing code
│   ├── raw/                 Source CSV files
│   └── processing_summary.json
├── 04_technical_architecture.md
├── 02_user_journey_rbac.md
├── render.yaml
└── README.md
```

## Local Setup

### Prerequisites

- Python 3.9 or later
- Node.js 18 or later
- PostgreSQL

### Backend

```powershell
cd backend
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

pip install -r requirements.txt
$env:SECRET_KEY = "generate-a-long-random-secret"
$env:DATABASE_URL = "postgresql://user:password@localhost/harvestos"
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

### Frontend

```powershell
cd client
npm install
npm run dev
```

The Vite development server runs at `http://localhost:5173`.

The first registered user is assigned the `Admin` role. Later registrations are assigned `Pending` until an administrator changes their role.

### Backend Tests

```powershell
cd backend
python -m pytest
python -m pytest --cov=app --cov-report=term-missing
```

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Signs JWT access tokens; required by the backend. |
| `DATABASE_URL` | PostgreSQL connection string used by SQLAlchemy. |

Do not commit secrets or local environment files.

## Technical Decisions

### Why PostgreSQL?

The project has related entities and foreign-key relationships, so a relational database is a natural fit for maintaining consistent farm, lot, buyer, order, inventory, and shipment data.

### Why FastAPI?

FastAPI provides typed request validation through Pydantic and generated OpenAPI documentation, which makes the API easier to inspect while developing the client.

### Why React and TypeScript?

React supports reusable pages and layout components, while TypeScript helps keep frontend API models and component props explicit.

### Why JWT and RBAC?

The application has different operational responsibilities. JWT handles authenticated API requests, while server-side role checks prevent unauthorized mutations and administration actions.

### Why SQLAlchemy?

SQLAlchemy provides a Python ORM for expressing the project relationships and keeping database access in the backend rather than in frontend code.

## What I Learned

Building HarvestOS helped me understand:

- designing relational database relationships
- structuring a FastAPI application
- connecting a React client to REST endpoints
- implementing authentication and RBAC
- validating operational data at the API boundary
- modeling workflow state with status fields
- writing automated backend tests and measuring test coverage
- separating reusable frontend layout from page-level behavior
- documenting tradeoffs and implementation limits honestly


## Additional Documentation

The repository contains earlier design and planning notes. The most implementation-relevant document is [04_technical_architecture.md](04_technical_architecture.md). The role and user-flow notes are in [02_user_journey_rbac.md](02_user_journey_rbac.md).
