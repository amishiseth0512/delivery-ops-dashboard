from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Order).all()


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@router.post("/", response_model=schemas.OrderResponse, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if order.driver_id is not None:
        driver = db.query(models.User).filter(models.User.id == order.driver_id).first()
        if driver is None:
            raise HTTPException(status_code=404, detail="Driver not found")
        if driver.role != models.UserRole.driver:
            raise HTTPException(status_code=400, detail="Assigned user is not a driver")

    new_order = models.Order(
        description=order.description,
        driver_id=order.driver_id,
        status=models.OrderStatus.placed,
    )
    db.add(new_order)
    db.flush()

    history = models.OrderStatusHistory(
        order_id=new_order.id,
        old_status=None,
        new_status=models.OrderStatus.placed,
        changed_by=current_user.id,
    )
    db.add(history)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
def update_status(order_id: int, body: schemas.StatusUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == models.UserRole.driver and order.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only update your own orders")

    old_status = order.status
    order.status = body.status

    history = models.OrderStatusHistory(
        order_id=order.id,
        old_status=old_status,
        new_status=body.status,
        changed_by=current_user.id,
    )
    db.add(history)
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/reassign", response_model=schemas.OrderResponse)
def reassign_order(order_id: int, body: schemas.ReassignRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != models.UserRole.dispatcher:
        raise HTTPException(status_code=403, detail="Only dispatchers can reassign orders")

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    driver = db.query(models.User).filter(models.User.id == body.driver_id).first()
    if driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    if driver.role != models.UserRole.driver:
        raise HTTPException(status_code=400, detail="User is not a driver")

    order.driver_id = body.driver_id
    db.commit()
    db.refresh(order)
    return order
