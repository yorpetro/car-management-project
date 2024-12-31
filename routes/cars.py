from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi.params import Depends
from fastapi import APIRouter

from orm import Cars, CarGarageAssociations
from models import CarsIn, CarsOut
from routes.buisness_validators import CarValidators
from orm.db_session import get_db

car_router = APIRouter()


@car_router.get("/cars/{car_id}", response_model=CarsOut)
def get_car(car_id, db: Session = Depends(get_db)):
    return CarValidators.validate_car_id(car_id, db)


@car_router.get("/cars", response_model=List[CarsOut])
def get_all_cars(
        carMake: Optional[str] = None,
        garageId: Optional[int] = None,
        fromYear: Optional[int] = None,
        toYear: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Cars)

    if carMake:
        query = query.filter(Cars.make.ilike(f"%{carMake}%"))
    if garageId:
        query = query.join(CarGarageAssociations).filter(
            CarGarageAssociations.garage_id == garageId)
    if fromYear:
        query = query.filter(Cars.production_year >= fromYear)
    if toYear:
        query = query.filter(Cars.production_year <= toYear)

    return query.all()


@car_router.post("/cars", response_model=CarsOut)
def create_car(car: CarsIn, db: Session = Depends(get_db)):
    CarValidators.validate_license_plate(car.licensePlate, db)
    new_car = Cars(
        make=car.make,
        model=car.model,
        production_year=car.productionYear,
        license_plate=car.licensePlate,
    )
    print(car.garageIds)

    db.add(new_car)
    db.flush()
    new_car.garages = CarValidators.validate_and_associate_garages(car.garageIds, db)

    db.commit()
    db.refresh(new_car)

    return new_car


@car_router.put("/cars/{car_id}", response_model=CarsOut)
def update_car(car_id: int, car: CarsIn, db: Session = Depends(get_db)):
    existing_car: Cars | None = CarValidators.validate_car_id(car_id, db)

    CarValidators.validate_license_plate(car.licensePlate, db, car_id)

    existing_car.make = car.make
    existing_car.model = car.model
    existing_car.production_year = car.productionYear
    existing_car.license_plate = car.licensePlate

    existing_car.garages.clear()
    existing_car.garages = CarValidators.validate_and_associate_garages(
        car.garageIds, db
    )

    db.commit()
    db.refresh(existing_car)

    return existing_car


@car_router.delete("/cars/{car_id}")
def delete_car(car_id: int, db: Session = Depends(get_db)):
    existing_car: Cars | None = CarValidators.validate_car_id(car_id, db)
    db.delete(existing_car)
    return True
