import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, Driver
from backend.app.routers import auth, rides, drivers, payments, locations
from backend.app.services.websocket_manager import ws_manager

import threading

_seed_lock = threading.Lock()
_seeded = False

def seed_initial_data():
    """Initializes tables and seeds demo users & drivers if DB is empty."""
    global _seeded
    with _seed_lock:
        if _seeded:
            return
        Base.metadata.create_all(bind=engine)
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                # 1. Migration for payments table
                res = conn.execute(text("PRAGMA table_info(payments)"))
                existing_cols = [r[1] for r in res.fetchall()]
                for col, col_type in [("razorpay_order_id", "VARCHAR(100)"), ("razorpay_payment_id", "VARCHAR(100)"), ("razorpay_signature", "VARCHAR(255)")]:
                    if col not in existing_cols:
                        conn.execute(text(f"ALTER TABLE payments ADD COLUMN {col} {col_type}"))

                # 2. Migration for rides table (Ola & Uber OTP, Payment Mode, Car Model)
                res_rides = conn.execute(text("PRAGMA table_info(rides)"))
                existing_ride_cols = [r[1] for r in res_rides.fetchall()]
                for col, col_type in [("otp", "VARCHAR(10)"), ("payment_mode", "VARCHAR(50)"), ("car_model", "VARCHAR(120)")]:
                    if col not in existing_ride_cols:
                        conn.execute(text(f"ALTER TABLE rides ADD COLUMN {col} {col_type}"))

                # 3. Migration for users table (Authentication password hash)
                res_users = conn.execute(text("PRAGMA table_info(users)"))
                existing_user_cols = [r[1] for r in res_users.fetchall()]
                if "password_hash" not in existing_user_cols:
                    conn.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))

                # 4. Migration for drivers table (Car visual image)
                res_drivers = conn.execute(text("PRAGMA table_info(drivers)"))
                existing_driver_cols = [r[1] for r in res_drivers.fetchall()]
                if "vehicle_image" not in existing_driver_cols:
                    conn.execute(text("ALTER TABLE drivers ADD COLUMN vehicle_image VARCHAR(255)"))

                conn.commit()
        except Exception as e:
            print(f"Migration note: {e}")

        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            if user_count == 0:
                print("--- Seeding initial demo data for Flying Cabs (India Fleet) ---")
                # 1. Primary Rider (Passenger)
                rider = User(
                    name="Aarav Sharma",
                    email="aarav.sharma@aerocabs.in",
                    phone="+91 98765 43210",
                    role="rider",
                    profile_pic="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
                    rating_avg=4.95
                )
                db.add(rider)
                db.commit()

            # Fleet of pilots, cab drivers, auto drivers, luxury chauffeurs, and bike riders across India
            pan_india_drivers = [
                # Bengaluru
                {
                    "name": "Capt. Vikram Rathore",
                    "email": "vikram.rathore@aerocabs.in",
                    "phone": "+91 98450 11007",
                    "vehicle_info": "AeroVTOL Sky-X7 (Air Garuda)",
                    "vehicle_type": "flying",
                    "profile_pic": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "KA-01-AERO-007",
                    "lat": 12.9780, "lng": 77.6400, "altitude_m": 160.0,
                    "battery_pct": 98, "earnings_today": 4850.00, "total_trips": 328
                },
                {
                    "name": "Rajesh Kumar",
                    "email": "rajesh.kumar@aerocabs.in",
                    "phone": "+91 99800 22441",
                    "vehicle_info": "Tata Tigor EV Prime",
                    "vehicle_type": "standard",
                    "profile_pic": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "KA-05-EV-4242",
                    "lat": 12.9170, "lng": 77.6220, "altitude_m": 0.0,
                    "battery_pct": 86, "earnings_today": 2450.00, "total_trips": 540
                },
                {
                    "name": "Manjunath Gowda",
                    "email": "manju.gowda@aerocabs.in",
                    "phone": "+91 98440 33221",
                    "vehicle_info": "Bajaj RE EV Auto (Green-Yellow)",
                    "vehicle_type": "auto",
                    "profile_pic": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "KA-02-AU-7711",
                    "lat": 12.9716, "lng": 77.5946, "altitude_m": 0.0,
                    "battery_pct": 90, "earnings_today": 1250.00, "total_trips": 890
                },
                {
                    "name": "Kavita Reddy",
                    "email": "kavita.reddy@aerocabs.in",
                    "phone": "+91 98455 66778",
                    "vehicle_info": "Mercedes-Benz E-Class Prime",
                    "vehicle_type": "luxury",
                    "profile_pic": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "KA-03-PRIME-101",
                    "lat": 12.9756, "lng": 77.6066, "altitude_m": 0.0,
                    "battery_pct": 94, "earnings_today": 5400.00, "total_trips": 210
                },
                {
                    "name": "Sunil Gowda",
                    "email": "sunil.gowda@aerocabs.in",
                    "phone": "+91 98451 99001",
                    "vehicle_info": "Ather 450X EV Bike Taxi",
                    "vehicle_type": "bike",
                    "profile_pic": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "KA-01-BK-8899",
                    "lat": 12.9720, "lng": 77.6350, "altitude_m": 0.0,
                    "battery_pct": 92, "earnings_today": 980.00, "total_trips": 680
                },
                {
                    "name": "Deepak Rao",
                    "email": "deepak.rao@aerocabs.in",
                    "phone": "+91 98452 44332",
                    "vehicle_info": "Maruti WagonR Compact AC",
                    "vehicle_type": "micro",
                    "profile_pic": "https://images.unsplash.com/photo-1528892952291-009c663ce843?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "KA-04-MC-3344",
                    "lat": 12.9350, "lng": 77.6150, "altitude_m": 0.0,
                    "battery_pct": 89, "earnings_today": 1650.00, "total_trips": 470
                },
                # Delhi NCR
                {
                    "name": "Capt. Harpreet Singh",
                    "email": "harpreet.singh@aerocabs.in",
                    "phone": "+91 98110 55432",
                    "vehicle_info": "Volocopter Horizon 4 (Indra-Air)",
                    "vehicle_type": "flying",
                    "profile_pic": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "DL-01-SKY-909",
                    "lat": 28.5562, "lng": 77.1000, "altitude_m": 175.0, # IGI Airport
                    "battery_pct": 94, "earnings_today": 5600.00, "total_trips": 412
                },
                {
                    "name": "Ramesh Verma",
                    "email": "ramesh.verma@aerocabs.in",
                    "phone": "+91 98102 33445",
                    "vehicle_info": "Maruti Swift Dzire ZXi",
                    "vehicle_type": "standard",
                    "profile_pic": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "DL-03-CAB-4421",
                    "lat": 28.6304, "lng": 77.2177, "altitude_m": 0.0, # Connaught Place
                    "battery_pct": 89, "earnings_today": 3100.00, "total_trips": 720
                },
                {
                    "name": "Joginder Singh",
                    "email": "joginder.singh@aerocabs.in",
                    "phone": "+91 98188 99112",
                    "vehicle_info": "Mahindra Treo Electric Auto",
                    "vehicle_type": "auto",
                    "profile_pic": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "DL-04-AU-8821",
                    "lat": 28.6139, "lng": 77.2090, "altitude_m": 0.0,
                    "battery_pct": 91, "earnings_today": 1640.00, "total_trips": 990
                },
                {
                    "name": "Vikramjeet Malhotra",
                    "email": "vikramjeet.m@aerocabs.in",
                    "phone": "+91 98111 22334",
                    "vehicle_info": "BMW 5-Series Executive Cruiser",
                    "vehicle_type": "luxury",
                    "profile_pic": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "DL-01-PRIME-001",
                    "lat": 28.4952, "lng": 77.0890, "altitude_m": 0.0, # Cyber City
                    "battery_pct": 96, "earnings_today": 6200.00, "total_trips": 195
                },
                {
                    "name": "Sanjay Yadav",
                    "email": "sanjay.yadav@aerocabs.in",
                    "phone": "+91 98112 55667",
                    "vehicle_info": "Ola S1 Pro Gen2 Bike Taxi",
                    "vehicle_type": "bike",
                    "profile_pic": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "DL-08-BK-7722",
                    "lat": 28.6250, "lng": 77.2150, "altitude_m": 0.0,
                    "battery_pct": 93, "earnings_today": 1120.00, "total_trips": 750
                },
                {
                    "name": "Mohd. Irfan",
                    "email": "mohd.irfan@aerocabs.in",
                    "phone": "+91 98103 44556",
                    "vehicle_info": "Tata Tiago EV Micro",
                    "vehicle_type": "micro",
                    "profile_pic": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "DL-02-MC-5566",
                    "lat": 28.5708, "lng": 77.3261, "altitude_m": 0.0, # Noida
                    "battery_pct": 88, "earnings_today": 1820.00, "total_trips": 510
                },
                # Mumbai
                {
                    "name": "Capt. Aditya Patil",
                    "email": "aditya.patil@aerocabs.in",
                    "phone": "+91 98200 44556",
                    "vehicle_info": "AeroVTOL Sky-X7 (Sea Breeze)",
                    "vehicle_type": "flying",
                    "profile_pic": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "MH-01-AERO-009",
                    "lat": 19.0760, "lng": 72.8777, "altitude_m": 150.0, # BKC
                    "battery_pct": 96, "earnings_today": 6800.00, "total_trips": 290
                },
                {
                    "name": "Sandeep Salvi",
                    "email": "sandeep.salvi@aerocabs.in",
                    "phone": "+91 98211 77889",
                    "vehicle_info": "Toyota Etios AC Sedan",
                    "vehicle_type": "standard",
                    "profile_pic": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "MH-02-CAB-1100",
                    "lat": 18.9220, "lng": 72.8346, "altitude_m": 0.0, # Nariman Point
                    "battery_pct": 92, "earnings_today": 2800.00, "total_trips": 650
                },
                {
                    "name": "Ganesh Shinde",
                    "email": "ganesh.shinde@aerocabs.in",
                    "phone": "+91 98205 33441",
                    "vehicle_info": "Bajaj Compact RE Auto",
                    "vehicle_type": "auto",
                    "profile_pic": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "MH-02-AU-3311",
                    "lat": 19.0657, "lng": 72.8687, "altitude_m": 0.0,
                    "battery_pct": 91, "earnings_today": 1450.00, "total_trips": 820
                },
                {
                    "name": "Rohan D'Souza",
                    "email": "rohan.dsouza@aerocabs.in",
                    "phone": "+91 98201 99887",
                    "vehicle_info": "Audi A6 Luxury Limousine",
                    "vehicle_type": "luxury",
                    "profile_pic": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "MH-01-LUX-777",
                    "lat": 19.0607, "lng": 72.8362, "altitude_m": 0.0, # Bandra
                    "battery_pct": 97, "earnings_today": 7100.00, "total_trips": 160
                },
                {
                    "name": "Prashant Patil",
                    "email": "prashant.patil@aerocabs.in",
                    "phone": "+91 98209 88112",
                    "vehicle_info": "TVS iQube EV Bike Taxi",
                    "vehicle_type": "bike",
                    "profile_pic": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "MH-03-BK-1234",
                    "lat": 19.1176, "lng": 72.9060, "altitude_m": 0.0, # Powai
                    "battery_pct": 90, "earnings_today": 1050.00, "total_trips": 690
                },
                # Jamshedpur (Steel City)
                {
                    "name": "Capt. Arjun Tudu",
                    "email": "arjun.tudu@aerocabs.in",
                    "phone": "+91 94311 00223",
                    "vehicle_info": "AeroVTOL Sky-X7 (Steel Wing)",
                    "vehicle_type": "flying",
                    "profile_pic": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "JH-05-AERO-001",
                    "lat": 22.8133, "lng": 86.1685, "altitude_m": 140.0, # Sonari Airport
                    "battery_pct": 97, "earnings_today": 3950.00, "total_trips": 185
                },
                {
                    "name": "Amit Sharma",
                    "email": "amit.sharma@aerocabs.in",
                    "phone": "+91 94313 88990",
                    "vehicle_info": "Tata Punch EV Empowered",
                    "vehicle_type": "standard",
                    "profile_pic": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "JH-05-CAB-1234",
                    "lat": 22.8010, "lng": 86.1860, "altitude_m": 0.0, # Bistupur
                    "battery_pct": 88, "earnings_today": 1950.00, "total_trips": 430
                },
                {
                    "name": "Manoj Soren",
                    "email": "manoj.soren@aerocabs.in",
                    "phone": "+91 94315 22114",
                    "vehicle_info": "Piaggio Ape E-City Auto",
                    "vehicle_type": "auto",
                    "profile_pic": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "JH-05-AU-2211",
                    "lat": 22.8080, "lng": 86.2030, "altitude_m": 0.0,
                    "battery_pct": 92, "earnings_today": 1180.00, "total_trips": 540
                },
                # Hyderabad
                {
                    "name": "Capt. Syed Farooq",
                    "email": "syed.farooq@aerocabs.in",
                    "phone": "+91 98490 12345",
                    "vehicle_info": "Volocopter Horizon 4 (Nizam Sky)",
                    "vehicle_type": "flying",
                    "profile_pic": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "TS-09-SKY-505",
                    "lat": 17.4483, "lng": 78.3915, "altitude_m": 165.0, # Hitech City
                    "battery_pct": 95, "earnings_today": 5100.00, "total_trips": 310
                },
                {
                    "name": "K. Srinivas Rao",
                    "email": "srinivas.rao@aerocabs.in",
                    "phone": "+91 98491 55667",
                    "vehicle_info": "Hyundai Aura CNG Sedan",
                    "vehicle_type": "standard",
                    "profile_pic": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "TS-07-CAB-9900",
                    "lat": 17.4399, "lng": 78.3489, "altitude_m": 0.0,
                    "battery_pct": 87, "earnings_today": 2600.00, "total_trips": 480
                },
                # Kolkata
                {
                    "name": "Capt. Subhashish Roy",
                    "email": "subhashish.roy@aerocabs.in",
                    "phone": "+91 98300 98765",
                    "vehicle_info": "AeroVTOL Sky-X7 (Ganga Air)",
                    "vehicle_type": "flying",
                    "profile_pic": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "WB-02-AERO-808",
                    "lat": 22.5726, "lng": 88.3639, "altitude_m": 155.0, # Park Street
                    "battery_pct": 93, "earnings_today": 4200.00, "total_trips": 275
                },
                {
                    "name": "Bapi Mukherjee",
                    "email": "bapi.mukherjee@aerocabs.in",
                    "phone": "+91 98302 44332",
                    "vehicle_info": "Bajaj RE Kolkata Green Auto",
                    "vehicle_type": "auto",
                    "profile_pic": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80",
                    "vehicle_image": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=500&auto=format&fit=crop&q=80",
                    "license_plate": "WB-01-AU-6655",
                    "lat": 22.5535, "lng": 88.3512, "altitude_m": 0.0,
                    "battery_pct": 89, "earnings_today": 1340.00, "total_trips": 710
                }
            ]

            import hashlib
            default_pwd = hashlib.sha256(b"flying_cabs_india_bharat_2026pilot123").hexdigest()

            for d in pan_india_drivers:
                face = d.get("profile_pic", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80")
                v_img = d.get("vehicle_image", "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80")

                existing_u = db.query(User).filter(User.email == d["email"]).first()
                if not existing_u:
                    u = User(
                        name=d["name"],
                        email=d["email"],
                        phone=d["phone"],
                        role="driver",
                        profile_pic=face,
                        password_hash=default_pwd,
                        rating_avg=4.94
                    )
                    db.add(u)
                    db.commit()
                    db.refresh(u)
                else:
                    u = existing_u
                    u.profile_pic = face
                    if not u.password_hash:
                        u.password_hash = default_pwd
                    db.commit()

                existing_drv = db.query(Driver).filter(Driver.user_id == u.id).first()
                if not existing_drv:
                    drv = Driver(
                        user_id=u.id,
                        vehicle_info=d["vehicle_info"],
                        vehicle_type=d["vehicle_type"],
                        vehicle_image=v_img,
                        license_plate=d["license_plate"],
                        verified=True,
                        current_lat=d["lat"],
                        current_lng=d["lng"],
                        altitude_m=d["altitude_m"],
                        battery_pct=d["battery_pct"],
                        status="active",
                        earnings_today=d["earnings_today"],
                        total_trips=d["total_trips"]
                    )
                    db.add(drv)
                    db.commit()
                else:
                    existing_drv.vehicle_image = v_img
                    existing_drv.vehicle_info = d["vehicle_info"]
                    db.commit()

            print("Nationwide driver fleet successfully verified & seeded with faces & car visuals!")
            _seeded = True
        finally:
            db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_data()
    yield

# Ensure tables and seed data are initialized immediately on import as well
seed_initial_data()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Full-stack Python ride-hailing platform with FastAPI, WebSockets, and Leaflet interactive map.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(rides.router, prefix=settings.API_V1_STR)
app.include_router(drivers.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(locations.router, prefix=settings.API_V1_STR)

# WebSockets
@app.websocket("/ws/rider/{rider_id}")
async def websocket_rider_endpoint(websocket: WebSocket, rider_id: int):
    await ws_manager.connect_rider(rider_id, websocket)
    try:
        while True:
            # Keep socket alive and receive any client ping/events
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_rider(rider_id, websocket)

@app.websocket("/ws/driver/{driver_id}")
async def websocket_driver_endpoint(websocket: WebSocket, driver_id: int):
    await ws_manager.connect_driver(driver_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_driver(driver_id, websocket)

@app.websocket("/ws/map")
async def websocket_map_endpoint(websocket: WebSocket):
    await ws_manager.connect_map(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect_map(websocket)

# Static Files & SPA Frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Flying Cabs API", "version": settings.PROJECT_VERSION}
