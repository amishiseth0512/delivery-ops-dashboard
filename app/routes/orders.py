from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@router.post("/", response_model=schemas.OrderResponse, status_code=201)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if order_in.driver_id is not None:
        driver = db.query(models.User).filter(models.User.id == order_in.driver_id).first()
        if driver is None:
            raise HTTPException(status_code=404, detail="Driver not found")
        if driver.role != models.UserRole.driver:
            raise HTTPException(status_code=400, detail="Assigned user is not a driver")

    new_order = models.Order(
        description=order_in.description,
        driver_id=order_in.driver_id,
        status=models.OrderStatus.placed,
    )
    db.add(new_order)
    db.flush()  # flush gives new_order an id before we commit, so we can use it below

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
