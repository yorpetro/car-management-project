from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from fastapi.params import Depends
from fastapi import APIRouter

from orm import get_db_session, Cars, CarGarageAssociations, Garages
from models import GaragesOut, GaragesIn
from routes.buisness_validators import GarageValidators

garage_router = APIRouter()


def get_db() -> Session:
    with get_db_session() as session:
        yield session


@garage_router.get("/garages/{garage_id}", response_model=GaragesOut)
def get_garage_by_id(garage_id, db: Session = Depends(get_db)):
    return GarageValidators.validate_garage_id(garage_id, db)


@garage_router.get("/garages", response_model=List[GaragesOut])
def get_all_garages(city: str = None, db: Session = Depends(get_db)):
    query = db.query(Garages)
    if city:
        query = query.filter(Garages.city.ilike(f"%{city}%"))
    return query.all()


@garage_router.get("garages/dailyAvailabilityReport")
def get_garages_report(
        garage_id: int,
        start_date: datetime,
        end_date: datetime,
        db: Session = Depends(get_db)
):
    pass


@garage_router.post("/garages", response_model=GaragesOut)
def create_garage(garage: GaragesIn, db: Session = Depends(get_db)):
    new_garage = Garages(
        name=garage.name,
        location=garage.location,
        city=garage.city,
        capacity=garage.capacity
    )
    db.add(new_garage)
    db.commit()
    return new_garage


@garage_router.put("/garages/{garage_id}", response_model=GaragesOut)
def update_garage(garage_id: int, garage: GaragesIn, db: Session = Depends(get_db)):
    existing_garage: Garages | None = GarageValidators.validate_garage_id(garage_id, db)

    existing_garage.name = garage.name
    existing_garage.location = garage.location
    existing_garage.city = garage.city
    existing_garage.capacity = garage.capacity

    db.commit()
    db.refresh(existing_garage)
    return existing_garage


@garage_router.delete("/garages/{garage_id}")
def delete_garage(garage_id: int, db: Session = Depends(get_db)):
    garage: Garages | None = GarageValidators.validate_garage_id(garage_id, db)
    db.delete(garage)
    return True
