from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routes import ai, orders, users, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delivery Ops Dashboard",
    description="Backend API for managing delivery orders and drivers.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(ai.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Delivery Ops API is running"}
