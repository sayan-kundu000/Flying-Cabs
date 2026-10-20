import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_auth_session():
    response = client.post("/api/auth/session")
    assert response.status_code == 200
    user = response.json()
    assert user["role"] == "rider"
    assert user["name"] == "Aarav Sharma"

def test_nearby_drivers():
    response = client.get("/api/drivers/nearby?lat=12.9716&lng=77.5946&radius_km=30")
    assert response.status_code == 200
    drivers = response.json()
    assert len(drivers) > 0
    assert any(d["vehicle_type"] == "flying" for d in drivers)

def test_fare_estimate():
    # MG Road to KIA Airport
    response = client.get("/api/rides/estimate?origin_lat=12.9716&origin_lng=77.5946&dest_lat=13.1986&dest_lng=77.7066")
    assert response.status_code == 200
    data = response.json()
    assert data["distance_km"] > 0
    assert len(data["options"]) >= 3
    tiers = [o["tier_id"] for o in data["options"]]
    assert "flying" in tiers
    assert "standard" in tiers
    assert "luxury" in tiers

def test_ride_lifecycle():
    # 1. Request Ride (auto_simulate=False for controlled manual test)
    req_payload = {
        "rider_id": 1,
        "pickup_name": "MG Road Skydeck Helipad",
        "pickup_lat": 12.9716,
        "pickup_lng": 77.5946,
        "drop_name": "Kempegowda International Airport (BLR)",
        "drop_lat": 13.1986,
        "drop_lng": 77.7066,
        "vehicle_type": "flying",
        "fare_estimate": 1499.00,
        "distance_km": 34.5,
        "duration_mins": 14.0
    }
    create_res = client.post("/api/rides/request?auto_simulate=false", json=req_payload)
    assert create_res.status_code == 200
    ride = create_res.json()
    ride_id = ride["id"]
    assert ride["status"] == "REQUESTED"

    # 2. Get status
    status_res = client.get(f"/api/rides/{ride_id}/status")
    assert status_res.status_code == 200
    assert status_res.json()["id"] == ride_id

    # 3. Accept Ride
    accept_res = client.post(f"/api/rides/{ride_id}/accept?driver_id=1")
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "ACCEPTED"

    # 4. Update status to ARRIVED
    arrived_res = client.post(f"/api/rides/{ride_id}/update-status", json={"status": "ARRIVED"})
    assert arrived_res.status_code == 200
    assert arrived_res.json()["status"] == "ARRIVED"

    # 5. Update status to IN_PROGRESS
    in_prog_res = client.post(f"/api/rides/{ride_id}/update-status", json={"status": "IN_PROGRESS"})
    assert in_prog_res.status_code == 200
    assert in_prog_res.json()["status"] == "IN_PROGRESS"

    # 6. Complete Ride
    comp_res = client.post(f"/api/rides/{ride_id}/update-status", json={"status": "COMPLETED"})
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "COMPLETED"

    # 7. Pay Ride
    pay_res = client.post(f"/api/rides/{ride_id}/pay", json={"amount": 1499.00, "payment_method": "UPI (Google Pay)"})
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "succeeded"

    # 8. Review Ride
    rev_res = client.post(f"/api/rides/{ride_id}/review", json={"rating": 5, "comment": "Smooth flight, skipped entire Outer Ring Road traffic!"})
    assert rev_res.status_code == 200
    assert rev_res.json()["rating"] == 5

    # 9. Get Receipt
    rcp_res = client.get(f"/api/rides/{ride_id}/receipt")
    assert rcp_res.status_code == 200
    rcp = rcp_res.json()
    assert rcp["receipt_number"].startswith("BLR-SKY-")
    assert rcp["breakdown"]["total"] == 1499.00

