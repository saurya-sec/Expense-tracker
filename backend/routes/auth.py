import os

from fastapi import APIRouter, HTTPException
from supabase import create_client

from schema.auth import LoginRequest, SignupRequest


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


@router.post("/signup")
def signup(data: SignupRequest):

    response = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    return {
        "message": "Signup successful",
        "user": response.user
    }


@router.post("/login")
def login(data: LoginRequest):

    response = supabase.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "user": response.user
    }