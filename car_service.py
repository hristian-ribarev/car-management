from database import Session
from dtos import CreateCar, ResponseCar, UpdateCar
from garage_service import map_garage_to_response, garage_capacity
from model import Car, Garage
from sqlalchemy.orm import Session as ORMSession
from fastapi import HTTPException

def get_car_by_id(id: int, session: ORMSession) -> Car:
    car = session.get(Car, id)
    if car is None:
        raise HTTPException(status_code=404, detail='Car not found')
    return car

def create_car(request: CreateCar) -> ResponseCar:
    if any(char.isdigit() for char in request.make):
        raise HTTPException(status_code=400, detail="Make should not contain digits")

    if not isinstance(request.productionYear, int):
        raise HTTPException(status_code=400, detail="Year should be an integer")

    new_car = map_request_to_car(request)
    with Session() as session:
        existing_car = session.query(Car).filter_by(licensePlate=request.licensePlate).first()
        if existing_car:
            raise HTTPException(status_code=400, detail=f"License plate {request.licensePlate} is already taken")

        session.add(new_car)
        session.commit()
        session.refresh(new_car)

        if request.garageIds:
            for garageId in request.garageIds:
                if not str(garageId).isdigit():
                    raise HTTPException(status_code=400, detail=f"Garage ID {garageId} should contain digits only")

                garage = session.get(Garage, garageId)
                if not garage:
                    raise HTTPException(status_code=404, detail=f"Garage with id {garageId} not found")

                current_capacity = garage_capacity(garageId, session)
                if current_capacity >= garage.capacity:
                    raise HTTPException(status_code=400, detail=f"Garage {garage.name} is full")

                new_car.garages.append(garage)

        session.commit()
        session.refresh(new_car)
        return map_car_to_response(new_car)

def get_car(id: int) -> ResponseCar:
    with Session() as session:
        car = get_car_by_id(id, session)
        return map_car_to_response(car)

def get_cars(carMake: str = None, garageId: int = None, fromYear: int = None, toYear: int = None) -> list[ResponseCar]:
    with Session() as session:
        query = session.query(Car)

        if carMake:
            query = query.filter(Car.make == carMake)

        if garageId:
            query = query.join(Car.garages).filter(Garage.id == garageId)

        if fromYear:
            query = query.filter(Car.productionYear >= fromYear)

        if toYear:
            query = query.filter(Car.productionYear <= toYear)

        cars = query.all()
        return [map_car_to_response(car) for car in cars]

def update_car(id: int, request: UpdateCar) -> ResponseCar:
    with Session() as session:
        car = get_car_by_id(id, session)

        if any(char.isdigit() for char in request.make):
            raise HTTPException(status_code=400, detail="Make should not contain digits")

        if not isinstance(request.productionYear, int):
            raise HTTPException(status_code=400, detail="Year should be an integer")

        existing_car = session.query(Car).filter_by(licensePlate=request.licensePlate).first()
        if existing_car and existing_car.id != id:
            raise HTTPException(status_code=400, detail=f"License plate {request.licensePlate} is already taken")

        car.make = request.make
        car.model = request.model
        car.productionYear = request.productionYear
        car.licensePlate = request.licensePlate

        car.garages.clear()

        if request.garageIds:
            for garageId in request.garageIds:
                if not str(garageId).isdigit():
                    raise HTTPException(status_code=400, detail=f"Garage ID {garageId} should contain digits only")

                garage = session.get(Garage, garageId)
                if not garage:
                    raise HTTPException(status_code=404, detail=f"Garage with id {garageId} not found")

                current_capacity = garage_capacity(garageId, session)
                if current_capacity >= garage.capacity:
                    raise HTTPException(status_code=400, detail=f"Garage {garage.name} is full")

                car.garages.append(garage)

        session.commit()
        session.refresh(car)
        return map_car_to_response(car)

def delete_car(id: int) -> ResponseCar:
    with Session() as session:
        car = get_car_by_id(id, session)
        session.delete(car)
        session.commit()
        return map_car_to_response(car)

def map_car_to_response(car: Car) -> ResponseCar:
    return ResponseCar(
        id=car.id,
        make=car.make,
        model=car.model,
        productionYear=car.productionYear,
        licensePlate=car.licensePlate,
        garages=[map_garage_to_response(garage) for garage in car.garages]
    )

def map_request_to_car(request: CreateCar) -> Car:
    return Car(
        make=request.make,
        model=request.model,
        productionYear=request.productionYear,
        licensePlate=request.licensePlate
    )
