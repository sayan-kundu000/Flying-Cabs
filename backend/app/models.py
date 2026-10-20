import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    role = Column(String(20), default="rider")  # rider, driver, admin
    profile_pic = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    rating_avg = Column(Float, default=4.9)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationships
    driver_profile = relationship("Driver", back_populates="user", uselist=False)
    rides_requested = relationship("Ride", foreign_keys="Ride.rider_id", back_populates="rider")
    reviews_given = relationship("Review", foreign_keys="Review.rater_id", back_populates="rater")

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    vehicle_info = Column(String(120), nullable=False)  # name of aero vehicle / car model
    vehicle_type = Column(String(30), default="flying")  # standard, flying, luxury, auto, bike, micro
    vehicle_image = Column(String(255), nullable=True)  # car photo / visual render
    license_plate = Column(String(30), default="AERO-77")
    verified = Column(Boolean, default=True)
    current_lat = Column(Float, nullable=False)
    current_lng = Column(Float, nullable=False)
    altitude_m = Column(Float, default=150.0)  # Flying Cab altitude in meters
    battery_pct = Column(Integer, default=94)
    status = Column(String(20), default="active")  # active (online/available), busy, offline
    total_trips = Column(Integer, default=142)
    earnings_today = Column(Float, default=184.50)

    # Relationships
    user = relationship("User", back_populates="driver_profile")
    rides = relationship("Ride", foreign_keys="Ride.driver_id", back_populates="driver")

class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    
    pickup_name = Column(String(200), nullable=False)
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)

    drop_name = Column(String(200), nullable=False)
    drop_lat = Column(Float, nullable=False)
    drop_lng = Column(Float, nullable=False)

    vehicle_type = Column(String(30), default="flying")
    car_model = Column(String(120), nullable=True)  # chosen car model
    # Status progression: REQUESTED -> ACCEPTED -> ARRIVED -> IN_PROGRESS -> COMPLETED, or CANCELLED
    status = Column(String(30), default="REQUESTED", index=True)

    # Ola & Uber 4-digit Ride Start OTP & Payment Mode
    otp = Column(String(10), default="4829")
    payment_mode = Column(String(50), default="razorpay")

    fare_estimate = Column(Float, nullable=False)
    fare_actual = Column(Float, nullable=True)
    distance_km = Column(Float, default=0.0)
    duration_mins = Column(Float, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    rider = relationship("User", foreign_keys=[rider_id], back_populates="rides_requested")
    driver = relationship("Driver", foreign_keys=[driver_id], back_populates="rides")
    payment = relationship("Payment", back_populates="ride", uselist=False)
    review = relationship("Review", back_populates="ride", uselist=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False, unique=True)
    stripe_payment_intent_id = Column(String(100), nullable=True)
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(30), default="succeeded")  # pending, succeeded, failed
    payment_method = Column(String(50), default="Razorpay (UPI / Card)")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationship
    ride = relationship("Ride", back_populates="payment")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False, unique=True)
    rater_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rated_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, default=5)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    # Relationships
    ride = relationship("Ride", back_populates="review")
    rater = relationship("User", foreign_keys=[rater_id], back_populates="reviews_given")
