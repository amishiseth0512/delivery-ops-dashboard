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

    # needed so Pydantic can read SQLAlchemy model attributes, not just plain dicts
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


class StatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    old_status: Optional[OrderStatus]
    new_status: OrderStatus
    changed_by: int
    changed_at: datetime

    model_config = {"from_attributes": True}
