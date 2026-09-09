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

- Designed an **11-entity relational data model** with **11 foreign-key constraints** for users, farms, harvest lots, buyers, shipments, and related operational workflows.
- Implemented **35 REST API endpoints** using FastAPI, SQLAlchemy, and Pydantic schemas.
- Added JWT authentication with short-lived access tokens and bcrypt password hashing.
- Added server-side RBAC guards for admin-only and write operations.
- Implemented a traceability path from farm to harvest lot and from buyer to shipment.
- Added password-strength validation, common-password rejection, and input validation.
- Added rate limits for login, registration, and the root API endpoint.
- Added CORS restrictions and security headers middleware.
- Built reusable dashboard and navigation components in React and TypeScript.
- Added **19 automated tests** covering backend functionality, achieving **81% backend test coverage**.

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
