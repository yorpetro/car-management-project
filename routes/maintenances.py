from calendar import monthrange
from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.sql import extract, func
from fastapi.params import Depends
from fastapi.exceptions import HTTPException
from fastapi import APIRouter

from orm import Cars, Maintenances, Garages
from models import MaintenancesIn, MaintenancesOut, MonthsEnum, \
    MaintenanceRequestReport, MaintenanceYearMonth
from routes.buisness_validators import CarValidators, GarageValidators, \
    MaintenanceValidators
from orm.db_session import get_db

maintenances_router = APIRouter()


@maintenances_router.get("/maintenance/monthlyRequestsReport",
                         response_model=List[MaintenanceRequestReport])
def get_monthly_requests_report(garageId: int, startMonth: str, endMonth: str,
                                db: Session = Depends(get_db)):
    try:
        start_date = datetime.strptime(startMonth, "%Y-%m")
        end_date = datetime.strptime(endMonth, "%Y-%m")
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM."
        ) from e

    if start_date > end_date:
        raise HTTPException(status_code=400,
                            detail="Start month cannot be after end month.")

    month_range = []
    current_date = start_date
    while current_date <= end_date:
        month_range.append((current_date.year, current_date.month))
        days_in_month = monthrange(current_date.year, current_date.month)[1]
        current_date += timedelta(days=days_in_month)

    query = db.query(
        extract("year", Maintenances.scheduled_date).label("year"),
        extract("month", Maintenances.scheduled_date).label("month"),
        func.count(Maintenances.maintenance_id).label("request_count"),
    ).filter(
        Maintenances.scheduled_date >= start_date,
        Maintenances.scheduled_date <= end_date
    )

    query = query.filter(Maintenances.garage_id == garageId)

    query = query.group_by("year", "month").all()

    monthly_data = {(int(row.year), int(row.month)): row.request_count for row in query}

    response = []
    for year, month in month_range:
        month_enum = MonthsEnum(str(month).zfill(2)).name.upper()
        response.append(MaintenanceRequestReport(
            yearMonth=MaintenanceYearMonth(
                year=year,
                month=MonthsEnum[month_enum],
                leapYear=(year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)),
                monthValue=month
            ),
            requests=monthly_data.get((year, month), 0)
        ))

    return response


@maintenances_router.get("/maintenance/{maintenance_id}",
                         response_model=MaintenancesOut)
def get_maintenance_by_id(maintenance_id, db: Session = Depends(get_db)):
    maintenance = MaintenanceValidators.validate_maintenance_id(maintenance_id, db)
    car: Cars | None = CarValidators.validate_car_id(maintenance.car_id, db)
    garage: Garages | None = GarageValidators.validate_garage_id(
        maintenance.garage_id, db
    )

    car_name: str = f"{car.make} {car.model}"
    garage_name: str = str(garage.name)

    return {
        "id": maintenance.maintenance_id,
        "carId": maintenance.car_id,
        "carName": car_name,
        "serviceType": maintenance.service_type,
        "scheduledDate": maintenance.scheduled_date,
        "garageId": maintenance.garage_id,
        "garageName": garage_name,
    }


@maintenances_router.get("/maintenance", response_model=List[MaintenancesOut])
def get_all_maintenances(
        carId: Optional[int] = None,
        garageId: Optional[int] = None,
        startDate: Optional[str] = None,
        endDate: Optional[str] = None,
        db: Session = Depends(get_db)
):
    query = db.query(
        Maintenances.maintenance_id,
        Maintenances.scheduled_date,
        Maintenances.service_type,
        Maintenances.car_id.label("carId"),
        Cars.make.label("carMake"),
        Cars.model.label("carModel"),
        Maintenances.garage_id.label("garageId"),
        Garages.name.label("garageName"),
    ).join(Cars, Maintenances.car_id == Cars.car_id
           ).join(Garages, Maintenances.garage_id == Garages.garage_id)

    if carId:
        query = query.filter(Maintenances.car_id == carId)
    if garageId:
        query = query.filter(Maintenances.garage_id == garageId)
    if startDate:
        query = query.filter(Maintenances.scheduled_date >= startDate)
    if endDate:
        query = query.filter(Maintenances.scheduled_date <= endDate)

    # Ensure we only get records where both car_id and garage_id exist
    query = query.filter(Maintenances.car_id.isnot(None),
                         Maintenances.garage_id.isnot(None))
    results = query.all()

    return [
        {
            "maintenance_id": row.maintenance_id,
            "scheduled_date": row.scheduled_date,
            "service_type": row.service_type,
            "carId": row.carId,
            "carName": f"{row.carMake} {row.carModel}",
            "garageId": row.garageId,
            "garageName": row.garageName,
        }
        for row in results
    ]


@maintenances_router.post("/maintenance", response_model=MaintenancesOut)
def create_maintenances(maintenance: MaintenancesIn, db: Session = Depends(get_db)):
    car: Cars | None = CarValidators.validate_car_id(maintenance.carId, db)
    garage: Garages | None = GarageValidators.validate_garage_id(
        maintenance.garageId, db
    )

    car_name: str = f"{car.make} {car.model}"
    garage_name: str = str(garage.name)
    new_maintenance = Maintenances(
        service_type=maintenance.serviceType,
        scheduled_date=maintenance.scheduledDate,
        car_id=maintenance.carId,
        garage_id=maintenance.garageId
    )
    db.add(new_maintenance)
    db.flush()
    db.commit()

    return {
        "id": new_maintenance.maintenance_id,
        "carId": new_maintenance.car_id,
        "carName": car_name,
        "serviceType": new_maintenance.service_type,
        "scheduledDate": new_maintenance.scheduled_date,
        "garageId": new_maintenance.garage_id,
        "garageName": garage_name,
    }


@maintenances_router.put("/maintenance/{maintenance_id}",
                         response_model=MaintenancesOut)
def get_maintenance_by_id(maintenance: MaintenancesIn, maintenance_id,
                          db: Session = Depends(get_db)):
    existing = MaintenanceValidators.validate_maintenance_id(maintenance_id, db)

    car = CarValidators.validate_car_id(maintenance.carId, db)
    garage = GarageValidators.validate_garage_id(maintenance.garageId, db)

    existing.car_id = maintenance.carId
    existing.garage_id = maintenance.garageId
    existing.scheduled_date = maintenance.scheduledDate
    existing.service_type = maintenance.serviceType

    db.commit()
    db.refresh(existing)

    return {
        "id": existing.maintenance_id,
        "carId": existing.car_id,
        "carName": f"{car.make} {car.model}",
        "serviceType": existing.service_type,
        "scheduledDate": existing.scheduled_date,
        "garageId": existing.garage_id,
        "garageName": garage.name,
    }


@maintenances_router.delete("/maintenance/{maintenance_id}", response_model=bool)
def get_maintenance_by_id(maintenance_id, db: Session = Depends(get_db)):
    existing = MaintenanceValidators.validate_maintenance_id(maintenance_id, db)
    db.delete(existing)
    return True
