from fastapi import APIRouter, HTTPException, Query
from dtos import CreateCar, UpdateCar, ResponseCar
from car_service import create_car, get_car, get_cars, update_car, delete_car

car_router = APIRouter()

@car_router.get('/', response_model=list[ResponseCar])
def get_cars_by_make_garage_year(
        carMake: str = Query(None),
        garageId: int = Query(None),
        fromYear: int = Query(None),
        toYear: int = Query(None)
) -> list[ResponseCar]:
    return get_cars(carMake, garageId, fromYear, toYear)


@car_router.post('/', response_model=ResponseCar)
def create_single_car(request: CreateCar):
    try:
        return create_car(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e

@car_router.get('/{id}', response_model=ResponseCar)
def get_single_car(id: int):
    try:
        return get_car(id)
    except ValueError:
        raise HTTPException(status_code=404, detail='Car not found')

@car_router.put('/{id}', response_model=ResponseCar)
def update_single_car(id: int, request: UpdateCar):
    try:
        return update_car(id, request)
    except ValueError:
        raise HTTPException(status_code=404, detail='Car not found')

@car_router.delete('/{id}', response_model=dict)
def delete_single_car(id: int):
    try:
        deleted_car = delete_car(id)
        return {"message": f"Car {deleted_car.make} {deleted_car.model} deleted"}
    except ValueError:
        raise HTTPException(status_code=404, detail='Car not found')
