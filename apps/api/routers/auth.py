import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from apps.api.database import get_db, DatabaseManager
from apps.api.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from apps.api.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: DatabaseManager = Depends(get_db)):
    users_col = db.get_collection("users")
    
    # Check if user already exists
    existing = await users_col.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )
    
    user_id = str(uuid.uuid4())
    now_str = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": payload.email.lower(),
        "name": payload.name,
        "password_hash": hash_password(payload.password),
        "role": "user",
        "created_at": now_str,
        "preferences": {
            "theme": "dark",
            "default_mode": "AUTO",
            "privacy_level": "standard"
        }
    }
    
    await users_col.insert_one(user_doc)
    
    access_token = create_access_token({
        "sub": user_id,
        "email": user_doc["email"],
        "role": user_doc["role"]
    })
    
    user_response = UserResponse(
        id=user_id,
        email=user_doc["email"],
        name=user_doc["name"],
        role=user_doc["role"],
        created_at=now_str,
        preferences=user_doc["preferences"]
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db: DatabaseManager = Depends(get_db)):
    users_col = db.get_collection("users")
    user = await users_col.find_one({"email": payload.email.lower()})
    
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "role": user.get("role", "user")
    })
    
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user.get("role", "user"),
        created_at=user.get("created_at", datetime.now(timezone.utc).isoformat()),
        preferences=user.get("preferences", {})
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user.get("role", "user"),
        created_at=current_user.get("created_at", ""),
        preferences=current_user.get("preferences", {})
    )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Successfully logged out"}
