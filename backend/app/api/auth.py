from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
import httpx

from app.db.session import get_db
from app.db.models import User
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

@router.post("/register")
async def register(
    email: str,
    password: str,
    username: str,
    full_name: str,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.execute(
        select(User).where((User.email == email) | (User.username == username))
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return {"message": "User created successfully", "user_id": new_user.id}

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }

@router.get("/google")
async def google_auth():
    return {
        "auth_url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri=http://localhost:8000/api/auth/google/callback&scope=openid%20profile%20email&access_type=offline"
    }

@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": "http://localhost:8000/api/auth/google/callback",
                    "grant_type": "authorization_code"
                }
            )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            user_info = user_info_response.json()
            
            result = await db.execute(
                select(User).where(User.email == user_info["email"])
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    email=user_info["email"],
                    username=user_info.get("email").split("@")[0],
                    full_name=user_info.get("name", ""),
                    is_active=True,
                    is_verified=user_info.get("email_verified", False)
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            
            jwt_token = create_access_token(
                data={"sub": user.username, "user_id": user.id}
            )
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name
                }
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )