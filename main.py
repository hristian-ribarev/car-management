from fastapi import FastAPI
from database import engine
from model import Base
from car_router import car_router
from garage_router import garage_router
from maintenance_router import maintenance_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(car_router, prefix="/cars", tags=["Cars"])
app.include_router(garage_router, prefix="/garages", tags=["Garages"])
app.include_router(maintenance_router, prefix="/maintenance", tags=["Maintenances"])


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
