from pydantic import BaseModel, Field
from typing import List
from datetime import date

class UpdateMaintenance(BaseModel):
    carId: int
    serviceType: str = Field(..., min_length=2)
    scheduledDate: date
    garageId: int

class ResponseMaintenance(BaseModel):
    id: int
    carId: int
    carName: str = Field(..., min_length=2)
    serviceType: str = Field(..., min_length=2)
    scheduledDate: date
    garageId: int
    garageName: str = Field(..., min_length=2)

class UpdateGarage(BaseModel):
    name: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    capacity: int = Field(..., ge=1)
    city: str = Field(..., min_length=2)

class ResponseGarage(BaseModel):
    id: int
    name: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    capacity: int = Field(..., ge=1)

class UpdateCar(BaseModel):
    make: str = Field(..., min_length=2)
    model: str = Field(..., min_length=2)
    productionYear: int = Field(..., ge=1900)
    licensePlate: str = Field(..., min_length=2)
    garageIds: List[int] = []

class ResponseCar(BaseModel):
    id: int
    make: str = Field(..., min_length=2)
    model: str = Field(..., min_length=2)
    productionYear: int = Field(..., ge=1900)
    licensePlate: str = Field(..., min_length=2)
    garageIds: List[ResponseGarage] = []

class CreateMaintenance(BaseModel):
    garageId: int
    carId: int
    serviceType: str = Field(..., min_length=2)
    scheduledDate: date

class CreateGarage(BaseModel):
    name: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    capacity: int

class CreateCar(BaseModel):
    make: str = Field(..., min_length=2)
    model: str = Field(..., min_length=2)
    productionYear: int = Field(..., ge=1900)
    licensePlate: str = Field(..., min_length=2)
    garageIds: List[int] = []

class YearMonth(BaseModel):
    year: int = Field(..., ge=1900)
    monthValue: int = Field(..., ge=1, le=12)

class monthlyRequestsReport(BaseModel):
    yearMonth: YearMonth
    requests: int = Field(..., ge=0)

class dailyAvailabilityReport(BaseModel):
    date: date
    requests: int = Field(..., ge=0)
    availableCapacity: int = Field(..., ge=0)


