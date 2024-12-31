from datetime import datetime
from enum import Enum
from typing import Type

from pydantic import BaseModel, Field


class GaragesIn(BaseModel):
    name: str
    location: str
    city: str
    capacity: int


class GaragesOut(BaseModel):
    garage_id: int = Field(alias="id")
    name: str
    location: str
    city: str
    capacity: int

    class Config:
        populate_by_name = True


class CarsIn(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garageIds: list


class CarsOut(BaseModel):
    car_id: int = Field(alias="id")
    make: str
    model: str
    production_year: int = Field(alias="productionYear")
    license_plate: str = Field(alias="licensePlate")
    garages: list[GaragesOut]

    class Config:
        populate_by_name = True


class MaintenancesIn(BaseModel):
    garageId: int
    carId: int
    serviceType: str
    scheduledDate: str


class MaintenancesOut(BaseModel):
    maintenance_id: int = Field(alias="id")
    car_id: int = Field(alias="carId")
    carName: str
    service_type: str = Field(alias="serviceType")
    scheduled_date: datetime = Field(alias="scheduledDate")
    garage_id: int = Field(alias="garageId")
    garageName: str

    class Config:
        populate_by_name = True


class MonthsEnum(Enum):
    JANUARY = "01"
    FEBRUARY = "02"
    MARCH = "03"
    APRIL = "04"
    MAY = "05"
    JUNE = "06"
    JULY = "07"
    AUGUST = "08"
    SEPTEMBER = "09"
    OCTOBER = "10"
    NOVEMBER = "11"
    DECEMBER = "12"

class MaintenanceYearMonth(BaseModel):
    year: int
    month: MonthsEnum
    leapYear: bool
    monthValue: int

class MaintenanceRequestReport(BaseModel):
    yearMonth: MaintenanceYearMonth
    requests: int