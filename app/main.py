from fastapi import FastAPI

from app.database import engine, Base
from app.routes import orders, users, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delivery Ops Dashboard",
    description="Backend API for managing delivery orders and drivers.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Delivery Ops API is running"}
