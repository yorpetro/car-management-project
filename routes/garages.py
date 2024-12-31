from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from fastapi.params import Depends
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from orm import Garages, Maintenances
from models import GaragesOut, GaragesIn
from orm.db_session import get_db
from routes.buisness_validators import GarageValidators

garage_router = APIRouter()


@garage_router.get("/garages/dailyAvailabilityReport")
def get_garages_report(
        garageId: int,
        startDate: str,
        endDate: str,
        db: Session = Depends(get_db)
):
    try:
        start_date_parsed = datetime.strptime(startDate, "%Y-%m-%d")
        end_date_parsed = datetime.strptime(endDate, "%Y-%m-%d")
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
        ) from e

    if start_date_parsed > end_date_parsed:
        raise HTTPException(
            status_code=400, detail="Start date cannot be after end date."
        )

    garage = db.query(Garages).filter(Garages.garage_id == garageId).first()
    if not garage:
        raise HTTPException(status_code=404, detail="Garage not found.")

    daily_capacity = garage.capacity

    maintenance_data = db.query(Maintenances).filter(
        Maintenances.garage_id == garageId,
        Maintenances.scheduled_date >= start_date_parsed,
        Maintenances.scheduled_date <= end_date_parsed
    ).all()

    requests_by_date = {}
    for maintenance in maintenance_data:
        maintenance_date = maintenance.scheduled_date
        requests_by_date[maintenance_date] = requests_by_date.get(maintenance_date,
                                                                  0) + 1

    response = []
    current_date = start_date_parsed
    while current_date <= end_date_parsed:
        request_count = requests_by_date.get(current_date.date(), 0)
        available_capacity = daily_capacity - request_count

        response.append({
            "date": str(current_date.date()),
            "requests": request_count,
            "availableCapacity": max(available_capacity, 0)
        })

        current_date += timedelta(days=1)

    return response


@garage_router.get("/garages/{garage_id}", response_model=GaragesOut)
def get_garage_by_id(garage_id, db: Session = Depends(get_db)):
    return GarageValidators.validate_garage_id(garage_id, db)


@garage_router.get("/garages", response_model=List[GaragesOut])
def get_all_garages(city: str = None, db: Session = Depends(get_db)):
    query = db.query(Garages)
    if city:
        query = query.filter(Garages.city.ilike(f"%{city}%"))
    return query.all()


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
