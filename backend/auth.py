import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")

JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {
            "id": user_id,
            "email": payload.get("email"),
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except jwt.InvalidTokenError as e:
        print("JWT verification error:", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    except Exception as e:
        print("Authentication error:", e)

        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )