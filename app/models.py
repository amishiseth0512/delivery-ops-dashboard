from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    dispatcher = "dispatcher"
    driver = "driver"


class OrderStatus(str, enum.Enum):
    placed = "Placed"
    in_transit = "In Transit"
    delivered = "Delivered"
    cancelled = "Cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    orders = relationship("Order", back_populates="driver", foreign_keys="Order.driver_id")
    history = relationship("OrderStatusHistory", back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.placed)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # order can be unassigned
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    driver = relationship("User", back_populates="orders", foreign_keys=[driver_id])
    status_history = relationship("OrderStatusHistory", back_populates="order")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    old_status = Column(Enum(OrderStatus), nullable=True)  # null on the very first entry
    new_status = Column(Enum(OrderStatus), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="status_history")
    user = relationship("User", back_populates="history")
