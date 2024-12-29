from datetime import datetime, date
from typing import List
from sqlalchemy import func
from database import Session
from dtos import CreateMaintenance, UpdateMaintenance, ResponseMaintenance, monthlyRequestsReport, YearMonth
from garage_service import get_garage_by_id
from model import Maintenance, car_garage, Car, Garage
from sqlalchemy.orm import Session as ORMSession
from fastapi import HTTPException

def get_maintenance_by_id(id: int, session: ORMSession) -> Maintenance:
    maintenance = session.get(Maintenance, id)
    if maintenance is None:
        raise HTTPException(status_code=404, detail='Maintenance not found')
    return maintenance

def create_maintenance(request: CreateMaintenance) -> ResponseMaintenance:
    scheduled_date_str = str(request.scheduledDate)

    try:
        datetime.fromisoformat(scheduled_date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid scheduled date format")
    if not str(request.carId).isdigit():
        raise HTTPException(status_code=400, detail="Car ID should contain digits only")
    if not str(request.garageId).isdigit():
        raise HTTPException(status_code=400, detail="Garage ID should contain digits only")

    new_maintenance = map_request_to_maintenance(request)
    with Session() as session:
        session.add(new_maintenance)
        session.flush()

        insertDb = insert(car_garage).values(carId=request.carId, garageId=request.garageId)
        session.execute(insertDb)

        session.commit()
        session.refresh(new_maintenance)
        return map_maintenance_to_response(new_maintenance)

def get_maintenance(id: int) -> ResponseMaintenance:
    with Session() as session:
        maintenance = get_maintenance_by_id(id, session)
        return map_maintenance_to_response(maintenance)

def fetch_maintenances(carId: int = None, garageId: int = None, startDate: date = None, endDate: date = None) -> list[ResponseMaintenance]:
    with Session() as session:
        query = session.query(Maintenance)

        if carId is not None:
            query = query.filter(Maintenance.carId == carId)

        if garageId is not None:
            query = query.filter(Maintenance.garageId == garageId)

        if startDate is not None:
            query = query.filter(Maintenance.scheduledDate >= startDate)

        if endDate is not None:
            query = query.filter(Maintenance.scheduledDate <= endDate)

        maintenances = query.all()
        return [map_maintenance_to_response(maintenance) for maintenance in maintenances]

from sqlalchemy import delete, insert

def update_maintenance(id: int, request: UpdateMaintenance) -> ResponseMaintenance:
    with Session() as session:
        maintenance = get_maintenance_by_id(id, session)

        old_car = session.query(Car).filter(Car.id == maintenance.carId).first()
        old_garage = session.query(Garage).filter(Garage.id == maintenance.garageId).first()

        scheduled_date_str = str(request.scheduledDate)

        try:
            datetime.fromisoformat(scheduled_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled date format")
        if not str(request.carId).isdigit():
            raise HTTPException(status_code=400, detail="Car ID should contain digits only")
        if not str(request.garageId).isdigit():
            raise HTTPException(status_code=400, detail="Garage ID should contain digits only")

        maintenance.serviceType = request.serviceType
        maintenance.scheduledDate = request.scheduledDate
        maintenance.carId = request.carId
        maintenance.garageId = request.garageId

        deleteDb = delete(car_garage).where(
            car_garage.c.carId == old_car.id,
            car_garage.c.garageId == old_garage.id
        )
        session.execute(deleteDb)

        insertDb = insert(car_garage).values(carId=request.carId, garageId=request.garageId)
        session.execute(insertDb)

        session.commit()
        session.refresh(maintenance)

        new_car = session.query(Car).filter(Car.id == maintenance.carId).first()
        new_garage = session.query(Garage).filter(Garage.id == maintenance.garageId).first()

        return ResponseMaintenance(
            id=maintenance.id,
            carId=maintenance.carId,
            carName=f"{new_car.make} {new_car.model}" if new_car else None,
            serviceType=maintenance.serviceType,
            scheduledDate=maintenance.scheduledDate,
            garageId=maintenance.garageId,
            garageName=new_garage.name if new_garage else None
        )

def delete_maintenance(id: int) -> ResponseMaintenance:
    with Session() as session:
        maintenance = get_maintenance_by_id(id, session)

        car = session.query(Car).filter(Car.id == maintenance.carId).first()
        garage = session.query(Garage).filter(Garage.id == maintenance.garageId).first()

        deleteDb = delete(car_garage).where(
            car_garage.c.carId == maintenance.carId,
            car_garage.c.garageId == maintenance.garageId
        )
        session.execute(deleteDb)

        session.delete(maintenance)
        session.commit()

        return ResponseMaintenance(
            id=maintenance.id,
            carId=maintenance.carId,
            carName=f"{car.make} {car.model}" if car else None,
            serviceType=maintenance.serviceType,
            scheduledDate=maintenance.scheduledDate,
            garageId=maintenance.garageId,
            garageName=garage.name if garage else None
        )

def map_maintenance_to_response(maintenance: Maintenance) -> ResponseMaintenance:
    return ResponseMaintenance(
        id=maintenance.id,
        carId=maintenance.carId,
        carName=maintenance.car.make + ' ' + maintenance.car.model,
        serviceType=maintenance.serviceType,
        scheduledDate=maintenance.scheduledDate,
        garageId=maintenance.garageId,
        garageName=maintenance.garage.name
    )

def map_request_to_maintenance(request: CreateMaintenance) -> Maintenance:
    return Maintenance(
        serviceType=request.serviceType,
        scheduledDate=request.scheduledDate,
        carId=request.carId,
        garageId=request.garageId
    )


def get_monthly_requests_report(garageId: int, startDate: str, endDate: str) -> List[monthlyRequestsReport]:
    with Session() as session:
        garage = get_garage_by_id(garageId, session)
        if not garage:
            raise HTTPException(status_code=404, detail='Garage not found')

        report = []
        start_date = date.fromisoformat(startDate + '-01')
        end_date = date.fromisoformat(endDate + '-01')

        current_date = start_date

        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            if current_date.month == 12:
                month_end = current_date.replace(year=current_date.year + 1, month=1)
            else:
                month_end = current_date.replace(month=current_date.month + 1)

            requests = session.query(func.count(Maintenance.id)).filter(
                Maintenance.garageId == garageId,
                Maintenance.scheduledDate >= month_start,
                Maintenance.scheduledDate < month_end
            ).scalar()

            report.append(monthlyRequestsReport(
                yearMonth=YearMonth(year=current_date.year, monthValue=current_date.month),
                requests=requests
            ))

            current_date = month_end

        return report