def test_ride_history():
    hist_res = client.get("/api/rides/history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert isinstance(history, list)



def test_razorpay_config():
    response = client.get("/api/rides/razorpay/config")
    assert response.status_code == 200
    data = response.json()
    assert "key_id" in data
    assert data["currency"] == "INR"
    assert "name" in data

def test_razorpay_order_and_verify():
    # 1. Create a ride to pay
    req_payload = {
        "rider_id": 1,
        "pickup_name": "Indiranagar Skydeck",
        "pickup_lat": 12.9780,
        "pickup_lng": 77.6400,
        "drop_name": "Electronic City Phase 1 Skyport",
        "drop_lat": 12.8452,
        "drop_lng": 77.6602,
        "vehicle_type": "flying",
        "fare_estimate": 1250.00,
        "distance_km": 18.2,
        "duration_mins": 9.0
    }
    create_res = client.post("/api/rides/request?auto_simulate=false", json=req_payload)
    assert create_res.status_code == 200
    ride = create_res.json()
    ride_id = ride["id"]

    # 2. Create Razorpay order
    order_res = client.post(f"/api/rides/{ride_id}/razorpay/create-order", json={"amount": 1250.00, "tip": 50.0})
    assert order_res.status_code == 200
    order_data = order_res.json()
    assert "order_id" in order_data
    assert order_data["amount"] == 130000  # 1300.00 INR in paise
    assert order_data["currency"] == "INR"

    # 3. Verify Razorpay payment
    verify_payload = {
        "razorpay_order_id": order_data["order_id"],
        "razorpay_payment_id": "pay_test_rzp123456789",
        "razorpay_signature": "mock_signature_test",
        "amount": 1300.00,
        "payment_method": "Razorpay (UPI / Google Pay)"
    }
    verify_res = client.post(f"/api/rides/{ride_id}/razorpay/verify", json=verify_payload)
    assert verify_res.status_code == 200
    payment_data = verify_res.json()
    assert payment_data["status"] == "succeeded"
    assert payment_data["razorpay_payment_id"] == "pay_test_rzp123456789"
    assert payment_data["amount"] == 1300.00

    # 4. Check Receipt
    receipt_res = client.get(f"/api/rides/{ride_id}/receipt")
    assert receipt_res.status_code == 200
    rcpt = receipt_res.json()
    assert rcpt["payment"]["status"] == "succeeded"
    assert rcpt["payment"]["intent_id"] == "pay_test_rzp123456789"

def test_api_config_keys():
    # Test reading API keys for Google Maps and Razorpay
    res = client.get("/api/rides/config/keys")
    assert res.status_code == 200
    data = res.json()
    assert "google_maps_api_key" in data
    assert "razorpay_key_id" in data
    assert data["razorpay_key_id"].startswith("rzp_test_")

def test_pan_india_fleet():
    # Whole India search (large radius)
    res = client.get("/api/drivers/nearby?radius_km=2500")
    assert res.status_code == 200
    drivers = res.json()
    assert len(drivers) >= 4
    # Check that multiple vehicle types are present (e.g. auto, standard, flying)
    vehicle_types = set(d["vehicle_type"] for d in drivers)
    assert "flying" in vehicle_types
    assert "standard" in vehicle_types

def test_ride_otp():
    # Verify 4-digit ride OTP is created
    req_payload = {
        "rider_id": 1,
        "pickup_name": "Connaught Place, New Delhi",
        "pickup_lat": 28.6304,
        "pickup_lng": 77.2177,
        "drop_name": "Cyber City, Gurugram",
        "drop_lat": 28.4952,
        "drop_lng": 77.0890,
        "vehicle_type": "auto",
        "fare_estimate": 240.00,
        "distance_km": 24.5,
        "duration_mins": 45.0
    }
    create_res = client.post("/api/rides/request?auto_simulate=false", json=req_payload)
    assert create_res.status_code == 200
    ride = create_res.json()
    assert "otp" in ride
    assert len(ride["otp"]) == 4

def test_register_and_login():
    import uuid
    rand_email = f"user_{uuid.uuid4().hex[:8]}@aerocabs.in"
    # 1. Register new user
    reg_payload = {
        "name": "Priya Sharma",
        "email": rand_email,
        "phone": "+91 99887 76655",
        "password": "Password123!",
        "role": "rider",
        "profile_pic": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    auth_data = reg_res.json()
    assert "token" in auth_data
    assert auth_data["user"]["name"] == "Priya Sharma"

    # 2. Login with credentials
    login_res = client.post("/api/auth/login", json={
        "email_or_phone": rand_email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["user"]["email"] == rand_email

    # 3. Quick-switch to demo pilot
    switch_res = client.post("/api/auth/quick-switch/2")
    assert switch_res.status_code == 200
    assert "token" in switch_res.json()

def test_curated_avatars():
    res = client.get("/api/auth/avatars")
    assert res.status_code == 200
    avatars = res.json()
    assert len(avatars) >= 6
    assert any(a["name"] == "Priya Sharma" for a in avatars)
    assert any(a["name"] == "Capt. Vikram Rathore" for a in avatars)

def test_location_search_and_reverse():
    # 1. Search for airport
    search_res = client.get("/api/locations/search?q=airport&city=delhi")
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) > 0
    assert any("Airport" in r["name"] for r in results)

    # 2. Search for landmark
    cp_res = client.get("/api/locations/search?q=connaught")
    assert cp_res.status_code == 200
    cp_results = cp_res.json()
    assert len(cp_results) > 0
    assert "Connaught Place" in cp_results[0]["name"]

    # 3. Reverse geocode coordinates
    rev_res = client.get("/api/locations/reverse?lat=12.9756&lng=77.6066")
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert "name" in rev_data
    assert "MG Road" in rev_data["name"]

    # 4. Hotspots for a city
    hotspots_res = client.get("/api/locations/hotspots?city=mumbai")
    assert hotspots_res.status_code == 200
    hotspots = hotspots_res.json()
    assert len(hotspots) > 0

def test_pincode_search_and_endpoint():
    # 1. Search by Bengaluru PIN Code
    res_560001 = client.get("/api/locations/search?q=560001")
    assert res_560001.status_code == 200
    items_560001 = res_560001.json()
    assert len(items_560001) > 0
    assert items_560001[0]["category"] == "pincode"
    assert "560001" in items_560001[0]["name"]
    assert items_560001[0]["lat"] == pytest.approx(12.9797, 0.05)

    # 2. Search by Delhi PIN Code
    res_110001 = client.get("/api/locations/search?q=110001")
    assert res_110001.status_code == 200
    items_110001 = res_110001.json()
    assert len(items_110001) > 0
    assert "110001" in items_110001[0]["name"]

    # 3. Direct PIN code endpoint
    pin_res = client.get("/api/locations/pincode/400001")
    assert pin_res.status_code == 200
    pin_data = pin_res.json()
    assert pin_data["pincode"] == "400001"
    assert "Mumbai" in pin_data["sub"] or "Mumbai" in pin_data["name"]
    assert pin_data["lat"] == pytest.approx(18.9400, 0.05)

    # 4. Invalid PIN code handling
    bad_pin = client.get("/api/locations/pincode/999")
    assert bad_pin.status_code == 400




