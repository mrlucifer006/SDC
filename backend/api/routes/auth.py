from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import timedelta

from backend.database import get_session
from backend.models import User, UserCreate, Token, UserRead
from backend.core.auth import get_password_hash, verify_password, create_access_token, get_current_user
from backend.core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.username == user_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    if not user_data.email.endswith("@kpriet.ac.in"):
        raise HTTPException(status_code=400, detail="Email must be a valid @kpriet.ac.in address")
        
    email_exists = session.query(User).filter(User.email == user_data.email).first()
    if email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        is_admin=user_data.is_admin
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account locked due to malpractice. Please contact an admin."
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": "admin" if user.is_admin else "user"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from backend.core.state import get_settings

@router.post("/malpractice")
def report_malpractice(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if not get_settings().get("malpractice_enabled", True):
        return {"status": "ignored", "detail": "Malpractice flags are disabled"}
    if user.is_admin:
        return {"status": "ok", "detail": "Admin cannot be locked."}
    user.is_locked = True
    session.commit()
    return {"status": "locked"}
