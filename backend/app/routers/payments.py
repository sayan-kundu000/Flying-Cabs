import uuid
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import razorpay

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models import Ride, Payment, Review, User
from backend.app.schemas import (
    RidePayRequest,
    RideReviewRequest,
    PaymentResponse,
    ReviewResponse,
    RazorpayConfigResponse,
    RazorpayOrderCreateRequest,
    RazorpayOrderResponse,
    RazorpayVerifyRequest
)
from backend.app.services.websocket_manager import ws_manager

router = APIRouter(prefix="/rides", tags=["payments & reviews"])

def get_razorpay_client():
    """Returns initialized Razorpay client."""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.get("/razorpay/config", response_model=RazorpayConfigResponse)
def get_razorpay_config():
    """
    Public Razorpay configuration for frontend SDK initialization.
    """
    return RazorpayConfigResponse(
        key_id=settings.RAZORPAY_KEY_ID,
        currency=settings.RAZORPAY_CURRENCY,
        name=settings.MERCHANT_NAME,
        theme_color="#0284c7"
    )

@router.post("/{ride_id}/razorpay/create-order", response_model=RazorpayOrderResponse)
def create_razorpay_order(
    ride_id: int,
    order_req: RazorpayOrderCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Creates an official Razorpay Order for the ride payment.
    Amount is converted to paise as required by Razorpay API.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    base_amount = order_req.amount or ride.fare_actual or ride.fare_estimate or 580.0
    total_amount = base_amount + (order_req.tip or 0.0)
    amount_in_paise = int(round(total_amount * 100))
    receipt_id = f"rcpt_ride_{ride_id}_{int(time.time())}"

    order_id = None
    is_live = False

    # Check if live/test Razorpay API credentials are configured
    has_valid_secret = (
        settings.RAZORPAY_KEY_SECRET 
        and not "mock" in settings.RAZORPAY_KEY_SECRET.lower()
        and not settings.RAZORPAY_KEY_SECRET.startswith("s9x4H8")
    )
    has_valid_key = (
        settings.RAZORPAY_KEY_ID 
        and not "mock" in settings.RAZORPAY_KEY_ID.lower()
        and settings.RAZORPAY_KEY_ID.startswith("rzp_")
        and not settings.RAZORPAY_KEY_ID.startswith("rzp_test_mock")
    )

    if has_valid_key and has_valid_secret:
        try:
            client = get_razorpay_client()
            rzp_order = client.order.create({
                "amount": amount_in_paise,
                "currency": settings.RAZORPAY_CURRENCY,
                "receipt": receipt_id,
                "notes": {
                    "ride_id": str(ride_id),
                    "pickup": (ride.pickup_name or "Pickup")[:40],
                    "drop": (ride.drop_name or "Destination")[:40],
                    "vehicle": ride.vehicle_type or "standard"
                }
            })
            order_id = rzp_order.get("id")
            if order_id:
                is_live = True
        except Exception:
            # Fallback to simulated order ID if Razorpay API call fails or is unreachable
            order_id = f"order_mock_{uuid.uuid4().hex[:14]}"
            is_live = False
    else:
        # Development / Sandbox mock order
        order_id = f"order_mock_{uuid.uuid4().hex[:14]}"
        is_live = False

    return RazorpayOrderResponse(
        order_id=order_id,
        amount=amount_in_paise,
        currency=settings.RAZORPAY_CURRENCY,
        key_id=settings.RAZORPAY_KEY_ID,
        ride_id=ride.id,
        receipt=receipt_id,
        is_live=is_live
    )

@router.post("/{ride_id}/razorpay/verify", response_model=PaymentResponse)
async def verify_razorpay_payment(
    ride_id: int,
    verify_req: RazorpayVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verifies Razorpay payment signature and records successful transaction.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    # Check if already paid
    existing_payment = db.query(Payment).filter(Payment.ride_id == ride_id).first()
    if existing_payment:
        return existing_payment

    # Signature verification if secret is configured and not in test/mock mode
    is_mock_mode = (
        not settings.RAZORPAY_KEY_SECRET or 
        "mock" in settings.RAZORPAY_KEY_SECRET.lower() or 
        settings.RAZORPAY_KEY_SECRET.startswith("s9x4H8") or
        verify_req.razorpay_order_id.startswith("order_mock_") or
        (verify_req.razorpay_signature and "mock" in verify_req.razorpay_signature.lower())
    )
    if not is_mock_mode and verify_req.razorpay_signature:
        try:
            client = get_razorpay_client()
            client.utility.verify_payment_signature({
                "razorpay_order_id": verify_req.razorpay_order_id,
                "razorpay_payment_id": verify_req.razorpay_payment_id,
                "razorpay_signature": verify_req.razorpay_signature
            })
        except Exception:
            raise HTTPException(status_code=400, detail="Razorpay signature verification failed")

    amount = verify_req.amount or ride.fare_actual or ride.fare_estimate or 580.0

    payment = Payment(
        ride_id=ride.id,
        stripe_payment_intent_id=verify_req.razorpay_payment_id,
        razorpay_order_id=verify_req.razorpay_order_id,
        razorpay_payment_id=verify_req.razorpay_payment_id,
        razorpay_signature=verify_req.razorpay_signature,
        amount=amount,
        currency="INR",
        status="succeeded",
        payment_method=verify_req.payment_method or "Razorpay (UPI / Card)",
        created_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Broadcast payment success event over WebSockets to rider and map
    await ws_manager.broadcast_ride_update(ride.id, {
        "event": "PAYMENT_CONFIRMED",
        "type": "PAYMENT_CONFIRMED",
        "ride_id": ride.id,
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "payment_id": payment.id,
        "razorpay_payment_id": payment.razorpay_payment_id,
        "amount": payment.amount,
        "status": "succeeded"
    })
    # Also explicitly push to rider socket
    await ws_manager.send_to_rider(ride.rider_id, "PAYMENT_CONFIRMED", {
        "ride_id": ride.id,
        "payment_id": payment.id,
        "razorpay_payment_id": payment.razorpay_payment_id,
        "amount": payment.amount,
        "status": "succeeded"
    })

    return payment

@router.post("/{ride_id}/pay", response_model=PaymentResponse)
async def process_payment(
    ride_id: int,
    pay_data: RidePayRequest,
    db: Session = Depends(get_db)
):
    """
    Standard / Direct payment recording in DB (supports UPI, Card, Wallets).
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    existing_payment = db.query(Payment).filter(Payment.ride_id == ride_id).first()
    if existing_payment:
        return existing_payment

    amount = pay_data.amount or ride.fare_actual or ride.fare_estimate or 580.0
    txn_id = f"rzp_pay_{uuid.uuid4().hex[:14]}"

    payment = Payment(
        ride_id=ride.id,
        stripe_payment_intent_id=txn_id,
        razorpay_payment_id=txn_id,
        razorpay_order_id=f"order_{uuid.uuid4().hex[:14]}",
        amount=amount,
        currency="INR",
        status="succeeded",
        payment_method=pay_data.payment_method,
        created_at=datetime.now(timezone.utc)
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    await ws_manager.broadcast_ride_update(ride.id, {
        "event": "PAYMENT_CONFIRMED",
        "type": "PAYMENT_CONFIRMED",
        "ride_id": ride.id,
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "payment_id": payment.id,
        "amount": payment.amount,
        "status": "succeeded"
    })
    await ws_manager.send_to_rider(ride.rider_id, "PAYMENT_CONFIRMED", {
        "ride_id": ride.id,
        "payment_id": payment.id,
        "amount": payment.amount,
        "status": "succeeded"
    })

    return payment

@router.post("/{ride_id}/review", response_model=ReviewResponse)
def submit_review(
    ride_id: int,
    rev_data: RideReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Submit rating (1-5) and feedback for the driver.
    """
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    existing_review = db.query(Review).filter(Review.ride_id == ride_id).first()
    if existing_review:
        existing_review.rating = rev_data.rating
        existing_review.comment = rev_data.comment
        db.commit()
        db.refresh(existing_review)
        return existing_review

    driver_user_id = ride.driver.user_id if (ride.driver and ride.driver.user_id) else 2

    review = Review(
        ride_id=ride.id,
        rater_id=ride.rider_id,
        rated_id=driver_user_id,
        rating=rev_data.rating,
        comment=rev_data.comment,
        created_at=datetime.now(timezone.utc)
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Recalculate driver rating average
    driver_user = db.query(User).filter(User.id == driver_user_id).first()
    if driver_user:
        all_revs = db.query(Review).filter(Review.rated_id == driver_user_id).all()
        if all_revs:
            driver_user.rating_avg = round(sum(r.rating for r in all_revs) / len(all_revs), 2)
            db.commit()

    return review

@router.get("/{ride_id}/receipt")
def get_ride_receipt(ride_id: int, db: Session = Depends(get_db)):
    """Generate detailed breakdown receipt for the ride."""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    total_fare = ride.fare_actual or ride.fare_estimate
    base_fare = 499.00 if ride.vehicle_type == "flying" else 99.00
    distance_charge = round(total_fare * 0.65, 2)
    skyway_surcharge = round(total_fare * 0.15, 2) if ride.vehicle_type == "flying" else 0.0
    taxes = round(total_fare * 0.05, 2)  # 5% GST for passenger transport in India
    subtotal = round(total_fare - taxes, 2)

    payment = db.query(Payment).filter(Payment.ride_id == ride_id).first()

    return {
        "receipt_number": f"BLR-SKY-{ride.id:06d}",
        "ride_id": ride.id,
        "date": ride.created_at.strftime("%b %d, %Y %I:%M %p IST"),
        "rider_name": ride.rider.name if ride.rider else "Passenger",
        "driver_name": ride.driver.user.name if ride.driver else "Aero Pilot",
        "vehicle": ride.driver.vehicle_info if ride.driver else "AeroCab VTOL",
        "pickup": ride.pickup_name,
        "dropoff": ride.drop_name,
        "distance_km": ride.distance_km,
        "duration_mins": ride.duration_mins,
        "vehicle_type": ride.vehicle_type,
        "currency": "INR",
        "breakdown": {
            "base_fare": base_fare,
            "distance_charge": distance_charge,
            "sky_corridor_surcharge": skyway_surcharge,
            "subtotal": subtotal,
            "taxes_and_fees": taxes,
            "total": total_fare
        },
        "payment": {
            "status": payment.status if payment else "pending",
            "method": payment.payment_method if payment else "Razorpay / UPI",
            "intent_id": payment.razorpay_payment_id or payment.stripe_payment_intent_id if payment else "N/A",
            "razorpay_order_id": payment.razorpay_order_id if payment else None,
            "razorpay_payment_id": payment.razorpay_payment_id if payment else None
        }
    }
