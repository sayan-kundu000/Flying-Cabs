import hashlib
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import User, Driver
from backend.app.schemas import (
    UserResponse,
    UserRegisterRequest,
    UserLoginRequest,
    AuthSessionResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with project salt."""
    salt = "flying_cabs_india_bharat_2026"
    return hashlib.sha256(f"{salt}{password}".encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    if not hashed_password:
        return True  # Allow demo accounts without password
    return hash_password(plain_password) == hashed_password

# Default curated Indian face avatars
DEFAULT_FACES = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80",  # Priya / Rider
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&auto=format&fit=crop&q=80",  # Rajesh / Chauffeur
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80",  # Vikram / Pilot
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80",  # Ananya / Rider
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&auto=format&fit=crop&q=80",  # Harpreet / Pilot
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&auto=format&fit=crop&q=80",  # Sneha / Rider
    "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80",  # Sunil / Bike Rider
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&auto=format&fit=crop&q=80",  # Manjunath / Auto Pilot
]

@router.get("/avatars")
def get_curated_avatars():
    """Return curated Indian face avatar photos for rider and driver profile creation."""
    return [
        {"name": "Priya Sharma", "role": "rider", "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80"},
        {"name": "Capt. Vikram Rathore", "role": "pilot", "url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&auto=format&fit=crop&q=80"},
        {"name": "Rajesh Kumar", "role": "driver", "url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&auto=format&fit=crop&q=80"},
        {"name": "Capt. Priya Sen", "role": "driver", "url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=200&auto=format&fit=crop&q=80"},
        {"name": "Manjunath Gowda", "role": "driver", "url": "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?w=200&auto=format&fit=crop&q=80"},
        {"name": "Sunil Gowda", "role": "driver", "url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=200&auto=format&fit=crop&q=80"},
        {"name": "Ananya Roy", "role": "rider", "url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=200&auto=format&fit=crop&q=80"},
        {"name": "Deepak Rao", "role": "driver", "url": "https://images.unsplash.com/photo-1528892952291-009c663ce843?w=200&auto=format&fit=crop&q=80"},
    ]

@router.get("/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """List available demo users (Riders and Drivers) to easily test both roles."""
    return db.query(User).all()

@router.get("/session", response_model=UserResponse)
@router.post("/session", response_model=UserResponse)
def get_or_create_session(email: str = "aarav.sharma@aerocabs.in", db: Session = Depends(get_db)):
    """Verify or fetch active user session (simulates Clerk/Supabase auth verification)."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = db.query(User).filter(User.role == "rider").first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/register", response_model=AuthSessionResponse)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new rider or driver partner with face photo and vehicle choice."""
    clean_email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email address already exists. Please sign in.")

    # Assign default face avatar if none provided
    face_pic = req.profile_pic or (DEFAULT_FACES[0] if req.role == "rider" else DEFAULT_FACES[2])

    new_user = User(
        name=req.name.strip(),
        email=clean_email,
        phone=req.phone.strip() if req.phone else "+91 98765 00000",
        role=req.role if req.role in ["rider", "driver", "admin"] else "rider",
        profile_pic=face_pic,
        password_hash=hash_password(req.password),
        rating_avg=5.0,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # If registered as driver partner, also seed their driver profile
    if new_user.role == "driver":
        vehicle_img = req.vehicle_image or (
            "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=500&auto=format&fit=crop&q=80"
            if req.vehicle_type == "flying" else
            "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=500&auto=format&fit=crop&q=80"
        )
        new_driver = Driver(
            user_id=new_user.id,
            vehicle_info=req.vehicle_info or "Tata Tigor EV Prime",
            vehicle_type=req.vehicle_type or "standard",
            vehicle_image=vehicle_img,
            license_plate=req.license_plate or f"IND-{new_user.id:04d}",
            verified=True,
            current_lat=12.9716,
            current_lng=77.5946,
            altitude_m=150.0 if req.vehicle_type == "flying" else 0.0,
            battery_pct=96,
            status="active",
            earnings_today=0.0,
            total_trips=0
        )
        db.add(new_driver)
        db.commit()

    token = f"tok_fc_{uuid.uuid4().hex}"
    return AuthSessionResponse(
        user=new_user,
        token=token,
        message=f"Welcome to Flying Cabs, {new_user.name}!"
    )

@router.post("/login", response_model=AuthSessionResponse)
def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate existing user via Email or Phone."""
    ident = req.email_or_phone.strip().lower()
    user = db.query(User).filter(
        (User.email == ident) | (User.phone == ident)
    ).first()

    if not user:
        user = db.query(User).filter(User.phone.like(f"%{ident}%")).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or phone number. Please check credentials or register.")

    if req.password and user.password_hash:
        if not verify_password(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")

    token = f"tok_fc_{uuid.uuid4().hex}"
    return AuthSessionResponse(
        user=user,
        token=token,
        message=f"Welcome back, {user.name}!"
    )

@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Get active authenticated user by ID."""
    if user_id:
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            return u

    default_user = db.query(User).first()
    if not default_user:
        raise HTTPException(status_code=404, detail="No users found")
    return default_user

@router.post("/quick-switch/{user_id}", response_model=AuthSessionResponse)
def quick_switch_user(user_id: int, db: Session = Depends(get_db)):
    """1-click instant login/switching between demo rider and driver personas."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = f"tok_fc_{uuid.uuid4().hex}"
    return AuthSessionResponse(
        user=user,
        token=token,
        message=f"Switched persona to {user.name} ({user.role.upper()})"
    )
