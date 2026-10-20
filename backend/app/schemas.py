from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role: str = "rider"
    profile_pic: Optional[str] = None
    rating_avg: float = 4.9

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    password: str
    role: Optional[str] = "rider"
    profile_pic: Optional[str] = None
    # Optional driver fleet details if registering as pilot/driver
    vehicle_info: Optional[str] = "Tata Tigor EV Prime"
    vehicle_type: Optional[str] = "standard"
    vehicle_image: Optional[str] = None
    license_plate: Optional[str] = "DL-01-CAB-1234"

class UserLoginRequest(BaseModel):
    email_or_phone: str
    password: Optional[str] = None

class AuthSessionResponse(BaseModel):
    user: UserResponse
    token: str
    message: str

# Driver Schemas
class DriverBase(BaseModel):
    vehicle_info: str
    vehicle_type: str = "flying"
    vehicle_image: Optional[str] = None
    license_plate: str = "AERO-77"
    verified: bool = True
    current_lat: float
    current_lng: float
    altitude_m: float = 150.0
    battery_pct: int = 95
    status: str = "active"
    total_trips: int = 142
    earnings_today: float = 184.50

class DriverResponse(DriverBase):
    id: int
    user_id: int
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)

class DriverLocationUpdate(BaseModel):
    current_lat: float
    current_lng: float
    altitude_m: Optional[float] = None
    battery_pct: Optional[int] = None

class DriverStatusUpdate(BaseModel):
    status: str  # active, busy, offline

# Fare Estimate Schemas
class FareEstimateRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    origin_name: Optional[str] = "Pickup Location"
    dest_name: Optional[str] = "Destination"

class VehicleTierOption(BaseModel):
    tier_id: str
    name: str
    icon: str
    description: str
    fare: float
    duration_mins: int
    distance_km: float
    speed_factor: float
    capacity: int
    car_model: Optional[str] = None
    car_image: Optional[str] = None
    driver_name: Optional[str] = None
    driver_photo: Optional[str] = None
    driver_rating: Optional[float] = 4.95
    license_plate: Optional[str] = None
    eta_mins: Optional[int] = 3

class FareEstimateResponse(BaseModel):
    distance_km: float
    base_duration_mins: int
    options: List[VehicleTierOption]

# Ride Schemas
class RideCreate(BaseModel):
    rider_id: int
    pickup_name: str
    pickup_lat: float
    pickup_lng: float
    drop_name: str
    drop_lat: float
    drop_lng: float
    vehicle_type: str = "flying"
    car_model: Optional[str] = None
    preferred_driver_id: Optional[int] = None
    fare_estimate: float
    distance_km: float
    duration_mins: float
    otp: Optional[str] = None
    payment_mode: Optional[str] = "razorpay"

# API & Gateway Configuration Schemas
class ApiConfigResponse(BaseModel):
    google_maps_api_key: str
    google_maps_map_type: str
    razorpay_key_id: str
    razorpay_currency: str
    merchant_name: str

class ApiConfigUpdateRequest(BaseModel):
    google_maps_api_key: Optional[str] = None
    google_maps_map_type: Optional[str] = None
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None

# Payment Schemas (including Razorpay & UPI)
class PaymentResponse(BaseModel):
    id: int
    ride_id: int
    stripe_payment_intent_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    payment_method: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RazorpayConfigResponse(BaseModel):
    key_id: str
    currency: str
    name: str
    theme_color: str

class RazorpayOrderCreateRequest(BaseModel):
    amount: Optional[float] = None
    tip: Optional[float] = 0.0

class RazorpayOrderResponse(BaseModel):
    order_id: str
    amount: int  # in paise (e.g. 1499.00 -> 149900)
    currency: str
    key_id: str
    ride_id: int
    receipt: str
    is_live: Optional[bool] = False

class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: Optional[str] = None
    amount: Optional[float] = None
    payment_method: Optional[str] = "Razorpay (UPI / Card / NetBanking)"

class ReviewResponse(BaseModel):
    id: int
    ride_id: int
    rater_id: int
    rated_id: int
    rating: int
    comment: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RideResponse(BaseModel):
    id: int
    rider_id: int
    driver_id: Optional[int] = None
    pickup_name: str
    pickup_lat: float
    pickup_lng: float
    drop_name: str
    drop_lat: float
    drop_lng: float
    vehicle_type: str
    car_model: Optional[str] = None
    status: str
    otp: Optional[str] = "4829"
    payment_mode: Optional[str] = "razorpay"
    fare_estimate: float
    fare_actual: Optional[float] = None
    distance_km: float
    duration_mins: float
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    driver: Optional[DriverResponse] = None
    rider: Optional[UserResponse] = None
    payment: Optional[PaymentResponse] = None
    review: Optional[ReviewResponse] = None
    model_config = ConfigDict(from_attributes=True)

class RideStatusUpdate(BaseModel):
    status: str  # ACCEPTED, ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED
    driver_lat: Optional[float] = None
    driver_lng: Optional[float] = None
    entered_otp: Optional[str] = None

class RidePayRequest(BaseModel):
    payment_method: str = "UPI (Google Pay / PhonePe)"
    amount: Optional[float] = None

class RideReviewRequest(BaseModel):
    rating: int = Field(default=5, ge=1, le=5)
    comment: Optional[str] = "Smooth ride! Bypassed all city traffic."
