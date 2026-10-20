# 🛸 Flying Cabs — Next-Gen Aero Mobility Platform

A full-stack ride-hailing and sky-transit application built with a **Python stack (FastAPI)** and a modern **interactive web frontend with Leaflet.js maps and WebSockets**.

This project implements the architecture, data models, endpoints, and MVP recommendations detailed in the Google Drive specification (**Cab Booking Platform — Python Stack**).

> 📖 **Looking for the exhaustive technical manual?** Read the [Full System & Architecture Documentation](DOCUMENTATION.md) for complete entity diagrams, algorithmic formulas, WebSocket protocol specs, and API request/response schemas.

---

## ✨ Features & Architecture Highlights

### 1. Python Backend (FastAPI + SQLAlchemy + WebSockets)
- **FastAPI Core**: High-performance ASGI REST endpoints with automated OpenAPI docs at [`/docs`](http://127.0.0.1:3000/docs).
- **Interactive Database**: SQLite with SQLAlchemy models matching Section 4 of the spec:
  - `User`: Roles (`rider`, `driver`), profile, rating average.
  - `Driver`: Vehicle info, `vehicle_type` (`flying`, `standard`, `luxury`), telemetry coordinates, altitude (`altitude_m`), battery %, status (`active`, `busy`, `offline`), shift earnings.
  - `Ride`: Pickup & dropoff coordinates, fare estimates, status progression (`REQUESTED` → `ACCEPTED` → `ARRIVED` → `IN_PROGRESS` → `COMPLETED`).
  - `Payment`: Stripe `PaymentIntent` ID simulation, amount, payment method, timestamps.
  - `Review`: Star rating (1–5), pilot feedback comments.
- **Bi-directional WebSockets**:
  - `ws /ws/rider/{rider_id}`: Real-time driver dispatch alerts, GPS waypoints, arrival alerts, flight liftoff & touchdown notifications.
  - `ws /ws/driver/{driver_id}`: Incoming skyway dispatch offers, turn-by-turn simulation.
  - `ws /ws/map`: Global broadcast channel for fleet telemetry radar.
- **Haversine Fare & Sky-Corridor Estimator**:
  - **🛸 AeroCab Express (VTOL)**: High-altitude sky-corridor transit, 3x faster, zero street congestion.
  - **🚖 City Standard Cab**: Ground eco-cruiser for everyday city routes.
  - **⚡ Cyber Executive Cruiser**: Quiet luxury EV flagship.

### 2. Modern Aero-Tech Frontend
- **Aesthetic**: Futuristic glassmorphism with dark cosmic palette (`#070a12`, electric cyan `#00f0ff`, aero gold `#ffb703`, emerald green `#00f59b`).
- **Interactive Leaflet Map** *(Explicitly recommended on line 203 of the Drive document for MVP)*:
  - Click anywhere on the map or pick hotspots (*Downtown Helipad, SF Skyport, Tech Hub SOMA, Marina Pier*).
  - High-altitude polyline corridor showing direct flight vectors.
  - Animated pulsing vehicle marker showing real-time GPS movement.
- **3 Context Modes**:
  1. **Rider Mode**: Pick locations, compare flight tiers, dispatch cabs, track flight progress live, pay with simulated Stripe gateway, download flight receipts, and submit pilot reviews.
  2. **Driver Cockpit**: Toggle online status, receive audio-chime dispatch alerts, accept rides, advance flight phases manually.
  3. **Fleet Radar**: High-altitude ATC radar displaying active cabs, speed, battery %, and altitude.
- **Synthesized Audio Effects**: Native Web Audio API sound synthesizer (dispatch chimes, takeoff whoosh, arrival pings — zero external mp3 files).
- **Auto-Pilot Simulation**: Built-in toggle to test the full lifecycle automatically in 15 seconds without needing a second device or driver.

---

## 🚀 Quickstart Guide (Run Locally)

FastAPI, Uvicorn, and SQLAlchemy are pre-configured. You can run the entire platform with a single command:

```powershell
py run.py
```

Or run via Uvicorn directly:

```powershell
py -m uvicorn backend.app.main:app --reload --port 8000
```

Once running:
- **Web App**: Open [http://127.0.0.1:3000](http://127.0.0.1:3000)
- **Interactive Swagger API Docs**: Open [http://127.0.0.1:3000/docs](http://127.0.0.1:3000/docs)

---

## 🧪 Automated Test Suite

A complete test suite is included in `tests/test_api.py` covering health, auth sessions, nearby drivers, fare estimation, the full ride lifecycle, payments, reviews, receipts, and ride history.

Run tests:
```powershell
py -m pytest tests/test_api.py -v
```

---

## 🐳 Docker Deployment (Optional)

```bash
docker-compose up --build
```

---

## 📂 Project Directory Structure

```
Flying Cabs/
├── backend/
│   ├── app/
│   │   ├── config.py             # App settings & environment config
│   │   ├── database.py           # SQLAlchemy engine & session maker
│   │   ├── models.py             # User, Driver, Ride, Payment, Review models
│   │   ├── schemas.py            # Pydantic validation schemas
│   │   ├── main.py               # FastAPI app, static mounts, WebSockets, DB seeding
│   │   ├── routers/
│   │   │   ├── auth.py           # /api/auth endpoints & demo user switcher
│   │   │   ├── rides.py          # /api/rides estimation, booking, status
│   │   │   ├── drivers.py        # /api/drivers nearby lookup & cockpit stats
│   │   │   └── payments.py       # /api/rides pay, review, receipt generation
│   │   └── services/
│   │       ├── fare_calculator.py  # Haversine distance & tiered pricing engine
│   │       ├── websocket_manager.py# Real-time connection & broadcast manager
│   │       └── simulation_service.py # Autonomous driver movement & flight simulation
├── frontend/
│   ├── index.html                # Modern semantic single-page UI
│   ├── style.css                 # Aero-tech design system & dark glassmorphic styling
│   ├── app.js                    # State management, Leaflet map, audio synthesizer
│   └── assets/
│       └── logo.png              # Futuristic AeroCab emblem
├── tests/
│   └── test_api.py               # Comprehensive pytest test suite
├── Dockerfile                    # Containerization buildfile
├── docker-compose.yml            # Multi-service compose config
├── requirements.txt              # Python package dependencies
├── run.py                        # One-click launch runner
└── README.md                     # Documentation & specification mapping
```

---

## 📋 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register new rider or driver partner with face photo & car choice |
| `POST` | `/api/auth/login` | Authenticate existing user via Email or Mobile Phone |
| `GET` | `/api/auth/avatars` | Fetch curated Indian face avatars for rider & pilot profiles |
| `POST` | `/api/auth/quick-switch/{id}`| 1-click instant persona switching between demo accounts |
| `GET` | `/api/auth/me` | Fetch active authenticated profile details |
| `POST` | `/api/auth/session` | Verify active user session (simulates Clerk/Supabase auth) |
| `GET` | `/api/auth/users` | List demo users to test multiple passenger & driver roles |
| `GET` | `/api/drivers/nearby` | Geospatial lookup for active drivers with Pan-India fleet distribution |
| `GET` | `/api/drivers/{id}/dashboard` | Driver shift metrics, daily earnings, and pending trips |
| `POST` | `/api/drivers/{id}/location` | Telemetry coordinate & altitude publisher |
| `POST` | `/api/drivers/{id}/status` | Toggle driver availability (`active` / `offline`) |
| `GET` | `/api/rides/estimate` | Compute route distance, ETA, tiered pricing with car & pilot info |
| `POST` | `/api/rides/request` | Dispatch ride request and broadcast via WebSockets |
| `GET` | `/api/rides/{id}/status` | Retrieve current status and tracking telemetry |
| `POST` | `/api/rides/{id}/accept` | Driver accepts dispatched trip |
| `POST` | `/api/rides/{id}/update-status`| Update status (`ARRIVED`, `IN_PROGRESS`, `COMPLETED`) |
| `POST` | `/api/rides/{id}/pay` | Authorize fare payment (simulates Razorpay / UPI gateway) |
| `POST` | `/api/rides/{id}/review` | Submit driver rating and feedback |
| `GET` | `/api/rides/{id}/receipt` | Generate itemized flight & GST breakdown receipt |
| `GET` | `/api/rides/history` | Retrieve past ride records |
| `WS` | `/ws/rider/{id}` | Real-time rider WebSocket channel |
| `WS` | `/ws/driver/{id}` | Real-time driver WebSocket channel |
| `WS` | `/ws/map` | Real-time fleet telemetry map broadcast channel |

