from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import pwd_context, create_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(form: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.email).first()
    if user is None or not pwd_context.verify(form.password, user.hashed_password):
        # same error for both cases so we don't leak whether the email exists
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_token(user.id, user.role.value)
    return {"access_token": token, "token_type": "bearer"}
