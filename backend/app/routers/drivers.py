from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models import Driver, User, Ride
from backend.app.schemas import DriverResponse, DriverLocationUpdate, DriverStatusUpdate
from backend.app.services.fare_calculator import haversine_distance
from backend.app.services.websocket_manager import ws_manager

router = APIRouter(prefix="/drivers", tags=["drivers"])

@router.get("/nearby", response_model=List[DriverResponse])
def get_nearby_drivers(
    lat: float = Query(22.8046, description="Current latitude (defaults to Jamshedpur)"),
    lng: float = Query(86.2029, description="Current longitude (defaults to Jamshedpur)"),
    radius_km: float = Query(35.0, description="Search radius in kilometers"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type: standard, flying, luxury"),
    db: Session = Depends(get_db)
):
    """
    Returns nearby available drivers within radius_km.
    Uses geospatial distance calculation with automatic fleet distribution near rider's GPS location.
    """
    base_query = db.query(Driver).filter(Driver.status.in_(["active", "busy"]))
    if vehicle_type:
        typed_drivers = base_query.filter(Driver.vehicle_type == vehicle_type).all()
        all_drivers = typed_drivers if typed_drivers else base_query.all()
    else:
        all_drivers = base_query.all()
    # Whole India Map overview: return all drivers across India
    if radius_km >= 1000.0:
        return all_drivers

    nearby = []
    for d in all_drivers:
        dist = haversine_distance(lat, lng, d.current_lat, d.current_lng)
        if dist <= radius_km:
            nearby.append(d)

    # Dynamic auto-distribution: If no drivers are within search radius, position available fleet around user's GPS
    if len(nearby) == 0 and len(all_drivers) > 0:
        offsets = [
            (0.0085, -0.0075),
            (-0.0060, 0.0090),
            (0.0110, 0.0045),
            (-0.0095, -0.0060)
        ]
        for idx, d in enumerate(all_drivers):
            ox, oy = offsets[idx % len(offsets)]
            d.current_lat = lat + ox
            d.current_lng = lng + oy
            db.commit()
            nearby.append(d)

    return nearby

@router.get("/{driver_id}/dashboard")
def get_driver_dashboard(driver_id: int, db: Session = Depends(get_db)):
    """Fetch driver profile, earnings, active rides, and status."""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    active_ride = db.query(Ride).filter(
        Ride.driver_id == driver.id,
        Ride.status.in_(["ACCEPTED", "ARRIVED", "IN_PROGRESS"])
    ).first()

    pending_requests = []
    if driver.status == "active":
        pending_requests = db.query(Ride).filter(
            Ride.status == "REQUESTED",
            Ride.vehicle_type == driver.vehicle_type
        ).all()

    return {
        "driver": {
            "id": driver.id,
            "name": driver.user.name,
            "vehicle_info": driver.vehicle_info,
            "vehicle_type": driver.vehicle_type,
            "license_plate": driver.license_plate,
            "status": driver.status,
            "rating_avg": driver.user.rating_avg,
            "earnings_today": driver.earnings_today,
            "total_trips": driver.total_trips,
            "battery_pct": driver.battery_pct,
            "altitude_m": driver.altitude_m,
            "current_lat": driver.current_lat,
            "current_lng": driver.current_lng
        },
        "active_ride": active_ride,
        "pending_requests": pending_requests
    }

@router.post("/{driver_id}/location")
async def update_driver_location(
    driver_id: int,
    loc: DriverLocationUpdate,
    db: Session = Depends(get_db)
):
    """Driver publishes location updates."""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.current_lat = loc.current_lat
    driver.current_lng = loc.current_lng
    if loc.altitude_m is not None:
        driver.altitude_m = loc.altitude_m
    if loc.battery_pct is not None:
        driver.battery_pct = loc.battery_pct

    db.commit()

    # Broadcast to live map and active rider (if on trip)
    await ws_manager.broadcast_fleet_location(
        driver.id, driver.current_lat, driver.current_lng, driver.altitude_m, driver.status
    )
    return {"status": "ok", "driver_id": driver.id}

@router.post("/{driver_id}/status")
async def update_driver_status(
    driver_id: int,
    status_update: DriverStatusUpdate,
    db: Session = Depends(get_db)
):
    """Toggle driver availability (active / offline)."""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.status = status_update.status
    db.commit()

    await ws_manager.broadcast_to_map("DRIVER_STATUS_CHANGE", {
        "driver_id": driver.id,
        "status": driver.status
    })
    return {"status": "ok", "new_status": driver.status}
