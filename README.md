# HarvestOS

## Agricultural Supply Chain & Export Operations Platform

HarvestOS is a full-stack system for managing agricultural procurement, farms, harvest lots, buyers, shipments, and operational dashboards. It was built as an engineering project to explore how a relational data model, REST APIs, authentication, role-based authorization, and a React interface can support traceable supply-chain workflows.

## Overview

The application connects a React and TypeScript client to a FastAPI backend backed by PostgreSQL. Users can register, authenticate, manage farm and buyer records, create harvest lots, advance lot statuses, create shipments, and view operational information through the dashboard.

The repository also contains frontend views for packhouse operations, quality grading, route planning, market intelligence, export documents, and reports. Some of these views are interface prototypes or use local/demo data rather than complete backend workflows.

## Why I Built This

Agricultural supply chains involve multiple stages between harvest and delivery, including procurement, quality inspection, storage, transportation, and documentation. I built HarvestOS to explore how these workflows could be represented as a single software system with relational data, role-based access, traceability, and operational analytics.

## Key Features

- Farm, harvest lot, buyer, and shipment records stored through a relational backend.
- Harvest-lot status flow from `Intake` to `Quality`, `Packing`, and `Storage`.
- Dashboard and operational pages built with React, TypeScript, Tailwind CSS, and Recharts.
- JWT login and registration with server-side password validation.
- Role-based authorization for administrative actions and data mutations.
- Admin user listing and role management.
- Shipment status advancement and temperature/ETA fields.
- PostgreSQL-compatible SQLAlchemy models with foreign-key relationships.
- FastAPI OpenAPI documentation available at `/docs` while the API is running.

## Engineering Highlights

- Designed a relational data model for users, farms, harvest lots, buyers, and shipments.
- Implemented REST endpoints using FastAPI, SQLAlchemy, and Pydantic schemas.
- Added JWT authentication with short-lived access tokens and bcrypt password hashing.
- Added server-side RBAC guards for admin-only and write operations.
- Implemented a traceability path from farm to harvest lot and from buyer to shipment.
- Added password-strength validation, common-password rejection, and input validation.
- Added rate limits for login, registration, and the root API endpoint.
- Added CORS restrictions and security headers middleware.
- Built reusable dashboard and navigation components in React and TypeScript.

## Application Preview

The repository currently includes `thumbnail.png` as a project preview. Additional screenshots should be added here as the implemented screens are captured:

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
Quality / Packing / Storage Status
  |
  v
Operational Dashboard
```

Each harvest lot stores a `farm_id`, weight, quality grade, status, and timestamp. Operators can update the lot status as it moves through the current workflow.

### Buyer and Shipment Management

```text
Buyer
  |
  v
Shipment
  |
  v
Planned -> In Transit -> Delivered
```

Shipments reference buyers and store container information, status, internal temperature, and ETA. The API exposes shipment listing, creation, status advancement, telemetry lookup, and deletion.

## Database Design

The current SQLAlchemy model contains these main entities:

- `User`: credentials, profile information, and role.
- `Farm`: location, crop type, area, expected yield, and status.
- `HarvestLot`: farm relationship, weight, grade, pipeline status, and logged time.
- `Buyer`: company and contact information.
- `Shipment`: buyer relationship, container number, status, temperature, and ETA.

The important relationships are `Farm -> HarvestLot` and `Buyer -> Shipment`. These foreign keys provide the foundation for tracing operational records back to their related farm or buyer.

## API Design

The backend exposes REST endpoints under `/api`:

| Area | Examples |
| --- | --- |
| Authentication | `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` |
| Administration | `GET /api/admin/users`, `PATCH /api/admin/users/{user_id}/role` |
| Farms | `GET`, `POST`, `PUT`, and `DELETE /api/farms` |
| Harvest lots | `GET`, `POST`, `PUT`, `DELETE /api/harvest-lots`, plus status updates |
| Buyers | `GET`, `POST`, `PUT`, and `DELETE /api/buyers` |
| Shipments | `GET`, `POST`, `DELETE`, telemetry lookup, and status advancement |

Interactive API documentation is generated by FastAPI at `http://localhost:8000/docs`.

## Security & Authorization

The implemented security controls include:

- JWT access tokens with a 30-minute expiry.
- bcrypt password hashing.
- Server-assigned roles; users cannot choose a role during registration.
- Admin-only user and role management.
- Admin and Operations checks for write operations.
- Password validation requiring at least 10 characters and rejecting common passwords or identity-based passwords.
- IP-based rate limiting for authentication routes.
- Explicit CORS origins and security response headers.
- Generic login errors to avoid revealing whether an email exists.

These controls are implemented for this project and should not be interpreted as a production security audit or certification.

## Testing Status

There is currently no committed automated test suite in the repository. Authentication, authorization, and critical workflow tests are a planned improvement rather than an implemented feature. This is intentionally documented so the project description matches the current code.

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
- Alembic dependency for database migrations
- `python-jose` and bcrypt for authentication
- SlowAPI for rate limiting

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
│   └── requirements.txt
├── client/
│   ├── src/
│   │   ├── components/      Shared layout and dashboard components
│   │   ├── context/         Authentication context
│   │   ├── pages/           Application screens
│   │   └── services/        API client
│   └── package.json
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

```bash
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

```bash
cd client
npm install
npm run dev
```

The Vite development server runs at `http://localhost:5173`.

The first registered user is assigned the `Admin` role. Later registrations are assigned `Pending` until an administrator changes their role.

## Environment Variables

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Signs JWT access tokens; required by the backend. |
| `DATABASE_URL` | PostgreSQL connection string used by SQLAlchemy. |

Do not commit secrets or local environment files.

## Technical Decisions

### Why PostgreSQL?

The project has related entities and foreign-key relationships, so a relational database is a natural fit for maintaining consistent farm, lot, buyer, and shipment data.

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
- separating reusable frontend layout from page-level behavior
- documenting tradeoffs and implementation limits honestly

## Future Improvements

- Add automated tests for authentication, RBAC, CRUD operations, and lot/shipment workflows.
- Add database migration files and a repeatable seed dataset.
- Connect quality, route, export-document, and market-intelligence screens to dedicated backend services.
- Add file storage for export documents.
- Add CI for frontend lint/build and backend tests.
- Add Docker-based local development once the service configuration is finalized.

## Additional Documentation

The repository contains earlier design and planning notes. The most implementation-relevant document is [04_technical_architecture.md](04_technical_architecture.md). The role and user-flow notes are in [02_user_journey_rbac.md](02_user_journey_rbac.md).
