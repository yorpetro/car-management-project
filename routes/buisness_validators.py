from typing import Type

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from orm import Cars


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
    def validate_car_id(car_id: int, db: Session) -> Type[Cars] | None:
        """
        Validates if a car ID exists in the database.
        """
        if car := db.query(Cars).filter_by(car_id=car_id).first():
            return car
        else:
            raise HTTPException(status_code=404, detail="Car not found.")
