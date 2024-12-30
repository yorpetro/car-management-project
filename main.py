from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from models import CarsIn, CarsOut
from orm import Cars, get_db_session, Garages, CarGarageAssociations

app = FastAPI()

def get_db() -> Session:
    with get_db_session() as session:
        yield session

@app.get("/")
def root():
    return {
        "message": "Welcome to car-management-backend api, "
                   "Go to /docs to see the swagger documentation :)"
    }

@app.post("/cars", response_model=CarsOut)
def create_car(car: CarsIn, db: Session = Depends(get_db)):
    if db.query(Cars).filter_by(license_plate=car.license_plate).first():
        raise HTTPException(status_code=400, detail="License plate already exists.")

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