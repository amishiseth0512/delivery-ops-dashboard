from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models import UserRole, OrderStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    model_config = {"from_attributes": True}


class OrderBase(BaseModel):
    description: str
    driver_id: Optional[int] = None


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: int
    status: OrderStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ReassignRequest(BaseModel):
    driver_id: int


class StatusUpdateRequest(BaseModel):
    status: OrderStatus


class AssistantRequest(BaseModel):
    question: str


class AssistantResponse(BaseModel):
    answer: str
    generated_at: datetime
