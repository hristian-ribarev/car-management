from datetime import date, timedelta
from database import Session
from dtos import CreateGarage, UpdateGarage, ResponseGarage, dailyAvailabilityReport
from model import Garage, Maintenance, car_garage
from sqlalchemy.orm import Session as ORMSession
from fastapi import HTTPException

def get_garage_by_id(id: int, session: ORMSession) -> Garage:
    garage = session.get(Garage, id)
    if garage is None:
        raise HTTPException(status_code=404, detail='Garage not found')
    return garage

def create_garage(request: CreateGarage) -> ResponseGarage:
    if any(char.isdigit() for char in request.name):
        raise HTTPException(status_code=400, detail="Name should not contain digits")
    if any(char.isdigit() for char in request.location):
        raise HTTPException(status_code=400, detail="Location should not contain digits")
    if any(char.isdigit() for char in request.city):
        raise HTTPException(status_code=400, detail="City should not contain digits")
    if not str(request.capacity).isdigit() or int(request.capacity) < 0:
        raise HTTPException(status_code=400, detail="Capacity should contain 0 or positive digits only")

    new_garage = map_request_to_garage(request)
    with Session() as session:
        session.add(new_garage)
        session.commit()
        session.refresh(new_garage)
        return map_garage_to_response(new_garage)

def get_garage(id: int) -> ResponseGarage:
    with Session() as session:
        garage = get_garage_by_id(id, session)
        return map_garage_to_response(garage)

def get_garages(city: str = None) -> list[ResponseGarage]:
    with Session() as session:
        query = session.query(Garage)
        if city:
            query = query.filter(Garage.city == city)
        garages = query.all()
        return [map_garage_to_response(garage) for garage in garages]

def update_garage(id: int, request: UpdateGarage) -> ResponseGarage:
    with Session() as session:
        garage = get_garage_by_id(id, session)
        if any(char.isdigit() for char in request.name):
            raise HTTPException(status_code=400, detail="Name should not contain digits")
        if any(char.isdigit() for char in request.location):
            raise HTTPException(status_code=400, detail="Location should not contain digits")
        if any(char.isdigit() for char in request.city):
            raise HTTPException(status_code=400, detail="City should not contain digits")
        if not str(request.capacity).isdigit() or int(request.capacity) < 0:
            raise HTTPException(status_code=400, detail="Capacity should contain 0 or positive digits only")

        garage.name = request.name
        garage.location = request.location
        garage.city = request.city
        garage.capacity = request.capacity
        session.commit()
        session.refresh(garage)
        return map_garage_to_response(garage)

def delete_garage(id: int) -> ResponseGarage:
    with Session() as session:
        garage = get_garage_by_id(id, session)
        session.delete(garage)
        session.commit()
        return map_garage_to_response(garage)

def map_garage_to_response(garage: Garage) -> ResponseGarage:
    return ResponseGarage(
        id=garage.id,
        name=garage.name,
        location=garage.location,
        city=garage.city,
        capacity=garage.capacity
    )

def map_request_to_garage(request: CreateGarage) -> Garage:
    return Garage(
        name=request.name,
        location=request.location,
        city=request.city,
        capacity=request.capacity
    )


def get_daily_availability_report(garageId: int, startDate: date, endDate: date) -> list[dailyAvailabilityReport]:
    with Session() as session:
        garage = get_garage_by_id(garageId, session)
        if not garage:
            raise HTTPException(status_code=404, detail='Garage not found')

        report = []
        current_date = startDate
        while current_date <= endDate:
            maintenances = session.query(Maintenance).filter(
                Maintenance.garageId == garageId,
                Maintenance.scheduledDate == current_date
            ).count()

            available_capacity = garage.capacity - maintenances
            report.append(dailyAvailabilityReport(
                date=current_date,
                requests=maintenances,
                availableCapacity=available_capacity
            ))
            current_date += timedelta(days=1)

        return report



def garage_capacity(garageId: int, session: Session) -> int:
    return session.query(car_garage).filter_by(garageId=garageId).count()
