from datetime import date
from fastapi import APIRouter, HTTPException,Query
from typing import List
from dtos import CreateGarage, UpdateGarage, ResponseGarage, dailyAvailabilityReport
from garage_service import create_garage, get_garage, get_garages, update_garage, delete_garage, get_daily_availability_report

garage_router = APIRouter()

@garage_router.get('/dailyAvailabilityReport', response_model=List[dailyAvailabilityReport])
def get_garage_daily_availability(garageId: int = Query(...), startDate: date = Query(...), endDate: date = Query(...)) -> List[dailyAvailabilityReport]:
    try:
        return get_daily_availability_report(garageId, startDate, endDate)
    except ValueError:
        raise HTTPException(status_code=404, detail='Garage not found')

@garage_router.get('/', response_model=list[ResponseGarage])
def get_garages_by_city(city: str = Query(None)) -> list[ResponseGarage]:
    return get_garages(city)

@garage_router.post('/', response_model=ResponseGarage)
def create_single_garage(request: CreateGarage):
    try:
        return create_garage(request)
    except ValueError:
        raise HTTPException(status_code=404, detail='Garage not created')

@garage_router.get('/{id}', response_model=ResponseGarage)
def get_single_garage(id: int):
    try:
        return get_garage(id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Garage not found')

@garage_router.put('/{id}', response_model=ResponseGarage)
def update_single_garage(id: int, request: UpdateGarage):
    try:
        return update_garage(id, request)
    except ValueError:
        raise HTTPException(status_code=404, detail='Garage not found')

@garage_router.delete('/{id}', response_model=dict)
def delete_single_garage(id: int):
    try:
        deleted_garage = delete_garage(id)
        return {"message": f"Garage {deleted_garage.name} deleted"}
    except ValueError:
        raise HTTPException(status_code=404, detail='Garage not found')



