from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.database import get_db
from backend.app.models import Ride, Driver, User
from backend.app.schemas import (
    FareEstimateResponse, RideCreate, RideResponse,
    RideStatusUpdate, ApiConfigResponse, ApiConfigUpdateRequest
)
from backend.app.services.fare_calculator import calculate_fare_options
from backend.app.services.websocket_manager import ws_manager
from backend.app.services.simulation_service import start_simulation
from backend.app.config import settings

router = APIRouter(prefix="/rides", tags=["rides"])

@router.get("/estimate", response_model=FareEstimateResponse)
def get_fare_estimate(
    origin_lat: float = Query(..., description="Pickup latitude"),
    origin_lng: float = Query(..., description="Pickup longitude"),
    dest_lat: float = Query(..., description="Destination latitude"),
    dest_lng: float = Query(..., description="Destination longitude"),
):
    """
    Calculates distance, duration, and tiered fare estimates for
    City Standard, AeroCab VTOL Flying Cab, and Cyber Executive Cruiser.
    """
    estimates = calculate_fare_options(origin_lat, origin_lng, dest_lat, dest_lng)
    return estimates

@router.post("/request", response_model=RideResponse)
async def request_ride(
    ride_in: RideCreate,
    auto_simulate: bool = Query(True, description="Automatically simulate driver acceptance and GPS transit"),
    db: Session = Depends(get_db)
):
    """
    Creates a new ride request and notifies available drivers via WebSockets.
    """
    rider = db.query(User).filter(User.id == ride_in.rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider user not found")

    import random
    otp_code = f"{random.randint(1000, 9999)}"

    new_ride = Ride(
        rider_id=ride_in.rider_id,
        pickup_name=ride_in.pickup_name,
        pickup_lat=ride_in.pickup_lat,
        pickup_lng=ride_in.pickup_lng,
        drop_name=ride_in.drop_name,
        drop_lat=ride_in.drop_lat,
        drop_lng=ride_in.drop_lng,
        vehicle_type=ride_in.vehicle_type,
        car_model=ride_in.car_model or ride_in.vehicle_type,
        status="REQUESTED",
        otp=otp_code,
        payment_mode=ride_in.payment_mode or "razorpay",
        fare_estimate=ride_in.fare_estimate,
        distance_km=ride_in.distance_km,
        duration_mins=ride_in.duration_mins,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)

    # Broadcast to driver sockets
    await ws_manager.broadcast_to_drivers("NEW_RIDE_REQUEST", {
        "ride_id": new_ride.id,
        "pickup_name": new_ride.pickup_name,
        "drop_name": new_ride.drop_name,
        "vehicle_type": new_ride.vehicle_type,
        "fare_estimate": new_ride.fare_estimate,
        "distance_km": new_ride.distance_km
    })

    # Broadcast to live fleet map
    await ws_manager.broadcast_to_map("RIDE_REQUESTED", {
        "ride_id": new_ride.id,
        "pickup": [new_ride.pickup_lat, new_ride.pickup_lng],
        "drop": [new_ride.drop_lat, new_ride.drop_lng]
    })

    # Auto-simulate driver matching and progression for smooth local testing
    if auto_simulate or settings.SIMULATION_AUTO_DRIVER:
        start_simulation(new_ride.id)

    return new_ride

@router.get("/history", response_model=List[RideResponse])
def get_ride_history(
    user_id: Optional[int] = Query(None, description="Filter by user id"),
    db: Session = Depends(get_db)
):
    """Retrieve history of completed or requested rides."""
    query = db.query(Ride).order_by(Ride.created_at.desc())
    if user_id:
        query = query.filter((Ride.rider_id == user_id) | (Ride.driver_id == user_id))
    return query.limit(20).all()

@router.get("/{ride_id}/status", response_model=RideResponse)
def get_ride_status(ride_id: int, db: Session = Depends(get_db)):
    """Fetch current status and coordinates of a ride."""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

@router.post("/{ride_id}/accept", response_model=RideResponse)
async def accept_ride(
    ride_id: int,
    driver_id: int = Query(..., description="ID of driver accepting the ride"),
    db: Session = Depends(get_db)
):
    """Driver manually accepts an incoming ride request."""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    if ride.status != "REQUESTED":
        raise HTTPException(status_code=400, detail=f"Ride cannot be accepted in status {ride.status}")

    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    ride.driver_id = driver.id
    ride.status = "ACCEPTED"
    ride.accepted_at = datetime.now(timezone.utc)
    driver.status = "busy"
    db.commit()
    db.refresh(ride)

    driver_info = {
        "id": driver.id,
        "name": driver.user.name,
        "phone": driver.user.phone,
        "vehicle_info": driver.vehicle_info,
        "vehicle_type": driver.vehicle_type,
        "license_plate": driver.license_plate,
        "rating_avg": driver.user.rating_avg,
        "current_lat": driver.current_lat,
        "current_lng": driver.current_lng,
        "altitude_m": driver.altitude_m,
        "battery_pct": driver.battery_pct
    }

    # Notify rider via WebSocket
    await ws_manager.send_to_rider(ride.rider_id, "RIDE_ACCEPTED", {
        "ride_id": ride.id,
        "status": "ACCEPTED",
        "otp": ride.otp,
        "driver": driver_info
    })

    return ride

@router.post("/{ride_id}/update-status", response_model=RideResponse)
async def update_ride_status(
    ride_id: int,
    status_update: RideStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update ride status (ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED)."""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # In India (Ola & Uber), verify passenger OTP before starting trip
    if status_update.status == "IN_PROGRESS" and status_update.entered_otp:
        if str(status_update.entered_otp).strip() != str(ride.otp).strip():
            raise HTTPException(status_code=400, detail="Invalid 4-digit ride OTP. Please verify with passenger.")

    ride.status = status_update.status
    if status_update.status == "COMPLETED":
        ride.completed_at = datetime.now(timezone.utc)
        ride.fare_actual = ride.fare_estimate
        if ride.driver:
            ride.driver.status = "active"
            ride.driver.total_trips += 1
            ride.driver.earnings_today += ride.fare_actual

    db.commit()
    db.refresh(ride)

    # Notify rider
    event_map = {
        "ARRIVED": "DRIVER_ARRIVED",
        "IN_PROGRESS": "RIDE_STARTED",
        "COMPLETED": "RIDE_COMPLETED",
        "CANCELLED": "RIDE_CANCELLED"
    }
    event_name = event_map.get(ride.status, "RIDE_STATUS_UPDATED")
    await ws_manager.send_to_rider(ride.rider_id, event_name, {
        "ride_id": ride.id,
        "status": ride.status,
        "otp": ride.otp,
        "fare": ride.fare_actual or ride.fare_estimate
    })

    return ride

@router.post("/{ride_id}/cancel")
async def cancel_ride(ride_id: int, db: Session = Depends(get_db)):
    """Cancel an active or pending ride."""
    from backend.app.services.simulation_service import cancel_simulation
    cancel_simulation(ride_id)

    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    ride.status = "CANCELLED"
    if ride.driver:
        ride.driver.status = "active"
    db.commit()

    await ws_manager.send_to_rider(ride.rider_id, "RIDE_CANCELLED", {"ride_id": ride.id})
    return {"status": "ok", "message": "Ride cancelled"}

@router.get("/config/keys", response_model=ApiConfigResponse)
def get_api_config_keys():
    """Returns configured API keys for Google Maps and Razorpay."""
    return ApiConfigResponse(
        google_maps_api_key=settings.GOOGLE_MAPS_API_KEY,
        google_maps_map_type=settings.GOOGLE_MAPS_MAP_TYPE,
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
        razorpay_currency=settings.RAZORPAY_CURRENCY,
        merchant_name=settings.MERCHANT_NAME
    )

@router.post("/config/keys", response_model=ApiConfigResponse)
def update_api_config_keys(req: ApiConfigUpdateRequest):
    """Allows user to update Google Maps API key and Razorpay keys dynamically."""
    import os
    if req.google_maps_api_key is not None:
        settings.GOOGLE_MAPS_API_KEY = req.google_maps_api_key.strip()
    if req.google_maps_map_type is not None:
        settings.GOOGLE_MAPS_MAP_TYPE = req.google_maps_map_type.strip()
    if req.razorpay_key_id is not None:
        settings.RAZORPAY_KEY_ID = req.razorpay_key_id.strip()
    if req.razorpay_key_secret is not None:
        settings.RAZORPAY_KEY_SECRET = req.razorpay_key_secret.strip()

    # Persist updated keys to .env so changes survive restarts
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith("GOOGLE_MAPS_API_KEY=") and req.google_maps_api_key is not None:
                    new_lines.append(f"GOOGLE_MAPS_API_KEY={settings.GOOGLE_MAPS_API_KEY}\n")
                elif line.startswith("GOOGLE_MAPS_MAP_TYPE=") and req.google_maps_map_type is not None:
                    new_lines.append(f"GOOGLE_MAPS_MAP_TYPE={settings.GOOGLE_MAPS_MAP_TYPE}\n")
                elif line.startswith("RAZORPAY_KEY_ID=") and req.razorpay_key_id is not None:
                    new_lines.append(f"RAZORPAY_KEY_ID={settings.RAZORPAY_KEY_ID}\n")
                elif line.startswith("RAZORPAY_KEY_SECRET=") and req.razorpay_key_secret is not None:
                    new_lines.append(f"RAZORPAY_KEY_SECRET={settings.RAZORPAY_KEY_SECRET}\n")
                else:
                    new_lines.append(line)
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
    except Exception as e:
        print(f"Could not persist keys to .env: {e}")

    return ApiConfigResponse(
        google_maps_api_key=settings.GOOGLE_MAPS_API_KEY,
        google_maps_map_type=settings.GOOGLE_MAPS_MAP_TYPE,
        razorpay_key_id=settings.RAZORPAY_KEY_ID,
        razorpay_currency=settings.RAZORPAY_CURRENCY,
        merchant_name=settings.MERCHANT_NAME
    )
