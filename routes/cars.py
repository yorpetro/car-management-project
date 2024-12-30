from typing import List, Optional, Type

from sqlalchemy.orm import Session
from fastapi.params import Depends
from fastapi import APIRouter

from orm import get_db_session, Cars, CarGarageAssociations
from models import CarsIn, CarsOut
from routes.buisness_validators import CarValidators
car_router = APIRouter()


def get_db() -> Session:
    with get_db_session() as session:
        yield session


@car_router.get("/cars/{car_id}", response_model=CarsOut)
def get_car(car_id, db: Session = Depends(get_db)):
    return CarValidators().validate_car_id(car_id, db)

@car_router.get("/cars", response_model=List[CarsOut])
def get_all_cars(
        car_make: Optional[str] = None,
        garage_id: Optional[int] = None,
        from_year: Optional[int] = None,
        to_year: Optional[int] = None,
        db: Session = Depends(get_db)
):
    query = db.query(Cars)

    if car_make:
        query = query.filter(Cars.make.ilike(f"%{car_make}%"))
    if garage_id:
        query = query.join(CarGarageAssociations).filter(CarGarageAssociations.garage_id == garage_id)
    if from_year:
        query = query.filter(Cars.production_year >= from_year)
    if to_year:
        query = query.filter(Cars.production_year <= to_year)

    return query.all()

@car_router.post("/cars", response_model=CarsOut)
def create_car(car: CarsIn, db: Session = Depends(get_db)):
    CarValidators().validate_license_plate(car.license_plate, db)
    new_car = Cars(
        make=car.make,
        model=car.model,
        production_year=car.production_year,
        license_plate=car.license_plate,
    )

    db.add(new_car)
    db.flush()

    new_car.validate_and_associate_garages(car.garage_ids, db)

    db.commit()
    db.refresh(new_car)

    return new_car

@car_router.put("/cars/{car_id}", response_model=CarsOut)
def update_car(car_id: int, car: CarsIn, db: Session = Depends(get_db)):
    car_validator = CarValidators()
    existing_car: Cars | None = car_validator.validate_car_id(car_id, db)

    car_validator.validate_license_plate(car.license_plate, db, car_id)

    existing_car.make = car.make
    existing_car.model = car.model
    existing_car.production_year = car.production_year
    existing_car.license_plate = car.license_plate

    existing_car.garages.clear()
    existing_car.validate_and_associate_garages(car.garage_ids, db)

    db.commit()
    db.refresh(existing_car)

    return existing_car

@car_router.delete("/cars/{car_id}")
def delete_car(car_id, db: Session = Depends(get_db)):
    existing_car = CarValidators.validate_car_id(car_id, db)
    db.delete(existing_car)
    return True

