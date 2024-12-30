from pydantic import BaseModel


class CarsIn(BaseModel):
    make: str
    model: str
    production_year: int
    license_plate: str
    garage_ids: list[int]


class GarageOut(BaseModel):
    garage_id: int
    name: str
    location: str
    city: str
    capacity: int

    class Config:
        from_attributes = True


class CarsOut(BaseModel):
    car_id: int
    make: str
    model: str
    production_year: int
    license_plate: str
    garages: list[GarageOut]

    class Config:
        from_attributes = True
