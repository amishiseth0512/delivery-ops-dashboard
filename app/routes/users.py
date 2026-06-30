from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/users", tags=["users"])

# bcrypt is intentionally slow, which makes brute-forcing hashed passwords expensive
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", response_model=List[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.post("/", response_model=schemas.UserResponse, status_code=201)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = models.User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=pwd_context.hash(user_in.password),
        role=user_in.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
