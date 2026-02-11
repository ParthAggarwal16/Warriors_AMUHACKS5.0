from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database import get_db
from models import User
from schemas import Token, GoogleAuthRequest, UserResponse
from auth import create_access_token
from config import settings

router = APIRouter()

@router.post("/google", response_model=Token)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth token
    """
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            auth_request.token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        
        # Extract user information
        email = idinfo.get("email")
        google_id = idinfo.get("sub")
        full_name = idinfo.get("name")
        picture = idinfo.get("picture")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Create new user
            username = email.split("@")[0]
            
            # Ensure unique username
            counter = 1
            base_username = username
            while db.query(User).filter(User.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user = User(
                email=email,
                username=username,
                full_name=full_name,
                google_id=google_id,
                profile_picture=picture
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/verify-token")
async def verify_token_endpoint(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify if a JWT token is valid
    """
    from auth import verify_token
    
    try:
        token_data = verify_token(token)
        user = db.query(User).filter(User.id == token_data.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "valid": True,
            "user_id": user.id,
            "email": user.email
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )