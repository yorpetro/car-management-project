from typing import Type

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session, Mapped

from orm import Cars, Garages, Maintenances


class CarValidators:
    @staticmethod
    def validate_license_plate(license_plate: str, db: Session, car_id: int = None):
        """
        Validates if a license plate is unique in the database.
        """
        query = db.query(Cars).filter(Cars.license_plate == license_plate)
        if car_id:
            query = query.filter(Cars.car_id != car_id)
        if query.first():
            raise HTTPException(status_code=400, detail="License plate already exists.")

    @staticmethod
    def validate_and_associate_garages(garage_ids: list[int], db: Session):
        """
        Validate and associate garage IDs with the car.
        """
        # Query the garages using their IDs
        garages = db.query(Garages).filter(Garages.garage_id.in_(garage_ids)).all()

        # Check if all garage IDs are valid
        if len(garages) != len(garage_ids):
            raise HTTPException(status_code=404,
                                detail="One or more garages not found.")

        return garages

    @staticmethod
    def validate_car_id(car_id: int | Mapped[int], db: Session) -> Type[Cars] | None:
        """
        Validates if a car ID exists in the database.
        """
        if car := db.query(Cars).filter_by(car_id=car_id).first():
            return car
        else:
            raise HTTPException(status_code=404, detail="Car not found.")

class GarageValidators:
    @staticmethod
    def validate_garage_id(garage_id: int | Mapped[int], db: Session) -> Type[Garages] | None:
        """
        Validates if a garage ID exists in the database.
        """
        if garage := db.query(Garages).filter_by(garage_id=garage_id).first():
            return garage
        else:
            raise HTTPException(status_code=404, detail="Garage not found.")

class MaintenanceValidators:
    @staticmethod
    def validate_maintenance_id(maintenance_id: int, db: Session)\
            -> Type[Maintenances] | None:
        """
        Validates if a maintenance ID exists in the database.
        """
        if maintenance := db.query(Maintenances).filter_by(maintenance_id=maintenance_id).first():
            return maintenance
        else:
            raise HTTPException(status_code=404, detail="Maintenance not found.")
