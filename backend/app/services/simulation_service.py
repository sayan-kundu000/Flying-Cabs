import asyncio
import logging
from datetime import datetime, timezone
from backend.app.database import SessionLocal
from backend.app.models import Ride, Driver, Payment
from backend.app.services.websocket_manager import ws_manager

logger = logging.getLogger("flying_cabs.simulation")

active_simulation_tasks = {}

def interpolate(p1: float, p2: float, t: float) -> float:
    return p1 + (p2 - p1) * t

async def simulate_ride_lifecycle(ride_id: int):
    """
    Simulates a full ride lifecycle with realistic GPS movement updates:
    1. Driver Acceptance (after 2s)
    2. Driver moving towards pickup (waypoints pushed via WebSockets)
    3. Driver Arrival (status -> ARRIVED)
    4. Ride Starts (status -> IN_PROGRESS)
    5. Vehicle moving from pickup to destination
    6. Ride Complete (status -> COMPLETED)
    """
    logger.info(f"Starting auto-simulation for Ride {ride_id}")
    
    # Wait 2 seconds before driver accepts
    await asyncio.sleep(2.0)
    
    db = SessionLocal()
    try:
        ride = db.query(Ride).filter(Ride.id == ride_id).first()
        if not ride or ride.status != "REQUESTED":
            return

        driver = None
        # 1. Match specific chosen car model if provided
        if getattr(ride, "car_model", None):
            first_word = ride.car_model.split()[0]
            driver = db.query(Driver).filter(
                Driver.vehicle_info.like(f"%{first_word}%"),
                Driver.status == "active"
            ).first()

        # 2. Find matching available driver by vehicle_type
        if not driver:
            driver = db.query(Driver).filter(
                Driver.vehicle_type == ride.vehicle_type,
                Driver.status == "active"
            ).first()

        if not driver:
            # Fallback to any active driver
            driver = db.query(Driver).filter(Driver.status == "active").first()

        if not driver:
            # Pick any driver
            driver = db.query(Driver).first()

        if driver:
            ride.driver_id = driver.id
            ride.status = "ACCEPTED"
            ride.accepted_at = datetime.now(timezone.utc)
            driver.status = "busy"
            db.commit()
            db.refresh(ride)
            db.refresh(driver)

            driver_info = {
                "id": driver.id,
                "name": driver.user.name if driver.user else "Pilot Alex",
                "phone": driver.user.phone if driver.user else "+91 98450 11007",
                "profile_pic": driver.user.profile_pic if driver.user else "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
                "vehicle_info": driver.vehicle_info,
                "vehicle_type": driver.vehicle_type,
                "vehicle_image": getattr(driver, "vehicle_image", None) or "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80",
                "license_plate": driver.license_plate,
                "rating_avg": driver.user.rating_avg if driver.user else 4.9,
                "current_lat": driver.current_lat,
                "current_lng": driver.current_lng,
                "altitude_m": driver.altitude_m,
                "battery_pct": driver.battery_pct
            }

            # Notify rider and map
            await ws_manager.send_to_rider(ride.rider_id, "RIDE_ACCEPTED", {
                "ride_id": ride.id,
                "status": "ACCEPTED",
                "otp": ride.otp,
                "driver": driver_info
            })
            await ws_manager.broadcast_to_map("RIDE_UPDATED", {
                "ride_id": ride.id,
                "status": "ACCEPTED",
                "otp": ride.otp,
                "driver_id": driver.id
            })

            # Stage 1: Driver moves towards pickup
            start_lat = driver.current_lat
            start_lng = driver.current_lng
            target_lat = ride.pickup_lat
            target_lng = ride.pickup_lng

            steps = 6
            for step in range(1, steps + 1):
                await asyncio.sleep(1.2)
                db.refresh(ride)
                if ride.status == "CANCELLED":
                    logger.info(f"Ride {ride_id} was cancelled during pickup dispatch.")
                    driver.status = "active"
                    db.commit()
                    return

                t = step / steps
                curr_lat = interpolate(start_lat, target_lat, t)
                curr_lng = interpolate(start_lng, target_lng, t)
                driver.current_lat = curr_lat
                driver.current_lng = curr_lng
                db.commit()

                movement_data = {
                    "ride_id": ride.id,
                    "driver_id": driver.id,
                    "lat": curr_lat,
                    "lng": curr_lng,
                    "altitude_m": driver.altitude_m,
                    "step": step,
                    "heading_to": "pickup"
                }
                await ws_manager.send_to_rider(ride.rider_id, "DRIVER_LOCATION_UPDATE", movement_data)
                await ws_manager.broadcast_fleet_location(driver.id, curr_lat, curr_lng, driver.altitude_m, driver.status)

            # Stage 2: Driver Arrives at Pickup
            await asyncio.sleep(1.0)
            db.refresh(ride)
            if ride.status == "CANCELLED":
                driver.status = "active"
                db.commit()
                return

            ride.status = "ARRIVED"
            db.commit()
            await ws_manager.send_to_rider(ride.rider_id, "DRIVER_ARRIVED", {
                "ride_id": ride.id,
                "status": "ARRIVED",
                "message": f"{driver.vehicle_info} has arrived at {ride.pickup_name}!"
            })

            # Stage 3: Ride Starts (In Progress)
            await asyncio.sleep(2.0)
            db.refresh(ride)
            if ride.status == "CANCELLED":
                driver.status = "active"
                db.commit()
                return

            ride.status = "IN_PROGRESS"
            db.commit()
            await ws_manager.send_to_rider(ride.rider_id, "RIDE_STARTED", {
                "ride_id": ride.id,
                "status": "IN_PROGRESS",
                "message": "Flight launched! Heading towards your destination."
            })

            # Stage 4: Vehicle moves from pickup to destination
            dest_lat = ride.drop_lat
            dest_lng = ride.drop_lng
            transit_steps = 8
            for step in range(1, transit_steps + 1):
                await asyncio.sleep(1.2)
                db.refresh(ride)
                if ride.status == "CANCELLED":
                    logger.info(f"Ride {ride_id} was cancelled in transit.")
                    driver.status = "active"
                    db.commit()
                    return

                t = step / transit_steps
                curr_lat = interpolate(target_lat, dest_lat, t)
                curr_lng = interpolate(target_lng, dest_lng, t)
                driver.current_lat = curr_lat
                driver.current_lng = curr_lng
                db.commit()

                movement_data = {
                    "ride_id": ride.id,
                    "driver_id": driver.id,
                    "lat": curr_lat,
                    "lng": curr_lng,
                    "altitude_m": driver.altitude_m + (20 if step < transit_steps else 0),
                    "step": step,
                    "heading_to": "destination"
                }
                await ws_manager.send_to_rider(ride.rider_id, "DRIVER_LOCATION_UPDATE", movement_data)
                await ws_manager.broadcast_fleet_location(driver.id, curr_lat, curr_lng, driver.altitude_m, driver.status)

            # Stage 5: Ride Completed
            await asyncio.sleep(1.0)
            db.refresh(ride)
            if ride.status == "CANCELLED":
                driver.status = "active"
                db.commit()
                return

            ride.status = "COMPLETED"
            ride.completed_at = datetime.now(timezone.utc)
            ride.fare_actual = ride.fare_estimate
            driver.status = "active"
            driver.total_trips += 1
            driver.earnings_today += ride.fare_actual
            db.commit()

            completion_data = {
                "ride_id": ride.id,
                "status": "COMPLETED",
                "fare": ride.fare_actual,
                "drop_name": ride.drop_name,
                "message": "You have safely arrived at your destination!"
            }
            await ws_manager.send_to_rider(ride.rider_id, "RIDE_COMPLETED", completion_data)
            await ws_manager.broadcast_to_map("RIDE_COMPLETED", completion_data)
            await ws_manager.broadcast_fleet_location(driver.id, dest_lat, dest_lng, driver.altitude_m, "active")

    except asyncio.CancelledError:
        logger.info(f"Auto-simulation for ride {ride_id} was explicitly cancelled.")
        try:
            cleanup_db = SessionLocal()
            r = cleanup_db.query(Ride).filter(Ride.id == ride_id).first()
            if r and r.driver_id:
                d = cleanup_db.query(Driver).filter(Driver.id == r.driver_id).first()
                if d and d.status == "busy":
                    d.status = "active"
                    cleanup_db.commit()
            cleanup_db.close()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error in ride simulation: {e}")
    finally:
        db.close()
        if ride_id in active_simulation_tasks:
            del active_simulation_tasks[ride_id]

def start_simulation(ride_id: int):
    # Cancel previous task if one exists for the same ride
    cancel_simulation(ride_id)
    task = asyncio.create_task(simulate_ride_lifecycle(ride_id))
    active_simulation_tasks[ride_id] = task
    return task

def cancel_simulation(ride_id: int):
    task = active_simulation_tasks.get(ride_id)
    if task and not task.done():
        task.cancel()
    if ride_id in active_simulation_tasks:
        del active_simulation_tasks[ride_id]
