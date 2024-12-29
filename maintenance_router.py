from datetime import date
from fastapi import APIRouter, HTTPException,Query
from typing import List
from dtos import CreateMaintenance, UpdateMaintenance, ResponseMaintenance, monthlyRequestsReport
from maintenance_service import create_maintenance, get_maintenance, fetch_maintenances, update_maintenance, delete_maintenance, get_monthly_requests_report

maintenance_router = APIRouter()

@maintenance_router.get('/monthlyRequestsReport', response_model=List[monthlyRequestsReport])
def get_maintenance_monthly_report(garageId: int = Query(...), startMonth: str = Query(..., regex=r'^\d{4}-\d{2}$'), endMonth: str = Query(..., regex=r'^\d{4}-\d{2}$')) -> List[monthlyRequestsReport]:
    try:
        return get_monthly_requests_report(garageId, startMonth, endMonth)
    except HTTPException as e:
        raise e
    except ValueError:
        raise HTTPException(status_code=404, detail='Garage not found')

@maintenance_router.get('/', response_model=list[ResponseMaintenance])
def get_maintenances(carId: int = None, garageId: int = None, startDate: date = Query(None), endDate: date = Query(None)) -> list[ResponseMaintenance]:
    return fetch_maintenances(carId, garageId, startDate, endDate)


@maintenance_router.post('/', response_model=ResponseMaintenance)
def create_single_maintenance(request: CreateMaintenance):
    try:
        return create_maintenance(request)
    except ValueError:
        raise HTTPException(status_code=404, detail='Maintenance not created')

@maintenance_router.get('/{id}', response_model=ResponseMaintenance)
def get_single_maintenance(id: int):
    try:
        return get_maintenance(id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Maintenance not found')

@maintenance_router.put('/{id}', response_model=ResponseMaintenance)
def update_single_maintenance(id: int, request: UpdateMaintenance):
    try:
        return update_maintenance(id, request)
    except ValueError:
        raise HTTPException(status_code=404, detail='Maintenance not found')

@maintenance_router.delete('/{id}', response_model=dict)
def delete_single_maintenance(id: int):
    try:
        deleted_maintenance = delete_maintenance(id)
        return {"message": f"Maintenance {deleted_maintenance.serviceType} deleted"}
    except ValueError:
        raise HTTPException(status_code=404, detail='Maintenance not found')


