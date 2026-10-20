import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Flying Cabs — Ola & Uber Bharat Edition"
    PROJECT_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./flying_cabs.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-flying-cabs-key-2026-bharat")
    SIMULATION_AUTO_DRIVER: bool = True  # Auto-simulate driver matching and progression for single-user testing

    # Google Maps & Terrain API Configuration
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyA_DemoGoogleMapsKey_FlyingCabsIndia_2026")
    GOOGLE_MAPS_MAP_TYPE: str = os.getenv("GOOGLE_MAPS_MAP_TYPE", "terrain")

    # Razorpay Payment Gateway Configuration
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_1DP5mmOlF5G5ag")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "s9x4H8kL90QxPzM2mock2026")
    RAZORPAY_CURRENCY: str = "INR"
    MERCHANT_NAME: str = "Flying Cabs (Ola-Uber India)"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

